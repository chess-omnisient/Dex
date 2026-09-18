---
name: shape
description: Create Shape Up breadboard diagrams and fat marker sketches using Mermaid — from scratch or from existing PRDs
---

# Shape — Visual Solution Shaping

Create **breadboard diagrams** (abstract user flow) and **fat marker sketches** (rough screen layouts) using Mermaid, following Shape Up methodology.

## Usage

```
/shape                          # Interactive — asks what you're shaping
/shape [idea description]       # Start shaping a new concept
/shape from PRD                 # Generate diagrams from an existing PRD
/shape [project name]           # Auto-detect PRD in project folder
```

Also invocable inline during `/product-brief` Phase 4 (Solution Shaping).

---

## Context Loading (Silent)

On invocation, silently read:
1. `System/user-profile.yaml` — company context
2. `System/pillars.yaml` — strategic pillars (for alignment)
3. `.claude/skills/shape/references/shape-up-principles.md` — methodology reference
4. `.claude/skills/shape/references/breadboard-patterns.md` — Mermaid breadboard patterns
5. `.claude/skills/shape/references/fat-marker-patterns.md` — Mermaid fat marker patterns
6. If Mode B: The target PRD file from `04-Projects/`

Do NOT mention that you're loading these files. Just use the knowledge naturally.

---

## Mode Detection

Determine the mode based on invocation:

| Input | Mode |
|-------|------|
| `/shape` (no args) | Ask: "What are you shaping? A new idea, or should I work from an existing PRD?" |
| `/shape [text that's an idea]` | **Mode A** — shape from scratch |
| `/shape from PRD` | **Mode B** — prompt for which project |
| `/shape [project name]` | **Mode B** — find PRD in `04-Projects/[project]/` |
| Called inline from `/product-brief` | **Mode C** — use conversation context from Phase 4 |

---

## Mode A: Shape from Scratch

### Phase 1: Capture

Accept the idea. Then ask:

> "What type of diagram do you need?"
> 1. **Breadboard** — map the user flow (places, actions, connections)
> 2. **Fat marker sketch** — rough layout of a specific screen
> 3. **Both** — breadboard first, then sketch key screens

If the user is unsure, default to **breadboard first** — it's the natural starting point.

### Phase 2: Identify Places

Ask: **"What are the key places in this flow?"** Places are screens, pages, dialogs, or distinct states the user visits.

**Challenge assumptions:**
- "Is [place] truly a separate screen, or is it a state within [other place]?"
- "What's the entry point? How does the user get here?"
- "Is there an admin/settings view we're missing?"

Synthesize and confirm the places list before moving on.

### Phase 3: Map Affordances & Connections

For each Place, ask:
- **"What can the user do here?"** — buttons, fields, links, dropdowns, toggles
- **"Where does each action take them?"** — which Place does it lead to?

**Challenge for completeness:**
- "What happens if validation fails here?"
- "Can the user go back from this point?"
- "What if the user has no data yet — is there an empty state?"
- "Are there any background/async steps (processing, notifications)?"

Build the connection map and confirm with the user.

### Phase 4: Generate Breadboard

Generate the Mermaid breadboard diagram following the patterns in `references/breadboard-patterns.md`.

**Choosing the right pattern:**
- 3-5 places → Simple breadboard (stadium nodes)
- 6-10 places → Detailed breadboard (subgraphs with affordances)
- 10+ places → Split into sub-flows and generate multiple diagrams

Display the diagram and ask: **"Does this capture the flow? Anything missing or wrong?"**

Iterate until the user is satisfied. Accept commands like `add place`, `add connection`, `remove [element]`, `simplify`, `expand`.

### Phase 5: Fat Marker Sketch (if requested)

For each key Place identified in the breadboard, ask:
- **"What elements appear on this screen?"** (charts, tables, buttons, forms)
- **"How are they roughly arranged?"** (top-to-bottom, side-by-side panels, tabs)

Generate the Mermaid fat marker sketch following `references/fat-marker-patterns.md`.

**Key principle:** If it looks too detailed, you've gone too far. Fat marker = zones and element types, not exact layout.

Display and iterate.

### Phase 6: Save & Integrate

Ask where to save:
- **Existing project:** Save to `04-Projects/[Project]/Shape_Breadboard.md` and/or `Shape_FatMarker.md`
- **New project idea:** Save to `00-Inbox/Ideas/Shape_[Name]_YYYY-MM-DD.md` (both diagrams in one file)

**Offer next steps:**
- "Want to create a PRD from this? I can run `/product-brief` with this shape as input."
- "Should I link this to an existing project?"
- "Want to create tasks from the places/flows identified?"

