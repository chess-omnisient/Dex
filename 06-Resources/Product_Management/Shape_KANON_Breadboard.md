# Shape: Better KANON Visibility and Control

**Date:** 2026-03-16
**Mode:** From PRD
**Related PRD:** [PRD_KANON_Visibility_Control.md](PRD_KANON_Visibility_Control.md)

---

## Breadboard 1: Buyer Flow (Project Creation)

The buyer selects their own dataset during project creation and is presented with the KANON risk report. They can continue with defaults, edit fields, swap tables, or exit to Own Data Prep.

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    subgraph "My Datasets"
        A1["Upload & register data"]
        A2["⏳ KANON1 runs during hydration"]
        A3["Risk report stored with dataset"]
    end

    subgraph "Project Creation — Step 1"
        B1["Select own table"]
        B2["Platform fetches KANON1 report"]
    end

    subgraph "Risk Report (Buyer)"
        C1["View field risk classes"]
        C2["Per-field controls: Accept / Remove / Edit rounding"]
        C3["Name the view"]
    end

    subgraph "Own Data Prep"
        D1["Create new table manually"]
        D2["Re-register + hydrate"]
    end

    subgraph "⏳ Project Processing"
        E1["⏳ SQL View created in _A schema"]
        E2["⏳ KANON2: drop, round, remove identifiers"]
        E3["⏳ New table registered"]
    end

    subgraph "Project Step 2+"
        F1["Continue project creation with mitigated view"]
    end

    E4["❌ No report found"]

    A1 -->|"registers"| A2
    A2 -->|"stores"| A3
    A3 -->|"user starts project"| B1
    B1 -->|"table selected"| B2
    B2 -->|"report exists"| C1
    B2 -->|"no report"| E4
    E4 -->|"Go to Own Data Prep"| D1
    E4 -->|"Select another table"| B1
    C1 -->|"Continue (accept defaults)"| E1
    C1 -->|"Edit fields"| C2
    C2 --> C3
    C3 -->|"Apply edits"| E1
    C1 -->|"Remove + Create New"| B1
    C1 -->|"Go to Own Data Prep"| D1
    D1 --> D2
    D2 -->|"re-registered"| B1
    E1 --> E2
    E2 --> E3
    E3 -->|"view ready"| F1

    style A2 fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
    style E1 fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
    style E2 fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
    style E3 fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
    style E4 fill:#fee,stroke:#c00
```

---

## Breadboard 2: Seller Flow (Project Approval)

The seller receives a project approval request and is shown the risk report and drift report for the data entering the collaboration. They can accept, reject, or edit their own table before approving.

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    subgraph "Project Approval Request"
        A1["Notification: project awaiting approval"]
    end

    subgraph "Seller Risk Report"
        B1["View KANON risk profile"]
        B2["View drift report"]
        B3["Edit own table based on drift"]
    end

    subgraph "Approval Decision"
        C1["Accept project"]
        C2["Reject project"]
    end

    subgraph "⏳ Project Processing"
        D1["⏳ Project moves to Processing"]
        D2["⏳ Cleanroom join on mitigated views"]
    end

    subgraph "Project Active"
        E1["Cohorts & audiences built"]
        E2["Activation & attribution"]
    end

    A1 -->|"opens approval"| B1
    B1 --- B2
    B1 -->|"needs edits"| B3
    B3 -->|"edits applied"| B1
    B1 -->|"Accept"| C1
    B1 -->|"Reject"| C2
    C1 -->|"approved"| D1
    D1 --> D2
    D2 -->|"complete"| E1
    E1 --> E2

    style D1 fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
    style D2 fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
```

---

## Breadboard 3: Combined Overview (Both Actors)

High-level end-to-end showing how buyer and seller flows connect.

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart TD
    P1(["My Datasets\n(KANON1 at hydration)"])
    P2(["Project Creation\nStep 1: Select Table"])
    P3(["Buyer Risk Report\n+ Edit Controls"])
    P4(["⏳ SQL View Created\n+ KANON2 Processing"])
    P5(["Seller Approval\nRisk + Drift Report"])
    P6(["⏳ Cleanroom Join\nOMN-ID Matching"])
    P7(["Project Active\nCohorts & Activation"])

    P1 -->|"buyer starts project"| P2
    P2 -->|"table selected"| P3
    P3 -->|"continue / edits applied"| P4
    P4 -->|"sends for approval"| P5
    P5 -->|"seller accepts"| P6
    P6 -->|"processing complete"| P7
    P5 -->|"seller rejects"| P3

    style P4 fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
    style P6 fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
