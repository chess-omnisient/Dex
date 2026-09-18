#!/usr/bin/env python3
"""
Dex ClickUp MCP Server

Provides ClickUp integration for task management, syncing, and workspace navigation.
Uses ClickUp API v2 with personal API token authentication.

Usage:
    python clickup_server.py
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Optional, List, Dict, Any

# Health system
try:
    sys.path.insert(0, str(os.path.join(os.path.dirname(__file__), '..', '..')))
    from core.utils.dex_logger import log_error as _log_health_error, mark_healthy as _mark_healthy
    _HAS_HEALTH = True
except ImportError:
    _HAS_HEALTH = False

# Timezone
try:
    from core.utils.timezone import now as _tz_now, today as _tz_today
except ImportError:
    def _tz_now():
        return datetime.now()
    def _tz_today():
        return date.today()

# MCP SDK
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
except ImportError:
    print("Error: MCP SDK not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
_vault_path = os.environ.get('VAULT_PATH')
BASE_DIR = Path(_vault_path) if _vault_path else Path.cwd()

# Load .env from vault root (gitignored, holds API tokens)
_env_file = BASE_DIR / '.env'
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, _, value = line.partition('=')
            os.environ.setdefault(key.strip(), value.strip())

CLICKUP_API_BASE = "https://api.clickup.com/api/v2"
CLICKUP_API_TOKEN = os.environ.get('CLICKUP_API_TOKEN', '')

# Cache for workspace/space IDs (avoids repeated API calls)
_cache: Dict[str, Any] = {}


# ─── API helpers ───────────────────────────────────────────────────────────────

def _headers() -> dict:
    return {"Authorization": CLICKUP_API_TOKEN, "Content-Type": "application/json"}


def _get(path: str, params: Optional[dict] = None) -> dict:
    """GET request to ClickUp API."""
    if not HAS_REQUESTS:
        return {"error": "requests library not installed. Run: pip install requests"}
    if not CLICKUP_API_TOKEN:
        return {"error": "CLICKUP_API_TOKEN not set"}
    resp = requests.get(f"{CLICKUP_API_BASE}{path}", headers=_headers(), params=params, timeout=15)
    if resp.status_code == 429:
        return {"error": "Rate limited by ClickUp. Wait a moment and retry."}
    if resp.status_code != 200:
        return {"error": f"ClickUp API {resp.status_code}: {resp.text[:300]}"}
    return resp.json()


def _post(path: str, body: dict) -> dict:
    """POST request to ClickUp API."""
    if not HAS_REQUESTS:
        return {"error": "requests library not installed"}
    if not CLICKUP_API_TOKEN:
        return {"error": "CLICKUP_API_TOKEN not set"}
    resp = requests.post(f"{CLICKUP_API_BASE}{path}", headers=_headers(), json=body, timeout=15)
    if resp.status_code == 429:
        return {"error": "Rate limited by ClickUp. Wait a moment and retry."}
    if resp.status_code not in (200, 201):
        return {"error": f"ClickUp API {resp.status_code}: {resp.text[:300]}"}
    return resp.json()


def _put(path: str, body: dict) -> dict:
    """PUT request to ClickUp API."""
    if not HAS_REQUESTS:
        return {"error": "requests library not installed"}
    if not CLICKUP_API_TOKEN:
        return {"error": "CLICKUP_API_TOKEN not set"}
    resp = requests.put(f"{CLICKUP_API_BASE}{path}", headers=_headers(), json=body, timeout=15)
    if resp.status_code == 429:
        return {"error": "Rate limited by ClickUp. Wait a moment and retry."}
    if resp.status_code != 200:
        return {"error": f"ClickUp API {resp.status_code}: {resp.text[:300]}"}
    return resp.json()


# ─── Data helpers ──────────────────────────────────────────────────────────────

def _get_team_id() -> Optional[str]:
    """Get the first (usually only) workspace/team ID, with caching."""
    if 'team_id' in _cache:
        return _cache['team_id']
    data = _get("/team")
    if "error" in data:
        return None
    teams = data.get("teams", [])
    if not teams:
        return None
    _cache['team_id'] = teams[0]["id"]
    return _cache['team_id']


def _format_task(task: dict, verbose: bool = False) -> dict:
    """Format a ClickUp task into a clean summary."""
    result = {
        "id": task.get("id"),
        "name": task.get("name"),
        "status": task.get("status", {}).get("status", "unknown"),
        "priority": (task.get("priority") or {}).get("priority", "none"),
        "url": task.get("url"),
    }
    assignees = task.get("assignees", [])
    if assignees:
        result["assignees"] = [a.get("username") or a.get("email", "") for a in assignees]
    due = task.get("due_date")
    if due:
        result["due_date"] = datetime.fromtimestamp(int(due) / 1000).strftime("%Y-%m-%d")
    tags = task.get("tags", [])
    if tags:
        result["tags"] = [t.get("name") for t in tags]
    if verbose:
        result["description"] = (task.get("text_content") or "")[:500]
        result["list"] = task.get("list", {}).get("name")
        result["folder"] = task.get("folder", {}).get("name")
        result["space"] = task.get("space", {}).get("id")
        result["date_created"] = datetime.fromtimestamp(int(task["date_created"]) / 1000).strftime("%Y-%m-%d") if task.get("date_created") else None
        result["date_updated"] = datetime.fromtimestamp(int(task["date_updated"]) / 1000).strftime("%Y-%m-%d") if task.get("date_updated") else None
    return result


# ─── MCP Server ────────────────────────────────────────────────────────────────

server = Server("dex-clickup")


@server.list_tools()
async def list_tools():
    """List available ClickUp tools."""
    return [
        Tool(
            name="clickup_get_workspaces",
            description="List ClickUp workspaces (teams) the user has access to.",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="clickup_get_spaces",
            description="List spaces in a ClickUp workspace.",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {"type": "string", "description": "Workspace/team ID. Omit to use default workspace."}
                },
                "required": []
            }
        ),
        Tool(
            name="clickup_get_lists",
            description="List all lists in a space (including folderless lists).",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {"type": "string", "description": "Space ID to list from."}
                },
                "required": ["space_id"]
            }
        ),
        Tool(
            name="clickup_get_tasks",
            description="Get tasks from a ClickUp list with optional filtering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {"type": "string", "description": "List ID to get tasks from."},
                    "statuses": {"type": "array", "items": {"type": "string"}, "description": "Filter by status names (e.g., ['open', 'in progress'])."},
                    "include_closed": {"type": "boolean", "description": "Include closed/done tasks.", "default": False},
                    "page": {"type": "integer", "description": "Page number (0-indexed, 100 per page).", "default": 0}
                },
                "required": ["list_id"]
            }
        ),
        Tool(
            name="clickup_get_task",
            description="Get detailed info for a single ClickUp task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "ClickUp task ID."}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="clickup_search_tasks",
            description="Search tasks across the entire workspace by name, status, assignee, or tags.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (matched against task names client-side)."},
                    "statuses": {"type": "array", "items": {"type": "string"}, "description": "Filter by status names."},
                    "assignees": {"type": "array", "items": {"type": "integer"}, "description": "Filter by assignee user IDs."},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tag names."},
                    "include_closed": {"type": "boolean", "default": False},
                    "page": {"type": "integer", "default": 0}
                },
                "required": []
            }
        ),
        Tool(
            name="clickup_create_task",
            description="Create a new task in a ClickUp list.",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {"type": "string", "description": "List ID to create the task in."},
                    "name": {"type": "string", "description": "Task name/title."},
                    "description": {"type": "string", "description": "Task description (markdown supported)."},
                    "status": {"type": "string", "description": "Status name (e.g., 'open', 'in progress')."},
                    "priority": {"type": "integer", "description": "Priority: 1=urgent, 2=high, 3=normal, 4=low."},
                    "due_date": {"type": "string", "description": "Due date as YYYY-MM-DD."},
                    "assignees": {"type": "array", "items": {"type": "integer"}, "description": "User IDs to assign."},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tag names to add."}
                },
                "required": ["list_id", "name"]
            }
        ),
        Tool(
            name="clickup_update_task",
            description="Update an existing ClickUp task (status, name, priority, due date, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "ClickUp task ID to update."},
                    "name": {"type": "string", "description": "New task name."},
                    "description": {"type": "string", "description": "New description."},
                    "status": {"type": "string", "description": "New status name."},
                    "priority": {"type": "integer", "description": "New priority (1-4)."},
                    "due_date": {"type": "string", "description": "New due date as YYYY-MM-DD."},
                    "assignees_add": {"type": "array", "items": {"type": "integer"}, "description": "User IDs to add."},
                    "assignees_remove": {"type": "array", "items": {"type": "integer"}, "description": "User IDs to remove."}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="clickup_get_comments",
            description="Get comments on a ClickUp task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "ClickUp task ID."}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="clickup_add_comment",
            description="Add a comment to a ClickUp task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "ClickUp task ID."},
                    "comment_text": {"type": "string", "description": "Comment body (plain text)."}
                },
                "required": ["task_id", "comment_text"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls with error wrapping."""
    try:
        return await _call_tool_inner(name, arguments or {})
    except Exception as e:
        if _HAS_HEALTH:
            _log_health_error(
                source="dex-clickup",
                message=str(e),
                human_message=f"ClickUp tool '{name}' failed",
                context={"tool": name}
            )
        raise


