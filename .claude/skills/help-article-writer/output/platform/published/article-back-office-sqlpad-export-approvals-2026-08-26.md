---
title: Back Office: SQLPad Export Approvals
status: draft
author: chess@omnisient.com
created: 2026-08-26
collection: Back Office
collection_note: "'Back Office' isn't in article-information-architecture.md's documented Collection table (Getting Started, Datasets, Uploading Data, Projects, Audience Selections and Activations, Analytics and Modelling, Omnisient Platform/Web App, Admin and Settings, Trust Center, Contact Omnisient). It's a real, established Intercom collection (parent_id 19703896) with 4 sibling articles: Back Office: Reports, Back Office: Companies, Back Office: Users Admin, Back Office: PII Leaks. Flagging per the doc's own guidance rather than reclassifying — worth adding to the taxonomy doc as a deliberate decision, not silently absorbing into Analytics and Modelling."
article_shape: standalone
intercom_article_id: 16391390
intercom_url: https://help.omnisient.com/en/articles/16391390-back-office-sqlpad-export-approvals
revision_type: formatting-only, no functionality change
draft_article_id: 16644245
draft_pushed: 2026-08-26
---

**Back Office → SQLPad Approvals** is where you review SQLPad export requests before they're released to the requesting partner. Every export requires two sign-offs before release: approval from the data owner, followed by a review here.

<div style="background-color:#feedaf80; border:1px solid #fbc91633; padding: 8px;">
🔐 <b>Permissions:</b> Access to Back Office is restricted to staff only.
</div>

## Where to Find It

In the Omnisient Platform, go to **Back Office → SQLPad Approvals**.

> 🖼️ *Existing screenshot — carries over unchanged.*
> **Alt text:** "Back Office menu with SQLPad Approvals selected in the platform sidebar."

<div style="background-color:#e3e7fa80; border:1px solid #6366f133; padding: 8px;">
💡 <b>Two checks, not one:</b> Every SQLPad export requires sign-off from the data owner first (see <a href="https://help.omnisient.com/en/articles/15968482-approvals">Approvals</a>), followed by a review here by Omnisient. Both have to clear before the export is released.
</div>

## How the SQLPad Approvals List Works

| Column | What it shows |
|---|---|
| **Export Name** | The name of the requested export |
| **Requested By** | The partner who requested the export |
| **Collaboration Partners** | The other companies whose data feeds the export, and whose data owners need to approve it |
| **Approvals** | How many of the required data owners have approved so far, as a fraction (e.g. "1/2 Approved") |
| **Record Count** | The number of records the export contains |
| **Requested Date** | When the request was submitted |
| **Status** | Where the request stands (see below) |
| **Actions** | **Review** for requests awaiting approval, **View** for requests already reviewed |

### Status Meanings

| Status | What it means |
|---|---|
| **Awaiting Approval** | The request hasn't been reviewed by Omnisient staff yet |
| **Reviewed** | An Omnisient staff member has accepted the request, and it has moved into SQL Exports |
| **Locked** | The export has expired, or the underlying project has locked, for example due to a dataset share expiry |
| **Rejected** | An Omnisient staff member has rejected the request, giving a reason; the requester has received a detailed email including it |

In the platform, the list looks like this:

> 🖼️ *Existing screenshot — carries over unchanged.*
> **Alt text:** "SQLPad Approvals list showing export name, requester, collaboration partners, approval count, record count, requested date, and status."

## Request Review

The review screen breaks the request into three sections.

### SQLPad Query

The exact query the requestor ran to generate the export.

### Sample of Records

A random sample of five rows from the exported dataset, so you can catch anything before it goes out. Different identifiers carry different levels of risk depending on what's exposed; use this as a reference when judging whether an export is safe to release:

| Identifier | What it exposes if misused | Severity |
|---|---|---|
| **DW Keys** (the identifier columns you'll see in the query above, e.g. `DW_ID_KEY`, `DW_EMAIL_1_KEY`) | Can link rows across datasets to build user profiles, or act as a pivot point into richer records if combined with other exposed fields | Low → Medium (higher if linked to PII-rich records) |
| **SKEYS** (secondary or surrogate keys used in joins) | Can reconstruct relationships between tables, track behavior across time and systems, or enable cross-account correlation for de-anonymization | Low (rarely identifying alone, but enabling when combined with other data) |
| **Customer ID / iURN** | Can enable account takeover attempts, targeted social engineering, or lookups into payment and invoice records elsewhere. iURNs are just row numbers and aren't inherently linked to personal information; see [What is an iURN?](https://help.omnisient.com/en/articles/11967353-what-is-an-iurn) | Low |
| **PII / Hash** (names, ID numbers, emails, phone numbers, and their hashes) | Raw PII enables direct identity theft, phishing, and targeted fraud. Hashed PII can be broken through brute-force attacks or rainbow tables, especially where the hashing is weak (unsalted or fast). Hashed PII combined with other exposed fields can also be re-identified | Critical (raw PII). High → Critical (weakly hashed PII) |

<div style="background-color:#e3e7fa80; border:1px solid #6366f133; padding: 8px;">
💡 <b>Judge fields together, not in isolation:</b> A single field often isn't enough to identify someone on its own; a name alone, for example, is rarely a strong risk. Combined with other fields like surname, age, or gender, it can quickly build a solid identification. Judge exposure by what's exposed together, not by a single column.
</div>

👉 See [Up-Skilling Guide: How to Assess SQLPad Exports with Confidence](https://help.omnisient.com/en/articles/13230382-up-skilling-guide-how-to-assess-sqlpad-exports-with-confidence) for more on reading Sample of Records with confidence.

### Included Datasets

Every dataset that went into the export, with its owner and upload details.

A panel on the right, **Additional Details**, shows:

- **Project Code** and **Project Type**: which project the export belongs to
- **Collaboration Partners**: whose data contributed to the export
- **Requested By** and **Requestor Email**: who asked for it
- **Requested Date** and **Expiry Date**

The full review screen looks like this:

> 🖼️ **Image suggestion (Orient):** Shows the full review screen — SQLPad Query, Sample of Records, Included Datasets, and the Additional Details panel — laid out together with the Accept/Reject actions. Without this image, the reader would have to mentally assemble the screen's layout from three separate subsections with no sense of how they sit relative to each other or to the Accept/Reject buttons.
> - **Type:** Screenshot
> - **Alt text:** "SQLPad export review screen showing the query, sample of records, included datasets panel, and Accept/Reject actions."
> - **Filename:** `sqlpad-export-review-screen.png`
> - Capture from dummy/sandboxed data — never real platform data. This is the one gap left by the source revision: the live article's `<img>` for this screen is missing from the Intercom source entirely, not just outdated.

From here, select **Accept** or **Reject**.

| Action | What happens |
|---|---|
| **Accept** | The request moves into SQL Exports |
| **Reject** | You'll be asked to enter a reason. Be specific here, as the requester receives a detailed email including it |

<div style="background-color:#feedaf80; border:1px solid #fbc91633; padding: 8px;">
⚠️ <b>This review is a second check, not the only one.</b> The data owner carries primary responsibility for catching anything suspicious or misleading in an export. Masked data can look harmless while still representing real, identifiable people. This review adds a second, independent check on top of that approval.
</div>
