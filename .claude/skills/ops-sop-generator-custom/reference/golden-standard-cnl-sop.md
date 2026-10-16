# Golden Standard Reference — CNL Approval Process SOP

This is the reference SOP the `/ops-sop-generator-custom` skill is modeled on. It is a real,
shipped SOP for the Company Notebook Library (CNL) approval process, authored alongside the CNL
Shaped Solution PRD.

Read it before drafting to see how the sections actually behave in practice — in particular:

- **Purpose** states scope in two sentences: who owns it, what it covers.
- **Background** names the trigger, the review queue, and the exact aliases work routes to.
- **Workflow Overview** leads with the demo recording, then an ASCII diagram — included here
  because the flow branches into approve/decline.
- **User Declaration** quotes the policy text verbatim. The reviewer is checking against exact
  wording, so it is not summarized.
- **Back Office: Notebook Approvals Screen** is the reference surface — screen path, screenshot,
  column table, available actions — documented before any step so the steps can point at it.
- **Review Process** steps each carry their screenshot inline, and Step 2 spells out the specific
  patterns to look for per check rather than saying "review the notebook."
- **Approval** and **Decline** are separate numbered sections. Decline carries the
  "Writing a good decline reason" guidance with a quoted example — the part that turns a
  step-follower into someone doing the job properly.
- **Escalation** is trigger conditions as bullets, plus what to do with the item in hand.

Do not copy this content into a generated SOP. Copy its shape.

---

# SOP for the CNL Approval Process

## Purpose
This SOP defines how the Data Science team (Customer Success) reviews and actions notebook submissions made through the Company Notebook Library (CNL) promotion workflow. It covers what triggers a submission, how to review it in the Back Office, the criteria for approval or decline, and how to communicate outcomes to requesters.

* * *

## Background
The Company Notebook Library lets Omnisient platform users (including staff and clients) share approved notebooks across their organisation. Any analyst can submit a notebook for inclusion via **Promote to Library** in the Jupyter file browser (in a project context). Before submitting, users must read and confirm a set of declarations (see User Declaration below).

Submitted notebooks enter a review queue managed through the Back Office. Approval requests are routed to **Customer Success (Data Science)** and **Support**. Approved notebooks become available to all users in the requester's company via the Notebook Library panel in Jupyter.

