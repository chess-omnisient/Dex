---
status: draft
audience: internal
owner: Chess Ashley-Cooper
process_owner: Tristan Venter, Data Product Manager
reviewer: Tristan Venter
source_task: https://app.clickup.com/t/869fcxxh8
source_doc: https://app.clickup.com/9012824942/docs/8ck9jve-230572
created: 2026-10-21
updated: 2026-10-29
---

> ⚠️ **Internal only.** This article is published to the Help Center for staff only. The CICTR neutral cleanroom runs as Manual Enablement by Data Science, and there is no self-service flow for a customer to follow.
>
> Owner: Chess Ashley-Cooper. Last reviewed: 2026-10-29.

# CICTR Neutral Cleanroom Project

A Cross Industry Conversion Tracking Report (CICTR) measures how a campaign performed in terms of conversion, such as uptake of a lending product or an increase in credit exposure. In the neutral pattern, TransUnion and the lender client each share their data only with the Omnisient CS profile, the match runs in a neutral Omnisient project, and no record-level data passes between the two parties: each sees only the finished HTML report.

Use this where TransUnion is unwilling to expose its bureau data to the client, or where governance restricts the older pattern of running CICTR inside one party's own profile. TransUnion is always the data provider; the lender client varies by engagement.

Manual Enablement is the manually triggered delivery of this report by the Customer Success and Data Science teams, as opposed to a self-service flow on the platform. The Excel workbook previously used for this delivery is retired; the HTML report is the only output.

![Both parties share into Omnisient; only the report goes back. The client, as data buyer, shares the CMF into the Omnisient CS profile. TransUnion, as provider, shares the bureau dataset into the same profile. Inside that profile the CMF is matched against the bureau dataset and the CICTR report is produced, then returned to the client. No record-level data passes between the client and TransUnion.](images/cictr-data-sharing-flow.png)

## Who does what

| Party | Role | Responsibility |
|---|---|---|
| **Client** | Data buyer | Prepares and shares the CMF, and receives the report. |
| **TransUnion** | Data provider | Shares the bureau dataset for the report type. |
| **Customer Success owner** | Triggers and delivers | Triggers the run and emails the report. |
| **Data Science** | Runs the pipeline | Sets up the project and runs the pipeline. |
| **Omnisient CS profile** | Neutral cleanroom | Holds both shared datasets and produces the report. |

## Before you start

- **Who owns this:** A Customer Success resource owns triggering the pipeline for as long as CICTR runs as Manual Enablement. The run itself is carried out by the Data Science team.
- **Permissions required:** Access to the Omnisient CS profile and the CICTR neutral project within it, plus Jupyter Notebook access in that project.
- **Prerequisites:** Both parties have a contractual cleanroom agreement in place covering how their data may be used.

> 💡 **Why an own dataset?** A project needs at least one own dataset before it can be initialised. In the neutral pattern neither party's data belongs to the Omnisient CS profile, so a Universe dataset conforming to the CMF schema stands in to open the environment. Matching logic runs against it and returns no matches, by design. It plays no part in the report.

## Steps

Each run is triggered manually once the datasets land.

### Set up

1. **Set up (Data Science).** Check that the CICTR neutral project exists under the Omnisient CS profile. If it does not, create it with a Universe dataset in the CMF schema as its own dataset. [Add where to find the project and link the project creation guide.]

### Load data

