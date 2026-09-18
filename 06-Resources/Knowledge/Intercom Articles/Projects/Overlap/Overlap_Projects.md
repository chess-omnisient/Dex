> **Status:** Draft — not yet published

# Overlap Projects

An Overlap project lets you compare your customer dataset against a partner's shared dataset to identify where your customer bases intersect — and where they don't. It's the most common starting point in a new data partnership, giving both parties a clear picture of shared and exclusive customers before committing to deeper collaboration.

---

## Key concepts

| Term | What it means |
|---|---|
| **Overlap** | Customers who appear in both your dataset and your partner's dataset. |
| **Non-overlap** | Customers who appear in only one dataset. Useful for identifying acquisition and expansion opportunities. |
| **Customer Identifier** | The PII field mapped to your dataset when it was registered. Used to match records between the two datasets during an overlap. |
| **Denormalized dataset** | A dataset with one row per customer. Overlap projects require this structure — data with multiple rows per customer must be flattened before use. |
| **Segment** | An additional attribute attached to customer records (e.g., spend tier, health score) used to filter and enrich overlap results. |

---

## Match types

When creating an Overlap project, you choose how records are matched between the two datasets.

| Match type | How it works | When to use |
|---|---|---|
| **Best match** | The platform matches across multiple PII fields — phone number, first name, surname, and others — to find the strongest possible match automatically. | Default. Use when you want the highest match rate. |
| **ID match** | Matching is performed on the ID field specifically. | Use when you want to match on a single, known identifier. |

---

## How Overlap works

1. You select one of your own datasets and one shared partner dataset.
2. The platform checks that both datasets share at least one common PII column. If none are found, you are warned before submitting.
3. Records are matched using your chosen match type.
4. The project is submitted for approval by the partner dataset owner.
5. Once approved and processed, results are available in Power BI.

**Results show:**
- The number and percentage of customers appearing in both datasets
- Customers appearing only in your dataset
- Customers appearing only in the partner's dataset — if the partner has chosen to share their non-overlap

Results can be filtered by any segments attached to either dataset.

---

## What you can do with results

| Capability | Detail |
|---|---|
| **Understand your shared customer base** | See how much of your customer base overlaps with a partner's — useful for evaluating partnership value before deeper collaboration. |
| **Segmented analysis** | Filter results by segments to answer questions like: "Of our shared customers, how many are high-value?" Segments must be uploaded as additional columns on the dataset. |
| **Overlap-only sharing** | Each party sees shared customers but not the other's exclusive customers. Protects acquisition strategy and marketing IP. |
| **Full base sharing** | Both parties see each other's complete customer breakdown. Supports comparative profiling and identifying untapped segments. |
| **Selections** | Create defined subsets of customers from results for use in activations or further analysis. Subject to dataset share agreement terms. |

> For more on what data is available in results, see [Dataset Share](#).

---

## Limitations

| Limitation | Detail |
|---|---|
| **Transactional and multi-row data** | Overlap is optimised for one record per customer. Data with multiple rows per customer (transactional, claims, diagnosis) must be aggregated to customer level before use. Contact your account manager if you need support with this. |
| **PII matching** | Both datasets must share at least one common PII column. If none are found, the overlap returns zero results. The platform warns you at setup before you submit. |
| **Datasets fixed after creation** | Once a project is created, the selected datasets cannot be changed. Create a new project to use different tables. |
| **No custom reports** | The Power BI report is based on a fixed template. Custom report configurations are not currently available. |

---

## Analytical tools

| Tool | Available to | Notes |
|---|---|---|
| **Power BI** | All users | Default visualisation for overlap results |
| **Jupyter** | Technical users | Subscription-dependent |
| **SQLPad** | Technical users | Direct query access |

---

## Project roles

| Role | Can do |
|---|---|
| **Owner** | Full control — manage users, edit content, update permissions, delete project |
| **Read and Write** | View and edit the project, manage data and reports, perform selections |
| **Read Only** | View only — cannot edit the project, data, or reports |

You are automatically set as Owner when you create a project. All added users default to **Read Only**.

> See [Roles and Permissions](#) for full details.

---

## Related

- [Projects](#) — project types, statuses, notifications, and creating a project
- [Project Approvals](#) — how the approval process works
- [Dataset Share](#) — what data is shared and how it affects your results
- [Roles and Permissions](#) — managing user access across projects
- [Selections](#) — working with selections from overlap results