```

### Legend
| Symbol | Meaning |
|--------|---------|
| **Bordered group** (subgraph) | Place — a screen, page, or state the user visits |
| **Rectangle** inside a group | Affordance — something the user can see or do |
| **Solid arrow** `-->` with label | Connection — user action that triggers a transition |
| **Line without arrow** `---` | Co-located items — no sequence implied |
| **Dashed border** | Background/async step — no user interaction |
| **Red box** | Error or blocked state |

---

## Fat Marker Sketches

### Buyer Risk Report (Project Creation — Step 1)

The primary screen where the buyer reviews field-level risk and decides how to proceed.

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart TD
    subgraph HEADER["Header"]
        H1["TITLE: ⚠️ PII Re-identification Risk Report"]
        H2["BADGE: Table Name"]
    end

    subgraph REPORT["Risk Report Table"]
        direction LR
        subgraph COLUMNS["Field List"]
            R1["TABLE: Field Name | Risk Class | Mitigation | Controls"]
        end
        subgraph DETAIL["Risk Detail"]
            R2["BADGE: High — Field will be dropped"]
            R3["BADGE: Medium-Numeric — Rounded + records dropped"]
            R4["BADGE: Medium-Text — Records dropped"]
        end
    end

    subgraph CONTROLS["Per-Field Controls"]
        direction LR
        C1["BUTTON: Accept"]
        C2["BUTTON: Remove"]
        C3["BUTTON: Edit"]
        C4["DROPDOWN: Rounding options (numeric only)"]
    end

    subgraph VIEW_NAME["View Naming"]
        V1["INPUT: Name for new view"]
        V2["LABEL: System name (auto-generated)"]
    end

    subgraph ACTIONS["Action Bar"]
        direction LR
        A1["BUTTON: Continue (accept defaults)"]
        A2["BUTTON: Apply Edits + Create View"]
        A3["LINK: Remove + Select Another Table"]
        A4["LINK: Go to Own Data Prep"]
    end

    HEADER --> REPORT
    REPORT --> CONTROLS
    CONTROLS --> VIEW_NAME
    VIEW_NAME --> ACTIONS
    C3 -.->|"opens"| C4
```

### Seller Approval Risk Report

The screen shown to the data owner when approving a project.

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart TD
    subgraph HEADER["Header"]
        H1["TITLE: Project Approval — Risk Report"]
        H2["BADGE: Project Name"]
        H3["BADGE: Requesting Party"]
    end

    subgraph RISK["KANON Risk Profile"]
        R1["TABLE: Field Name | Risk Class | Mitigation Applied"]
        R2["ALERT: Fields flagged for investigation"]
    end

    subgraph DRIFT["Drift Report"]
        D1["TABLE: Schema changes since last hydration"]
        D2["BADGE: Drift severity indicator"]
    end

    subgraph EDIT["Seller Edit Controls"]
        E1["BUTTON: Edit own table based on drift"]
        E2["LINK: View full data processing report"]
    end

    subgraph ACTIONS["Decision"]
        direction LR
        A1["BUTTON: Accept Project"]
        A2["BUTTON: Reject Project"]
    end

    HEADER --> RISK
    RISK --> DRIFT
    DRIFT --> EDIT
    EDIT --> ACTIONS
```

### Dataset Risk Report (My Datasets / Available Datasets)

The pre-computed risk report stored with the dataset, viewable outside project context.

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart TD
    subgraph HEADER["Available Datasets"]
        H1["TITLE: KANON Report"]
        H2["TABS: Dataset Readied | Awaiting Hydration | Action Required"]
    end

    subgraph STATUS["Dataset Status"]
        direction LR
        S1["CARD: Dataset Ready\n(KANON1 complete)"]
        S2["CARD: Awaiting Hydration\n(no report yet)"]
        S3["CARD: Action: Extend Risk Report\n(schema changed)"]
    end

    subgraph REPORT["Risk Report Preview"]
        R1["TABLE: Field Name | Risk Class | Mitigation"]
        R2["BADGE: Report age / last hydration date"]
    end

    subgraph ACTIONS["Actions"]
        direction LR
        A1["BUTTON: Use in Project"]
        A2["BUTTON: Re-hydrate"]
        A3["BUTTON: View Full Report"]
    end

    HEADER --> STATUS
    STATUS -->|"select dataset"| REPORT
    REPORT --> ACTIONS
```

---

## Flow Notes

- **KANON1 is pre-computed** — runs at hydration (dataset registration), never at project creation time. This is critical for performance — the report is always ready instantly.
- **KANON2 runs during project processing** — this is the step that actually drops columns, rounds fields, and removes identifiable records. It happens after the buyer confirms edits and creates the SQL view.
- **Seller rejection loops back** — if the seller rejects, the buyer may need to re-edit fields and resubmit. The seller always sees the final mitigated state at acceptance time.
- **Edge case: no report** — blocks the buyer from continuing. They must re-register the dataset or choose a different table.
- **Priority TBD** — which ships first: Buyer Risk Report (project creation) or Seller Approval Risk Report? See Open Questions in PRD.
