---
title: Company Off-boarding — Standard Operating Procedure
type: sop
source_task: https://app.clickup.com/t/869eyvbef, https://app.clickup.com/t/869erv38p
created: 2026-09-14
---

# Company Off-boarding — Standard Operating Procedure

## 1. Introduction

This SOP covers what happens when a client company terminates its relationship with Omnisient and needs its data removed from the platform — end to end, not just the self-service deletion a client can do on their own.

This SOP formalizes the process the team agreed CPB's off-boarding should have followed from the start: **route to Legal/Risk before Engineering executes any removal beyond a client's own self-service deletion.**

---

## 2. Step-by-Step Guide: Running a Company Off-boarding

### Step 1 — Confirm the trigger
Off-boarding can start from any of:
- A formal termination notice sent to Legal/Sales
- A direct client email

A client's own self-service dataset deletion (Step 3) is not the finish line for a full company off-boarding — treat it as one input, not the whole job.

### Step 2 — Route to Legal/Risk before Engineering touches anything
Flag the request to Legal and Risk immediately, before any backend deletion work starts. Legal reviews:
- The client's contract, MSA/OPLA, cooperation agreements, and any active **Data Trade Agreements** — the terms and conditions attached to a dataset share, which carry their own start/end window (e.g. 1 Sept–30 Sept) independent of the main contract. An active data-share window with a third party can legally block full removal until it expires, depending on how the main agreement links to it.
- Who owns any derived outputs (projects, dashboards, reports) built from the client's data, and whether a third party still needs access to them.
- Any notice obligations owed to third parties who share data with this client.

### Step 3 — Client-side self-service deletion (baseline)
The client (or CS on their behalf) can go into the platform and schedule deletion of the datasets they uploaded. This locks any shares and projects created from that data automatically.

This alone is not sufficient for a full company off-boarding — it locks projects but doesn't remove the underlying data from the warehouse or data lake.

### Step 4 — Engineering executes full removal (once Legal clears it)
Split by owner:

- **Warehouse — Robin Cleland:** drop the client's tables/objects/logic from the SQL warehouse. On-site backups retain deleted data for 7 days and then roll off automatically — no separate cleanup needed there.
- **Datalake / front-end — Werner Hurter:** delete the client's parquet files and datalake objects. Any Power BI reports or other outputs built on that data will break once the source is gone — that's expected, not a bug worth chasing.
- **Client-specific features/pipelines** (if the client had a bespoke product feature, e.g. Basket Score): decommission the dedicated pipeline steps, backend stored procedures, and API infrastructure (UAT/Prod servers, containers, databases) scoped only to that client. Update Intercom/help-center articles and internal docs to state the feature is deactivated/decommissioned, and check for any scheduled job that could silently recreate the client's data/columns (this happened with Basket Score's weekly job and needed a specific fix to prevent recreation).
- **Offsite backups — Ishmael Muteremuka:** do not attempt to purge the client's data out of offsite/AWS daily backups. See "What NOT to worry about" below.

### Step 5 — Third-party notification (if applicable)
If the off-boarding client shared data with another client or partner (e.g. CPB → Shoprite), Legal decides whether that partner needs a heads-up to download outputs before final lockdown. This is a case-by-case legal call — don't notify a third party or promise them a download window without Legal's sign-off on the wording.

### Step 6 — Issue the Data Deletion Certificate
Use the standard certificate template: [Data Deletion Certificate template (SharePoint)](https://omnisient.sharepoint.com/:w:/s/omnisient.com-CoE/IQA2uyNRs2BrRrL33iEcs8mSAbaBbi6UJM_wUqFhHZJhVD4?e=cqHSm0)

Certificate wording must say data was **"cleared"** from live systems — never "purged" or "deleted from all backups" — since offsite backups are retained, not destroyed. Legal reviews and approves final wording before it goes to the client.

---

## 3. Standard Operating Procedure

**As-needed check:** this process only runs when a client formally terminates or requests data removal. There's no recurring or scheduled check — it's entirely event-triggered.

**Escalation:**
- Legal/Risk gatekeeper: Tracey Harris. 
- Engineering execution: Robin Cleland (warehouse), Werner Hurter (datalake/front-end), Ishmael Muteremuka (backups/infra).
- Commercial/coordination lead: [[Aimee_Malan|Aimee Malan]] — owns client communication and ties the workstream together end to end.

**What NOT to worry about:**
- Purging the client's data out of historical offsite/AWS backups. Restoring, deleting, and re-backing-up hundreds of multi-gigabyte daily files isn't feasible at scale, and it isn't required — accepted regulatory practice is that retained backups are fine as long as the data can't re-enter the live platform or be accessed. Don't spin up a second data warehouse to chase this.
- On-site warehouse backups — these age out automatically 7 days after the source data is deleted. No manual cleanup needed.

---

## 4. Open Items / To Confirm

- Whether/how to notify a third-party data-share partner (like Shoprite) is still a case-by-case Legal decision, not yet reduced to a standard rule.
- This SOP is the first formalization of company off-boarding at Omnisient. If a future case surfaces a new edge case (e.g. a client off-boarding mid-way through an active Data Trade Agreement with no linkage to the main contract), route to Legal rather than assuming this SOP already covers it — future OPLAs/contracts are also being updated to state explicitly that data removal is subject to any existing data shares in progress.
