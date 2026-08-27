#!/usr/bin/env python3
"""
Migrate existing Dex vault to Obsidian wiki link format
Zero AI tokens - pure regex pattern matching
"""
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.portable_contract import ContractViolation, resolve

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

BASE_DIR = Path(os.environ.get('VAULT_PATH', Path.cwd()))


def _entity_files(directory: Path):
    """Yield real entity pages, never the shipped folder placeholder."""
    if not directory.exists():
        return
    for entity_file in directory.rglob('*.md'):
        if entity_file.name.casefold() != 'readme.md':
            yield entity_file


def _is_migratable_markdown(path: Path) -> bool:
    """Only user-owned or seeded vault content may be rewritten."""
    if path.is_symlink():
        return False
    try:
        relative = path.relative_to(BASE_DIR).as_posix()
        resolution = resolve(relative)
    except (ContractViolation, ValueError):
        return False
    return not resolution.denied and resolution.ownership in {'seed', 'vault'}

# Build indices for smart conversion
def build_person_index() -> dict:
    """Build index of all person filenames"""
    people_dir = BASE_DIR / '05-Areas' / 'People'
    index = {}
    
    for person_file in _entity_files(people_dir):
        name = person_file.stem  # e.g., John_Doe
        rel_path = person_file.relative_to(BASE_DIR)
        index[name] = str(rel_path)
    
    return index

def build_project_index() -> dict:
    """Build index of all projects"""
    projects_dir = BASE_DIR / '04-Projects'
    index = {}
    
    for proj_file in _entity_files(projects_dir):
        name = proj_file.stem
        rel_path = proj_file.relative_to(BASE_DIR)
        index[name] = str(rel_path)
    
    return index

def build_company_index() -> dict:
    """Build index of all companies"""
    companies_dir = BASE_DIR / '05-Areas' / 'Companies'
    index = {}
    
    for comp_file in _entity_files(companies_dir):
        name = comp_file.stem
        rel_path = comp_file.relative_to(BASE_DIR)
        index[name] = str(rel_path)
    
    return index

def convert_references_in_file(content: str, person_idx: dict, 
                               project_idx: dict, company_idx: dict) -> Tuple[str, int]:
    """Convert plain text references to wiki links. Returns (new_content, num_changes)"""
    changes = 0
    
    # Skip fenced blocks and inline code spans.
    code_spans = []
    def save_code_span(match):
        code_spans.append(match.group(0))
        return f"__CODE_SPAN_{len(code_spans)-1}__"
    
    content = re.sub(r'```.*?```', save_code_span, content, flags=re.DOTALL)
    content = re.sub(
        r'(?P<ticks>`+).*?(?P=ticks)',
        save_code_span,
        content,
        flags=re.DOTALL,
    )
    
    # Convert person references (Firstname_Lastname pattern)
    for person_name, person_path in person_idx.items():
        # Only convert if not already a wiki link
        pattern = rf'(?<!\[\[)\b({re.escape(person_name)})\b(?!\]\])'
        matches = len(re.findall(pattern, content))
        if matches > 0:
            content = re.sub(pattern, r'[[\1]]', content)
            changes += matches
    
    # Convert project references (04-Projects/Project_Name)
    for project_name, project_path in project_idx.items():
        pattern = rf'(?<!\[\[)\b({re.escape(project_path)})\b(?!\]\])'
        matches = len(re.findall(pattern, content))
        if matches > 0:
            content = re.sub(pattern, r'[[\1]]', content)
            changes += matches
    
    # Convert company references
    for company_name, company_path in company_idx.items():
        pattern = rf'(?<!\[\[)\b({re.escape(company_name)})\b(?!\]\])'
        matches = len(re.findall(pattern, content))
        if matches > 0:
            content = re.sub(pattern, r'[[\1]]', content)
            changes += matches
    
    # Convert task ID references (^task-YYYYMMDD-XXX)
    pattern = r'(?<!\[\[)\^(task-\d{8}-\d{3,})(?!\]\])'
    matches = len(re.findall(pattern, content))
    if matches > 0:
        content = re.sub(pattern, r'[[^\1]]', content)
        changes += matches
    
    # Restore code blocks and inline spans.
    for i, span in enumerate(code_spans):
        content = content.replace(f"__CODE_SPAN_{i}__", span)
    
    return content, changes

