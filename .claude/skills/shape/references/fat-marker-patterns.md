# Fat Marker Sketch Mermaid Patterns

All sketches use `%%{init: {'theme': 'neutral'}}%%` for light/dark mode compatibility.

Fat marker sketches show **what goes where** on a screen — rough zones and element types, not pixel-level layout.

---

## Pattern 1: Simple Screen Layout

Best for: Single-purpose screens, forms, simple views.

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart TD
    subgraph Screen["Screen Name"]
        A["ELEMENT TYPE: description"]
        B["ELEMENT TYPE: description"]
        C["ELEMENT TYPE: description"]
        D["BUTTON: action label"]
    end
```

**Rules:**
- One subgraph = one screen
- Elements listed top to bottom = visual reading order
- Use ALL CAPS for element types
- Keep descriptions to 2-4 words

---

## Pattern 2: Zoned Layout

Best for: Dashboards, multi-panel screens, complex views.

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart TD
    subgraph HEADER["Header Zone"]
        H1["TITLE: page name"]
        H2["CONTROLS: filters, actions"]
    end

    subgraph MAIN["Main Content"]
        direction LR
        subgraph LEFT["Left Panel"]
            L1["ELEMENT"]
            L2["ELEMENT"]
        end
        subgraph RIGHT["Right Panel"]
            R1["ELEMENT"]
            R2["ELEMENT"]
        end
    end

    subgraph FOOTER["Footer Zone"]
        F1["ELEMENT"]
    end

    HEADER --> MAIN
    MAIN --> FOOTER
```

**Rules:**
- Top-level subgraphs = major screen zones (header, main, sidebar, footer)
- `direction LR` inside a zone creates side-by-side columns
- Solid arrows (`-->`) between zones show visual hierarchy / reading order
- Don't nest more than 2 levels deep

---

## Pattern 3: Data Flow Layout

Best for: Screens with filtering, drill-down, or interactive data relationships.

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart TD
    subgraph FILTERS["Filter Bar"]
        F1["DROPDOWN: dimension A"]
        F2["DROPDOWN: dimension B"]
        F3["DATE PICKER: range"]
    end

    subgraph VISUALS["Data Visualization"]
        direction LR
        V1["CHART: primary metric"]
        V2["CHART: secondary metric"]
    end

    subgraph TABLE["Detail View"]
        T1["TABLE: detailed records"]
    end

    F1 -.->|"filters"| V1
    F2 -.->|"filters"| V2
    VISUALS -->|"drill down"| TABLE
```

**Rules:**
- Dotted arrows (`-.->`) show data flow / filtering relationships
- Solid arrows show user navigation flow (clicking to drill down)
- Label filter relationships to clarify what drives what

---

## Pattern 4: Multi-Tab / Multi-View

Best for: Screens with tabs, toggles, or mode switches.

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart TD
    subgraph HEADER["Page Header"]
        H1["TITLE: page name"]
        H2["TABS: View A | View B | View C"]
    end

    subgraph VIEW_A["View A (default)"]
        A1["CHART: metric overview"]
        A2["TABLE: detail rows"]
    end

    subgraph VIEW_B["View B"]
        B1["LIST: grouped items"]
        B2["BUTTON: bulk action"]
    end

    HEADER -->|"Tab A"| VIEW_A
    HEADER -->|"Tab B"| VIEW_B
```

---

## Element Type Labels

Use these standard labels for consistency:

| Label | Represents |
|-------|-----------|
| `TITLE` | Page or section heading |
| `BUTTON` | Clickable action |
| `LINK` | Navigation link |
| `DROPDOWN` | Selection control |
| `INPUT` | Text entry field |
| `TOGGLE` | On/off switch |
| `CHECKBOX` | Multi-select option |
| `DATE PICKER` | Date selection |
| `SEARCH` | Search field |
| `TABLE` | Data table |
| `LIST` | Ordered/unordered list |
| `CHART` | Any data visualization |
| `CARD` | Content card / tile |
| `FORM` | Group of input fields |
| `TABS` | Tab navigation |
| `NAV` | Navigation menu |
| `BREADCRUMB` | Path navigation |
| `BADGE` | Status indicator |
| `ALERT` | Notification / warning |
| `MODAL` | Overlay dialog |
| `EMPTY STATE` | No-data placeholder |

---

## Layout Direction Guide

| Layout need | Mermaid approach |
|-------------|-----------------|
| Vertical stack (most screens) | `flowchart TD` (default) |
| Side-by-side panels | `direction LR` inside a subgraph |
| Grid of cards | Multiple nodes in a `direction LR` subgraph |
| Sidebar + main | Nested subgraphs with `direction LR` |
| Full-width sections stacked | Top-level subgraphs connected with `-->` |

---

## Complexity Guidelines

| Screen complexity | Recommended approach |
|-------------------|---------------------|
| Simple form or list | Pattern 1 (simple layout) |
| Dashboard with zones | Pattern 2 (zoned layout) |
| Data-heavy with filters | Pattern 3 (data flow) |
| Multi-view screen | Pattern 4 (multi-tab) |
| Very complex screen | Split into multiple sketches (one per tab/mode) |

---

## Connecting Fat Marker Sketches to Breadboards

When generating both diagram types, name fat marker sketch subgraphs to match breadboard Place names. This creates a clear mapping:

- Breadboard Place: `(["Dashboard"])` → Fat marker: `subgraph Dashboard["Dashboard"]`
- Breadboard Place: `(["Config Screen"])` → Fat marker: `subgraph Config["Config Screen"]`

Generate one fat marker sketch per key Place identified in the breadboard. Skip Places that are simple (confirmation dialogs, loading states) — only sketch screens with meaningful layout decisions.