## Workflow Overview
[https://t9012824942.p.clickup-attachments.com/t9012824942/0f3f2bbc-1e0c-4146-82d8-69c2f0c6b87e/Company%20Notebook%20Library%20Demo.webm?view=open](https://t9012824942.p.clickup-attachments.com/t9012824942/0f3f2bbc-1e0c-4146-82d8-69c2f0c6b87e/Company%20Notebook%20Library%20Demo.webm?view=open)

```sql
User submits notebook via "Promote to Library"
        ↓
User confirms declaration in modal
        ↓
Submission logged → notification sent to CS (Data Science) + Support
        ↓
DS reviewer downloads and reviews notebook in Back Office
        ↓
  ┌─────────────┐            ┌─────────────────┐
  │  Approved   │            │    Declined      │
  │ Notebook    │            │ Email to user    │
  │ published   │            │ with reason;     │
  │ to library  │            │ user may resubmit│
  └─────────────┘            └─────────────────┘
```

## User Declaration
Before a notebook is submitted, the user must read and confirm all of the following in the promotion modal.

Promoted notebooks are reviewed by the Omnisient Data Science team before becoming available in the shared library. Submissions are logged against your account. Please read and confirm each of the following before submitting:

**No prohibited data** — To the best of my knowledge, this notebook contains only code. It does not include, embed, or reference any partner data, personal information, derived outputs, or identifying attributes.

**No re-identification attempt** — To the best of my knowledge, this notebook does not contain logic, queries, or techniques designed or likely to re-identify individuals from anonymised or pseudonymised datasets.

**No malicious purpose** — I am not submitting this notebook to exfiltrate data, circumvent access controls, or for any purpose that would harm individuals, partners, or Omnisient's platform.

> **I understand this notebook will be reviewed by the Omnisient Data Science team and may be rejected or flagged if it does not meet the above standards.**

## Back Office: Notebook Approvals Screen
Navigate to **Back Office > Notebook Approvals** to view the review queue.
![](https://t9012824942.p.clickup-attachments.com/t9012824942/6698a5fb-2b73-4eeb-aef5-fe8479cd9001/image.png)
### Table columns

| Column | Description |
| ---| --- |
| Notebook Name | Filename of the submitted `.ipynb` |
| Requester Name | Name of the user who submitted |
| Requester Email | Email of the submitter |
| Company Name | The requester's organisation |
| Project Code | The project from which the notebook was promoted |
| Requested Date | Date the submission was made |
| Status | `Pending Approval` , `Rejected` or `Approved` |

### Actions
For `Pending Approval` submissions only:
*   **Download** — downloads the `.ipynb` for review
*   **⋮ action menu** — opens Approve / Decline options
* * *

## Review Process
### Step 1: Receive an email
This email is sent to:
*   [support@omnisient.com](mailto:support@omnisient.com)
*   [customersuccess@omnisient.com](mailto:customersuccess@omnisient.com) aliases
![](https://t9012824942.p.clickup-attachments.com/t9012824942/0ea790ca-4143-4a39-932a-4964a8acd169/image.png)

Find the request in a `Pending Approval` state with the notebook name surfaced in the email.

### Step 2: Download and review the notebook
Click **Download** and open the file in a local Jupyter environment or notebook viewer. Check against each declaration:

**1\. No prohibited data**
Scan all cells for hardcoded data values, printed outputs, embedded dataframes, or inline results. Check for references to partner datasets, PII fields (names, emails, IDs, phone numbers), or derived scores. A notebook submitted with outputs still present should be declined — users are required to clear all outputs before promoting.

**2\. No re-identification logic**
Look for joins on quasi-identifiers (e.g. age + gender + postcode combinations), statistical inference across multiple attributes, or linkage attacks on anonymised data. Simple analytics and modelling code with no identifying inputs are acceptable.

**3\. No malicious purpose**
Look for data exfiltration patterns: writing files to external paths, HTTP calls to external endpoints, credentials embedded in code, or logic designed to circumvent row-level security.

**4\. Outputs are cleared**

### Step 3: Make a decision
Use the **⋮ action menu** to select **Approve** or **Decline**.

* * *
## Approval
If the notebook passes all four checks:
1. Select **Approve** from the action menu.
2. Status updates to `Approved` in the queue.
3. The notebook is published to the requester's organisation's Company Notebook Library — visible to all users in the Notebook Library panel in Jupyter.
4. The requester receives an email notification confirming approval.

* * *
## Decline

If the notebook fails any check:
1. Select **Decline** from the action menu.
2. Provide a clear, specific reason — this is included in the email sent to the requester.
    1. **Writing a good decline reason:** Be specific about which check failed and what was found (e.g. _"Notebook contains printed dataframe outputs with what appear to be real user records. Please clear all outputs and resubmit."_). If the issue is ambiguous, err toward declining and ask the user to clarify intent before resubmitting.
![](https://t9012824942.p.clickup-attachments.com/t9012824942/8836a92d-9941-4fc3-8503-071598d1a802/image.png)

The requester receives an email with the reason and can address the feedback and resubmit via the same Promote to Library flow.
![](https://t9012824942.p.clickup-attachments.com/t9012824942/428b20d5-7b16-4049-9776-8b8bbab4fa16/image.png)

* * *
## Escalation
Escalate if:
*   A notebook contains what appears to be a genuine re-identification attempt or data exfiltration pattern.
*   A requester resubmits a declined notebook without addressing the stated concern.
*   A submission references or accesses data outside the submitter's project scope.

In these cases, decline the notebook, note the escalation internally, and do not approve further submissions from the same account until reviewed.
