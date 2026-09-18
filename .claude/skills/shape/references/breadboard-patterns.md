# Breadboard Mermaid Patterns

All breadboards use `%%{init: {'theme': 'neutral'}}%%` for light/dark mode compatibility.

---

## Pattern 1: Simple Breadboard

Best for: Quick ideation, simple flows, early shaping.

**Places** = Stadium-shaped nodes `(["..."])`
**Affordances** = Edge labels (what the user does to move between places)
**Connections** = Arrows between places

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    P1(["Place Name"])
    P2(["Place Name"])
    P3(["Place Name"])

    P1 -->|"affordance\nanother affordance"| P2
    P2 -->|"affordance"| P3
    P3 -->|"error / back"| P2
```

**Rules:**
- One node per Place — keep names short (2-4 words)
- Edge labels list the key affordances that trigger the transition
- Use `\n` to stack multiple affordances on one edge
- Use `LR` (left-to-right) for linear flows, `TD` (top-down) for hierarchical ones
- Error/back paths go right-to-left or bottom-to-top

---

## Pattern 2: Detailed Breadboard

Best for: Complex flows, stakeholder communication, PRD-level shaping.

**Places** = Subgraphs (named blocks)
**Affordances** = Nodes inside subgraphs
**Connections** = Arrows between nodes across subgraphs

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    subgraph "Place Name"
        A1["Affordance: action or element"]
        A2["Affordance: another element"]
    end

    subgraph "Next Place"
        B1["Affordance"]
        B2["Affordance"]
    end

    A1 -->|"trigger"| A2
    A2 -->|"trigger"| B1
    B1 --> B2
```

**Rules:**
- Subgraph titles are Place names — use quotes for multi-word names
- Nodes inside represent what the user can see or do at that Place
- Arrows between nodes show flow (with optional trigger labels)
- Use `---` (no arrowhead) for co-located items that don't imply sequence
- Keep affordance descriptions to 3-5 words max

---

## Pattern 3: Branching Flow

For flows with conditional paths (success/failure, role-based, phased rollout).

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    P1(["Start"])
    P2(["Decision Point"])
    P3(["Success Path"])
    P4(["Error Path"])
    P5(["End State"])

    P1 -->|"submits form"| P2
    P2 -->|"valid"| P3
    P2 -->|"invalid"| P4
    P3 -->|"confirms"| P5
    P4 -->|"corrects input"| P2
```

---

## Pattern 4: Parallel Paths

For flows where users can take multiple independent actions from one Place.

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart TD
    P1(["Hub Screen"])
    P2(["Path A"])
    P3(["Path B"])
    P4(["Path C"])
    P5(["Shared Destination"])

    P1 -->|"action A"| P2
    P1 -->|"action B"| P3
    P1 -->|"action C"| P4
    P2 -->|"completes"| P5
    P3 -->|"completes"| P5
    P4 -->|"completes"| P5
```

---

## Pattern 5: Async / Background Process

For steps that happen without user interaction (processing, email triggers, scheduled jobs).

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    P1(["User Action"])
    BG["⏳ Background Process\n(no user interaction)"]
    P2(["Result Screen"])

    P1 -->|"triggers"| BG
    BG -->|"email notification"| P2

    style BG fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
```

**Rules:**
- Use dashed stroke for background/async steps
- Always show how the user is notified when the process completes
- Label clearly that no user interaction occurs

---

## Pattern 6: Phased Rollout

For features delivered in phases, showing what's available when.

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    P1(["Core Screen"])
    P2(["Phase 1 Feature"])
    P3(["Phase 2 Feature"])
    P4(["Phase 3 Feature"])

    P1 -->|"available now"| P2
    P1 -.->|"Phase 2"| P3
    P1 -.->|"Phase 3"| P4
```

**Rules:**
- Solid arrows for current-phase connections
- Dotted arrows (`-.->`) for future-phase connections with phase label
- Helps stakeholders see the delivery roadmap visually

---

## Visual Legend (include in generated diagrams)

Add this legend below every breadboard diagram so readers can interpret the notation without prior Shape Up knowledge.

```markdown
### Legend
| Symbol | Meaning |
|--------|---------|
| **Bordered group** (subgraph) | Place — a screen, page, or state the user visits |
| **Rectangle** inside a group | Affordance — something the user can see or do |
| **Solid arrow** `-->` with label | Connection — user action that triggers a transition |
| **Line without arrow** `---` | Co-located items — no sequence implied |
| **Dashed border** | Background/async step — no user interaction |
| **Red box** ❌ | Error or failure state |
| **Dotted arrow** `-.->` | Future phase — not yet available |
```

---

## Node Naming Conventions

| Element | Format | Example |
|---------|--------|---------|
| Place (simple) | `P1(["Name"])` | `P1(["Dashboard"])` |
| Place (detailed) | `subgraph "Name"` | `subgraph "Project Config"` |
| Affordance | `A1["Description"]` | `A1["Select template"]` |
| System step | `S1["⏳ Description"]` | `S1["⏳ Processing"]` |
| Error state | `E1["❌ Description"]` | `E1["❌ Validation failed"]` |

Use prefixes per Place for readability: Place 1 affordances = A1, A2; Place 2 = B1, B2; etc.

---

## Complexity Guidelines

| Flow steps | Recommended pattern |
|------------|-------------------|
| 3-5 | Simple breadboard |
| 6-10 | Detailed breadboard |
| 10+ | Split into sub-flows (happy path + error handling + admin) |
| Multiple actors | Separate breadboard per actor, or use subgraph columns |