def estimate_migration(files: List[Path]) -> str:
    """Estimate migration time"""
    num_files = len(files)
    est_seconds = num_files / 30  # ~30 files/sec
    
    if est_seconds < 60:
        return f"~{int(est_seconds)} seconds"
    else:
        minutes = int(est_seconds / 60)
        return f"~{minutes} minute{'s' if minutes > 1 else ''}"


def create_git_backup() -> tuple[str, bool]:
    """Capture the exact pre-migration state and return its commit plus creation flag."""
    add = subprocess.run(
        ['git', 'add', '-A'],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )
    if add.returncode != 0:
        raise RuntimeError(add.stderr.strip() or 'git could not stage the vault')

    staged = subprocess.run(
        ['git', 'diff', '--cached', '--quiet', '--'],
        cwd=BASE_DIR,
    )
    if staged.returncode not in (0, 1):
        raise RuntimeError('git could not verify the staged backup state')

    created = staged.returncode == 1
    if created:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        commit = subprocess.run(
            ['git', 'commit', '-m', f'Backup before Obsidian migration - {timestamp}'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        if commit.returncode != 0:
            raise RuntimeError(commit.stderr.strip() or commit.stdout.strip() or 'git could not create the backup commit')

    baseline = subprocess.run(
        ['git', 'rev-parse', 'HEAD'],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )
    if baseline.returncode != 0:
        raise RuntimeError(baseline.stderr.strip() or 'git could not identify the backup commit')
    return baseline.stdout.strip(), created

def migrate_vault(dry_run: bool = False) -> int:
    """Main migration function"""
    print("Dex Obsidian Migration\n" + "="*50)
    
    # Build indices
    print("Building indices...")
    person_idx = build_person_index()
    project_idx = build_project_index()
    company_idx = build_company_index()
    print(f"  Found {len(person_idx)} people")
    print(f"  Found {len(project_idx)} projects")
    print(f"  Found {len(company_idx)} companies")
    
    # Find all markdown files
    print("\nScanning vault...")
    md_files = [
        path for path in BASE_DIR.rglob('*.md')
        if _is_migratable_markdown(path)
    ]
    print(f"  Found {len(md_files)} markdown files")
    print(f"  Estimated time: {estimate_migration(md_files)}")
    
    if dry_run:
        print("\n[DRY RUN MODE] - No files will be modified")
    
    input("\nPress Enter to continue...")
    
    # Create backup via git
    backup_ref = None
    if not dry_run:
        print("\nCreating backup...")
        try:
            backup_ref, backup_created = create_git_backup()
        except RuntimeError as error:
            print(f"Backup failed; no files were changed: {error}")
            return 1
        if backup_created:
            print(f"  Backup commit created: {backup_ref}")
        else:
            print(f"  No new commit needed; the vault was already captured at {backup_ref}")
    
    # Process files
    print("\nConverting files...")
    total_changes = 0
    files_modified = 0
    
    iterator = tqdm(md_files, desc="Processing") if HAS_TQDM else md_files
    
    for md_file in iterator:
        try:
            content = md_file.read_text()
            new_content, changes = convert_references_in_file(
                content, person_idx, project_idx, company_idx
            )
            
            if changes > 0:
                if not dry_run:
                    md_file.write_text(new_content)
                files_modified += 1
                total_changes += changes
        except Exception as e:
            print(f"\nError processing {md_file}: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("Migration Complete!")
    print(f"  Files scanned: {len(md_files)}")
    print(f"  Files modified: {files_modified}")
    print(f"  Total conversions: {total_changes}")
    
    if not dry_run:
        print(f"\nBackup baseline: {backup_ref}")
        print(
            "To revert these changes without rewriting history: "
            f"git restore --source={backup_ref} --worktree -- ."
        )
        
        # macOS notification
        subprocess.run([
            'osascript', '-e',
            f'display notification "{files_modified} files converted with wiki links" '
            f'with title "Dex Obsidian Migration Complete" sound name "Glass"'
        ])

        # Sound
        subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])
    else:
        print("\n[DRY RUN] No files were modified. Run without --dry-run to apply changes.")

    return 0

if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    raise SystemExit(migrate_vault(dry_run=dry_run))