2. **Load data (client).** Upload the CMF on the Omnisient Platform against the [CMF data contract — link needed]. Validation flags out-of-spec fields, and the client maps them to accepted schema fields before the upload is accepted.
3. **Load data (TransUnion).** Share the bureau dataset for the report type into the project as a [partner share](https://help.omnisient.com/en/articles/10660392-partner-datasets), not an own dataset: New Credit Accounts Opened (NCAO) for the NCAO CICTR report; Additional Exposure, plus NCAO, for the CLI CICTR report.
4. **Load data (Data Science).** Add the CMF to the project manually and confirm it shows as validated before going further.

### Run

5. **Hand over (Data Science).** Tell the Customer Success owner that both datasets are in place. [Confirm who notifies whom, and in which channel.]
6. **Run (Customer Success triggers, Data Science runs).** Open the [Jupyter Notebook](https://help.omnisient.com/en/articles/8057225-integrated-jupyter-notebook-solution) in the project and run the pipeline: BestMatch overlap of the CMF against the bureau data, campaign window filtering, Client_Reference enrichment, link table build and consumer-level aggregation. It renders the HTML report directly. BestMatch is the existing matching method; this article does not change it.

   > ⚠️ **Client_Reference enrichment halts on failure.** If the CMF has no matching entry in TransUnion's Client Reference Lookup, the pipeline stops with an error and produces no report. No report is produced without a confirmed internal/external classification. Contact: [name or channel].

7. **Check (Data Science).** Confirm the report type label (NCAO CICTR or CLI CICTR) appears in both the banner subtitle and the browser page title. The two types share a design, so this label is the only visible difference.

### Deliver

8. **Deliver (Customer Success).** Email the HTML report to the client, one self-contained file per report type. [Add sender, template and recipient rule.]

**You should now have** a completed HTML report, produced from the match between the TransUnion dataset and the CMF, delivered to the client.

## About the report

There are two report types. Both share the CMF data contract, the pipeline, the internal/external classification and the report design. A client may receive one or both. Each is a self-contained HTML file.

| | NCAO CICTR report | CLI CICTR report |
|---|---|---|
| Reports on | New credit accounts opened by the campaign audience | Credit limit increases and further loans on existing accounts |
| Bureau dataset | New Credit Accounts Opened | Additional Exposure, plus NCAO for one section |
| Products | Personal and Micro Loans (PL), Credit Card (CC), Revolving Term Credit (RT), Home Loans (HL), Vehicle Finance (VF) | CC, PL, RT only. HL and VF are fixed-term, so a limit increase does not apply |
| Credit Terms Overview | Yes | No |
| New Account Acquisition Activity | No | Yes |

Report sections, top to bottom: report banner, Campaign Overview and Additional Filters, Conversion Summary, New Account Acquisition Activity (CLI only), Comparison Tool, and Credit Terms Overview (NCAO only).

Both types support Risk Band and Customer Age filters, multi-select, applied report-wide.

> ⚠️ **The report type label is mandatory** in the banner subtitle and browser page title. The two types share a design, so it is the only thing telling them apart at a glance.

> **Note:** **No download button.** The Manual Enablement report carries no download, print or export control. Client-side PDF export is backlogged for the self-service version.

> **Note:** **No delivery SLA.** Reports are delivered at the intervals the client requests, not against a committed turnaround.

## Troubleshooting

| Issue | Likely cause | Fix |
|---|---|---|
| Project will not create or initialise | No Universe dataset, or it does not follow the CMF schema | Load a Universe dataset in the CMF schema, then create the project. No matches against it is expected. |
| Bureau data looks out of date | Bureau datasets refresh monthly | Expected behaviour. Set client expectations on the reporting window. |
| The pipeline halts at Client_Reference enrichment | The CMF has no matching entry in TransUnion's Client Reference Lookup | Resolve the lookup entry with TransUnion before rerunning. Contact: [name or channel]. |
| The CMF upload is rejected | Fields are out of spec against the CMF data contract | The client maps the flagged fields to accepted schema fields, then re-uploads. |
| Baseline comparison is greyed out in the report | No campaign in the CMF has `is_baseline_reference = 1` | Expected. Baseline mode needs a baseline reference campaign in the CMF. |
| TransUnion objects to sharing their dataset at all | They read the request as sharing their bureau data with the client directly | Say: "TransUnion shares its bureau data with Omnisient only. The client never receives it and sees only the finished report." |
| The client asks where the download button is | Manual Enablement reports have no download, print or export control | Expected. Client-side PDF export is backlogged for the self-service version. |

## Key terms

| Term | What it means |
|---|---|
| **CICTR** | Cross Industry Conversion Tracking Report. Measures campaign conversion, such as uptake of a lending product or an increase in credit exposure. Sits under Consumer Insights. |
| **CMF (Client Master File)** | The file the lender client uploads with their campaign data, validated against a fixed data contract. Carries campaign ID, credit product code, campaign start and end dates, consumer ID number and a baseline reference flag. |
| **New Credit Accounts Opened (NCAO)** | TransUnion bureau data covering new credit accounts opened across the market, refreshed monthly. The source dataset for the NCAO CICTR report. |
| **Additional Exposure** | TransUnion bureau data covering credit limit increases and further loans on existing accounts. The source dataset for the CLI CICTR report. |
| **CLI (credit limit increase)** | An increase to the limit on an existing account, or a further loan against it, as opposed to a newly opened account. |
| **Manual Enablement** | Manually triggered delivery of the report by Customer Success and Data Science, as opposed to a self-service flow on the platform. |
| **BestMatch** | Omnisient's existing privacy-preserving matching method, used by the pipeline to overlap the CMF against the bureau data. |
| **Universe dataset** | See Before you start. |
| **Neutral cleanroom** | A CICTR neutral project inside the Omnisient CS profile, rather than inside either party's profile, so neither party has visibility of the other's dataset. |
| **Internal / External** | Whether an account sits with the lender client (internal) or another provider (external). Determined by matching the bureau record's Client Reference against the CMF's derived Client_Reference. |
| **Adjacent product** | A credit product other than the one advertised, tracked alongside it. |

## Background

### Why a neutral cleanroom is used

TransUnion was unwilling to share its bureau data directly with the lender client, wanting the client's exposure to that data ring-fenced to the report alone.

### How this differs from the previous process

| | Previous process | Neutral pattern |
|---|---|---|
| Whose profile the project sits in | TransUnion's | Omnisient CS |
| Project's own dataset | NCAO (TransUnion's own) | Universe dataset (returns no matches) |
| How NCAO enters the project | Already there as the own dataset | Shared in by TransUnion |
| How the CMF enters the project | Shared in by the client | Shared in by the client, added manually |
| TransUnion's bureau data exposed to the client | Yes | No |
| Where matching runs | Stored procedure on project creation | On the shared datasets, inside the project |

The matching logic, the CICTR logic and the report output are unchanged. What changes is whose profile the work happens in and what each party can see.

![Matching and CICTR project flows, comparing the previous process in the top row against the neutral pattern in the bottom row. Previous process: the project is created in the TransUnion profile with NCAO as its own dataset and the CMF shared in, matching logic runs via a stored procedure on project creation, then CICTR logic produces the HTML report. Neutral pattern: the project is created in the Omnisient CS profile with the Universe dataset as its own dataset, which returns no matches; NCAO is shared in by TransUnion and the CMF is added manually, matching logic runs on the shared datasets in the project, then CICTR logic produces the HTML report.](images/cictr-neutral-cleanroom-flow.png)

Source diagram: `images/cictr-neutral-cleanroom-flow.drawio`.

## Related

- [Available Datasets](https://help.omnisient.com/en/articles/13638749-available-datasets)
