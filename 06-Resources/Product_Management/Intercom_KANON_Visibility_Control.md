# KANON: Data Risk Visibility and Control

KANON is the platform's built-in data risk assessment system. It automatically identifies columns in your datasets that could pose re-identification risk, classifies them by severity, and applies mitigations before data enters a collaboration. Both buyers and sellers see risk reports at key decision points — during project creation and project approval.

## Key concepts

| Term | Meaning |
|------|---------|
| **KANON1** | The initial risk assessment that runs automatically when a dataset is registered (during data ingestion). It classifies each column by risk level and stores a report with the dataset. |
| **KANON2** | The mitigation step that runs during project processing. It applies the actions from the risk report — dropping columns, rounding values, and removing identifiable records. |
| **Risk class** | A severity rating assigned to each column: **High** (column will be dropped), **Medium-Numeric** (values rounded, some records dropped), or **Medium-Text** (some records dropped). |
| **Drift report** | A comparison showing schema changes since the dataset was last ingested. Shown to sellers during project approval. |
| **Mitigated view** | The cleaned version of a dataset after KANON2 processing. This is what enters the collaboration. |

## How KANON works

KANON operates in two phases, at two different points in the workflow.

### Phase 1: Risk assessment at dataset registration

When you upload and register a dataset, KANON1 runs automatically during data ingestion. It scans every column, assigns a risk class, and stores the report alongside the dataset. This means the risk report is always available instantly when you start a project — there's no waiting.

### Phase 2: Mitigation during project processing

After a buyer confirms their column-level choices and the seller approves the project, KANON2 runs as part of project processing. It creates a SQL view that drops high-risk columns, rounds numeric columns, and removes identifiable records based on the settings from the risk report.

## Buyer flow: reviewing risk during project creation

When creating a project, the buyer selects a dataset table. The platform retrieves the stored KANON1 report for that table and presents it before the project proceeds.

**What the buyer sees:**

The risk report displays every column in the selected table with its risk class and the recommended mitigation. From here, the buyer can:

- **Continue with defaults** — accept all recommended mitigations and proceed
- **Edit individual columns** — adjust rounding options for numeric columns, or remove specific columns
- **Name the view** — give the mitigated version a recognizable name
- **Switch tables** — remove the current selection and pick a different table
- **Go to Own Data Prep** — exit to manually prepare a new table, then return

**If no risk report exists** (e.g. the dataset wasn't ingested), the buyer is blocked from continuing. They can either select a different table or go to Own Data Prep to re-register the dataset.

Once the buyer confirms, the platform creates a SQL view and KANON2 processes it in the background. When processing completes, the project moves to the next step using the mitigated view.

## Seller flow: reviewing risk during project approval

When a project is submitted for approval, the seller (data owner) receives a notification and is shown the risk profile for the data entering the collaboration.

**What the seller sees:**

- **KANON risk profile** — the column-level risk classes and mitigations that have been applied
- **Drift report** — any schema changes since the dataset was last ingested, with a severity indicator
- **Flagged columns** — columns that may need investigation before approval

**What the seller can do:**

- **Accept the project** — the project moves to processing, where the cleanroom join runs on the mitigated views
- **Reject the project** — the buyer is notified and may need to re-edit columns and resubmit
- **Edit their own table** — if drift is detected, the seller can make adjustments before deciding

After acceptance, the project processes in the background. Once the cleanroom join completes, the project becomes active and cohorts, audiences, and activation are available.

## Viewing risk reports outside a project

Risk reports are also available in **My Datasets** / **Available Datasets**, independent of any project context.

Datasets are organized by status:

| Status | Meaning |
|--------|---------|
| **Dataset Ready** | KANON1 is complete. The risk report is available and the dataset can be used in projects. |
| **Awaiting Data Ingestion** | The dataset has been uploaded but data ingestion hasn't completed yet. No report is available. |
| **Action Required** | The schema has changed since the last data ingestion. The risk report needs to be extended or the dataset re-ingested. |

From any dataset, you can view the full risk report (column names, risk classes, and mitigations), see when the report was last generated, and choose to use the dataset in a project or trigger a re-data ingestion.

## End-to-end flow summary

1. **Dataset registration** — Buyer uploads data; KANON1 runs automatically and stores the risk report
2. **Project creation** — Buyer selects a table, reviews the risk report, and edits column-level controls if needed
3. **View creation** — Platform creates a SQL view and runs KANON2 to apply mitigations (background processing)
4. **Seller approval** — Seller reviews the risk profile and drift report, then accepts or rejects
5. **Cleanroom join** — On acceptance, the platform runs the join on mitigated views (background processing)
6. **Project active** — Cohorts, audiences, and activation become available

## Limitations

- KANON1 must complete before a dataset can be used in a project — there is no way to bypass the risk report
- If a seller rejects a project, the buyer must re-edit and resubmit; there is no partial approval
- Schema drift after data ingestion requires action before the dataset can be used in new projects
- KANON2 processing time depends on dataset size and the number of mitigations applied

## Related features

- [Datasets](#) — managing and registering your data
- [Projects](#) — creating and managing collaborations
- [Own Data Prep](#) — manually preparing tables before project creation

## Guides

- [How to review a risk report during project creation](#)
- [How to approve a project as a data owner](#)
- [How to re-ingest a dataset](#)

---

**Before publishing:**
- [ ] Confirm: which ships first — Buyer Risk Report or Seller Approval Risk Report? (marked as open question in the PRD)
- [ ] Confirm: exact risk class names and mitigation descriptions match the product UI
- [ ] Confirm: "Own Data Prep" is the correct user-facing name for that section
- [ ] Confirm: drift report severity levels — are there named tiers or just an indicator?
- [ ] Article to create: **How to review a risk report during project creation** (how-to, linked above)
- [ ] Article to create: **How to approve a project as a data owner** (how-to, linked above)
- [ ] Article to create: **How to re-ingest a dataset** (how-to, linked above)
- [ ] Check if existing Datasets hub article needs a link added to this article
- [ ] Check if existing Projects hub article needs a link added to this article