---

## Mode B: Shape from PRD

### Phase 1: Load PRD

Find the PRD:
1. Search `04-Projects/` for the project folder
2. Look for `PRD.md`, `PRD_*.md`, or any file with "PRD" in the name
3. If multiple found, ask the user which one

Read the PRD, focusing on:
- Solution section (core concept, key elements, user flow)
- Dashboard or screen descriptions
- Phase/milestone breakdowns
- Any flow descriptions in appendices

### Phase 2: Extract Flow Elements

Parse the PRD's user flow into Shape Up elements:

**Extract:**
- **Places** from flow steps (each numbered step often maps to a Place)
- **Affordances** from described user actions
- **Connections** from the step sequence and conditional paths

Present the extraction:

> "I extracted these from your PRD:
> - **Places:** [list]
> - **Key affordances:** [list]
> - **Branches/conditions:** [list]
>
> Does this look right, or should I adjust?"

Allow corrections before generating.

### Phase 3: Generate Breadboard

Generate the Mermaid breadboard from the extracted elements. Follow the same patterns and iteration as Mode A Phase 4.

### Phase 4: Generate Fat Marker Sketches

For screens described in detail in the PRD (dashboards, configuration pages, data views), generate fat marker sketches.

**Auto-detect sketch candidates:** Any PRD section that describes specific UI elements, chart types, filtering mechanisms, or layout zones is a candidate.

Display each sketch and iterate.

### Phase 5: Save

Save alongside the PRD in the project folder:
- `04-Projects/[Project]/Shape_Breadboard.md`
- `04-Projects/[Project]/Shape_FatMarker.md`

Offer to add a reference link in the PRD's Solution section pointing to the shape files.

---

## Mode C: Inline from /product-brief

When invoked during `/product-brief` Phase 4:

1. Use the solution description and user flow from the ongoing conversation (don't re-ask questions)
2. Extract Places, Affordances, and Connections from what was just discussed
3. Generate the breadboard inline
4. If screen layouts were described, generate fat marker sketches
5. Store the diagrams for inclusion in the PRD when Phase 8 generates the document
6. Return control to `/product-brief` Phase 5

**Key:** Don't save to separate files in Mode C — the diagrams become part of the PRD output.

---

## Diagram Output Format

All diagrams are wrapped in a markdown document with context:

```markdown
# Shape: [Idea/Project Name]

**Date:** YYYY-MM-DD
**Mode:** From scratch / From PRD
**Related PRD:** [link if applicable]

## Breadboard

[Description of what this flow covers]

\`\`\`mermaid
%%{init: {'theme': 'neutral'}}%%
[diagram content]
\`\`\`

### Flow Notes
- [Any important decisions or assumptions]
- [Error paths explained]
- [Phase annotations explained]

## Fat Marker Sketches

### [Screen Name 1]

[What this screen does]

\`\`\`mermaid
%%{init: {'theme': 'neutral'}}%%
[diagram content]
\`\`\`

### [Screen Name 2]
...
```

---

## Navigation Commands

Available at any phase:

| Command | Action |
|---------|--------|
| `back` / `previous` | Return to previous phase |
| `skip` | Skip current phase |
| `jump to [phase]` | Jump to: places, affordances, breadboard, fat-marker, save |
| `revise [element]` | Edit a specific place, connection, or sketch |
| `add place` | Add a new place to the breadboard |
| `add connection` | Add a new connection between places |
| `remove [element]` | Remove a place or connection |
| `simplify` | Reduce to simpler breadboard form (fewer details) |
| `expand` | Add more detail to current diagram |
| `switch to breadboard` | Switch to working on the breadboard |
| `switch to fat marker` | Switch to working on fat marker sketches |
| `start over` | Begin from scratch |

---

## Quality Checks

Before finalizing any diagram, verify:

**Breadboard:**
- [ ] Every Place is reachable (no orphan nodes)
- [ ] Every Place has at least one exit (no dead ends, unless it's a terminal state)
- [ ] Error/failure paths are shown
- [ ] Entry point is clear
- [ ] Async/background steps are marked with dashed style
- [ ] Phase annotations present (if multi-phase delivery)

**Fat Marker Sketch:**
- [ ] Element types use ALL CAPS labels
- [ ] Layout zones are clear (not just a list of elements)
- [ ] Data flow relationships shown with dotted arrows where applicable
- [ ] Matches the corresponding breadboard Place name
- [ ] Not too detailed — if it looks like a wireframe, simplify

---

## Track Usage (Silent)

After completing a shape session, silently update `System/usage_log.md` if there's a relevant feature checkbox to mark.