def _json_response(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, indent=2, default=str))]


async def _call_tool_inner(name: str, args: dict) -> list[TextContent]:

    # ── Workspaces ──
    if name == "clickup_get_workspaces":
        data = _get("/team")
        if "error" in data:
            return _json_response(data)
        teams = [{"id": t["id"], "name": t["name"], "members": len(t.get("members", []))} for t in data.get("teams", [])]
        return _json_response({"workspaces": teams})

    # ── Spaces ──
    elif name == "clickup_get_spaces":
        team_id = args.get("team_id") or _get_team_id()
        if not team_id:
            return _json_response({"error": "No workspace found. Check your API token."})
        data = _get(f"/team/{team_id}/space", params={"archived": "false"})
        if "error" in data:
            return _json_response(data)
        spaces = [{"id": s["id"], "name": s["name"], "private": s.get("private", False)} for s in data.get("spaces", [])]
        return _json_response({"spaces": spaces})

    # ── Lists ──
    elif name == "clickup_get_lists":
        space_id = args["space_id"]
        all_lists = []
        # Foldered lists
        folders_data = _get(f"/space/{space_id}/folder", params={"archived": "false"})
        if "error" not in folders_data:
            for folder in folders_data.get("folders", []):
                for lst in folder.get("lists", []):
                    all_lists.append({"id": lst["id"], "name": lst["name"], "folder": folder["name"], "task_count": lst.get("task_count")})
        # Folderless lists
        folderless = _get(f"/space/{space_id}/list", params={"archived": "false"})
        if "error" not in folderless:
            for lst in folderless.get("lists", []):
                all_lists.append({"id": lst["id"], "name": lst["name"], "folder": None, "task_count": lst.get("task_count")})
        return _json_response({"lists": all_lists})

    # ── Get tasks from list ──
    elif name == "clickup_get_tasks":
        list_id = args["list_id"]
        params = {"page": str(args.get("page", 0)), "include_closed": str(args.get("include_closed", False)).lower()}
        statuses = args.get("statuses")
        if statuses:
            for s in statuses:
                params[f"statuses[]"] = s
        data = _get(f"/list/{list_id}/task", params=params)
        if "error" in data:
            return _json_response(data)
        tasks = [_format_task(t) for t in data.get("tasks", [])]
        return _json_response({"tasks": tasks, "count": len(tasks)})

    # ── Get single task ──
    elif name == "clickup_get_task":
        data = _get(f"/task/{args['task_id']}")
        if "error" in data:
            return _json_response(data)
        return _json_response(_format_task(data, verbose=True))

    # ── Search tasks (workspace-wide) ──
    elif name == "clickup_search_tasks":
        team_id = _get_team_id()
        if not team_id:
            return _json_response({"error": "No workspace found."})
        params: Dict[str, Any] = {"page": str(args.get("page", 0)), "include_closed": str(args.get("include_closed", False)).lower()}
        for s in args.get("statuses", []):
            params["statuses[]"] = s
        for a in args.get("assignees", []):
            params["assignees[]"] = str(a)
        for t in args.get("tags", []):
            params["tags[]"] = t
        data = _get(f"/team/{team_id}/task", params=params)
        if "error" in data:
            return _json_response(data)
        tasks = [_format_task(t) for t in data.get("tasks", [])]
        # Client-side name filter if query provided
        query = args.get("query", "").lower().strip()
        if query:
            tasks = [t for t in tasks if query in t["name"].lower()]
        return _json_response({"tasks": tasks, "count": len(tasks), "query": query or None})

    # ── Create task ──
    elif name == "clickup_create_task":
        body: Dict[str, Any] = {"name": args["name"]}
        if args.get("description"):
            body["markdown_description"] = args["description"]
        if args.get("status"):
            body["status"] = args["status"]
        if args.get("priority"):
            body["priority"] = args["priority"]
        if args.get("due_date"):
            try:
                dt = datetime.strptime(args["due_date"], "%Y-%m-%d")
                body["due_date"] = int(dt.timestamp() * 1000)
            except ValueError:
                return _json_response({"error": f"Invalid due_date format: {args['due_date']}. Use YYYY-MM-DD."})
        if args.get("assignees"):
            body["assignees"] = args["assignees"]
        if args.get("tags"):
            body["tags"] = args["tags"]
        data = _post(f"/list/{args['list_id']}/task", body)
        if "error" in data:
            return _json_response(data)
        return _json_response({"created": True, "task": _format_task(data, verbose=True)})

    # ── Update task ──
    elif name == "clickup_update_task":
        body: Dict[str, Any] = {}
        if args.get("name"):
            body["name"] = args["name"]
        if args.get("description"):
            body["markdown_description"] = args["description"]
        if args.get("status"):
            body["status"] = args["status"]
        if args.get("priority"):
            body["priority"] = args["priority"]
        if args.get("due_date"):
            try:
                dt = datetime.strptime(args["due_date"], "%Y-%m-%d")
                body["due_date"] = int(dt.timestamp() * 1000)
            except ValueError:
                return _json_response({"error": f"Invalid due_date format. Use YYYY-MM-DD."})
        if args.get("assignees_add") or args.get("assignees_remove"):
            body["assignees"] = {"add": args.get("assignees_add", []), "rem": args.get("assignees_remove", [])}
        if not body:
            return _json_response({"error": "No fields to update. Provide at least one field."})
        data = _put(f"/task/{args['task_id']}", body)
        if "error" in data:
            return _json_response(data)
        return _json_response({"updated": True, "task": _format_task(data, verbose=True)})

    # ── Get comments ──
    elif name == "clickup_get_comments":
        data = _get(f"/task/{args['task_id']}/comment")
        if "error" in data:
            return _json_response(data)
        comments = []
        for c in data.get("comments", []):
            comments.append({
                "id": c.get("id"),
                "text": c.get("comment_text", ""),
                "user": c.get("user", {}).get("username"),
                "date": datetime.fromtimestamp(int(c["date"]) / 1000).strftime("%Y-%m-%d %H:%M") if c.get("date") else None
            })
        return _json_response({"comments": comments, "count": len(comments)})

    # ── Add comment ──
    elif name == "clickup_add_comment":
        body = {"comment_text": args["comment_text"]}
        data = _post(f"/task/{args['task_id']}/comment", body)
        if "error" in data:
            return _json_response(data)
        return _json_response({"added": True, "comment_id": data.get("id")})

    else:
        return _json_response({"error": f"Unknown tool: {name}"})


# ─── Entry point ───────────────────────────────────────────────────────────────

async def main():
    """Run the MCP server."""
    if _HAS_HEALTH:
        _mark_healthy("dex-clickup")
    logger.info("Starting Dex ClickUp MCP Server")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
