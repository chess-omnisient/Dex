---
title: Support and Incident Process – Standard Operating Procedure
type: sop
source_task: supportIncidentProcessFlow.drawio.pdf (as-is and future-state process maps); Severity Classification Guide for Support (https://app.clickup.com/9012824942/v/dc/8ck9jve-193532); Support process ClickUp doc incl. SLA management and severity reporting review (https://app.clickup.com/9012824942/v/dc/8ck9jve-112572); other ClickUp pages linked in section 7
created: 2026-09-29
---

# Support and Incident Process – Standard Operating Procedure

## 1. Introduction

This SOP describes how a client issue moves from first contact to closure at Omnisient: the channels a client or colleague can use, how Support turns an Intercom conversation into a categorised, severity-rated ticket, how that ticket is routed into ClickUp, how Engineering investigates and closes it, and when a Sev 1 issue escalates into the formal incident management process.

The routed process (ticket categories, the live toll-free line, separate ClickUp boards per category) went live in 2026 and replaced the earlier flow where every ticket landed on a single Bug Board as Sev 3. Where a gap from the old flow still applies, it's called out in the relevant step. WhatsApp is outstanding.

**Audience:** account managers and engineers. Account managers own the client-facing side (intake, severity, client comms, closure). Engineers own the ClickUp side (secondary review, investigation, mitigation, permanent fix).

**Support hours:** the Support Desk runs 09:00 to 17:00 CAT, Monday to Friday, under the standard OPLA (Omnisient Platform Licence Agreement). After-hours cover (17:00 to 09:00 CAT on weekdays, all day Saturday and Sunday) is contracted at additional cost and covers Sev 1 and Sev 2 resolution only, where the Sev 2 fix may be temporary. Clients on an API SLA are covered 07:00 to 22:00 CAT, Monday to Sunday including public holidays, as baseline. See section 2, step 4 for what that changes. Team-internal comms run on MS Teams and ClickUp; the Slack integration was removed in May 2026.

**Training:** Run by the CoE (Centre of Excellence) for account managers and engineers.

---

## 2. Step-by-Step Guide: How a Ticket Gets In

### Step 1 – Know the channels

Which channel the client uses decides who creates the ticket.

| Channel | Who creates the ticket |
| --- | --- |
| Email to support@omnisient.com or supportamericas@omnisient.com | Creates a conversation in Intercom. Support sets severity and converts it to a ticket. |
| Escalation email to clientsupport@omnisient.com | Same as above. |
| Omnisient platform (Contact Support, Report a Problem, Request a Feature) | The client creates the ticket directly. Support receives an email notification of every client-created ticket. |
| Chatbot (Intercom Messenger) | The client creates the ticket directly, same as above. |
| Toll-free line 0800 001 4686 (given to API SLA clients, e.g. Standard Bank) | Routes to [[Sharon]] on her mobile. If unanswered, the caller hears a recorded message asking for their issue and contact details; the voicemail and a transcript are emailed to support@omnisient.com. Support creates the ticket on the client's behalf using context from the call. Portal access and voicemail handling: [SA support toll-free number](https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-139772). |
| Omnisient Business WhatsApp profile | Support creates the ticket on the client's behalf using context from the WhatsApp exchange. |

Internal Omnisient stakeholders don't use these channels. They log issues via the **Intake Console on ClickUp**, choosing Technical issue / bug or Feature request. Data science queries go through the **DS intake form**. This is also the route the Omnisient team follows when logging a ticket on a client's behalf.

### Step 2 – What each in-platform option does

| Option | Where it goes |
| --- | --- |
| Help & Getting Started (sidebar) | Help Center at https://help.omnisient.com/ |
| Give Feedback (sidebar and drop-down) | Triggered survey. Submissions notify product@omnisient.com via a workflow trigger. |
| Request a Feature (drop-down) | Creates an Intercom ticket routed to the appropriate ClickUp board. Submissions notify product@omnisient.com via a workflow trigger. |
| Contact Support (drop-down) | Panel to populate details, routed to support@omnisient.com. |
| Report a Problem (drop-down) | Routed to the chatbot. The chatbot asks what the problem is, then creates a Bug, Feedback Request or Client Support ticket assigned to Omnisient Support, or a Data Science ticket assigned to Customer Success. |

### Step 3 – Classify the ticket

When converting an Intercom conversation to a ticket, pick one of four categories. The category decides the allowed severity range and which ClickUp board the ticket lands on.

| Category | Use it when | Severity range | ClickUp destination |
| --- | --- | --- | --- |
| Technical issue / bug | The platform isn't functioning as intended: errors, failures, performance issues, outages, data not processing or displaying correctly. Anything the client believes is broken, regardless of root cause. Not for how-to questions or feature requests. | Sev 1 to 4 | Bug Board |
| Platform feature request | New functionality or an improvement to an existing feature. Not for defects or how-to questions. | Sev 4 | Intake Console form |
| Platform support query | The platform works as designed but the user needs help: how-do-I questions, configuration, access or permissions, clarification on expected behaviour. | Sev 3 to 4 | Platform Support list |
| Data science query | Models, outputs, data logic, methodology or DS-led engagements. Needs the Data Science team, not platform engineering. | No severity | Customer Success sprint folder |

### Step 4 – Set severity before converting to a ticket

Every Intercom ticket defaults to Sev 3. Assess and set severity before you convert; don't leave the default. Severity drives SLA response and resolution windows and contractual obligations.

| Severity | Description | Examples |
| --- | --- | --- |
| Sev 1 | System or any production component is unavailable. A security vulnerability that could compromise client infrastructure, systems or data (exploited or not). A data breach has occurred. Online scoring APIs are down. | Platform completely inaccessible. Hydration failure affecting all users in a region. Client reports unauthorised access to their data. Standard Bank API returning errors across all endpoints. |
| Sev 2 | An error prevents a user from performing a critical task, no viable workaround, blocks a key business process. | Client can't upload via Desktop Connect and there's no alternative. A project share is failing and blocking a time-sensitive deliverable. Client can't run a scheduled batch job. |
| Sev 3 | An error prevents an important function but a workaround exists and the client isn't fully blocked. No critical business impact. | Report loads slowly but data is accessible. A filter is broken but the task can be completed another way. Dataset update date not refreshing. Project Generation Failed. Upload hydration failure. Datalake and Datawarehouse mismatches. OmniCheck. Desktop Connect. |
| Sev 4 | Low business impact: nice-to-have fixes, small irritations, cosmetic issues. | Misspelled UI label. Missing or wrong tooltip. Minor layout issue with no functional impact. |

**Quick decision flow:**

1. Is the system or a production component completely down for the client? → Sev 1
2. Is there a security concern or potential data breach? → Sev 1
3. Is the client blocked from critical work with no workaround? → Sev 2
4. Is the client impacted but has a workaround? → Sev 3
5. Is it a minor irritation with no real business impact? → Sev 4

When in doubt, go one level higher. It's easier to downgrade than to explain a missed SLA.

**SLA targets under the standard OPLA:**

| Severity | OPLA call type | Response | Resolution |
| --- | --- | --- | --- |
| Sev 1 | System unavailable | 1 hour | 8 hours |
| Sev 2 | Business critical calls (no viable workaround) | 4 hours | 24 hours |
| Sev 3 | Non-business critical calls (workaround exists) | 24 hours | 3 business days |
| Sev 4 | Low business impact calls | 48 hours | 5 business days |

Response means an Omnisient representative has acknowledged the report to the client by phone or email and assigned a severity. Both timers count: time to first response and time to resolution (tied to the ClickUp close date).

**Clients on an API SLA** (Standard Bank today, FNB in future) carry stricter terms with service credits on breach:

| Severity | API SLA response | API SLA resolution |
| --- | --- | --- |
| Sev 1 | 1 hour. Must be reported by telephone. | Worked 24x7x365 until resolved or a workaround is provided. |
| Sev 2 | 4 hours. Must be reported by telephone. | Worked by dedicated resources during business hours until resolved. |
| Sev 3 | 1 business day | Worked primarily during business hours. |
| Sev 4 | 2 business days | Worked primarily during business hours. |

- Service hours: 07:00 to 22:00 CAT, Monday to Sunday including public holidays, across production and testing environments. After-hours cover is baseline for these clients, not an add-on.
- Scheduled maintenance window: Sunday 22:00 to Monday 07:00 CAT. Releases and patching go here.
- Availability commitment: 99.5% per calendar month, excluding scheduled maintenance. Below that, a credit of 5% to 20% of the monthly API fee is deducted from the next invoice, but only once the target has been missed for 2 consecutive months.
- Sev 1 and Sev 2 API incidents can be logged at any time, including after hours, weekends and public holidays, by emailing support@omnisient.com to get a ticket number, then escalating by telephone to the account manager or after-hours contact.
- Exclusions: time the client spends investigating its own systems, client network or system faults, scheduled maintenance, and emergency changes don't count against the SLA.

**Platform vs API.** Some clients (Standard Bank, and FNB in future) have separate API SLAs with stricter resolution times and service credits payable on breach. For every ticket, decide which it is:

- **Platform:** the Omnisient web application (UI, projects, data uploads via Desktop or Server Connect, reports, user management).
- **API:** online scoring APIs, batch data APIs, or any programmatic interface a client's systems call directly.

API issues at Sev 1 or Sev 2 carry service credit exposure. Flag these immediately in the Production Issues channel and tag Werner.

**Pitfalls:**

- Don't classify by channel. A Sev 1 is a Sev 1 whether it came by email, chatbot or phone.
- Don't confuse an escalation with a severity change. A frustrated client chasing doesn't make something a Sev 2. Reassess the technical impact.
- Don't leave severity unset.

### Step 5 – Convert and notify

1. Set the severity in Intercom.
2. Convert the conversation to a ticket. This triggers the Azure Function that creates the ClickUp task, routed to the board for that category, with a unique reference number (for example BUS-14948). The client receives an email confirming the ticket has been logged.
3. **Sev 1 and Sev 2:** post immediately in the Production Issues channel with the ticket link, client name and a one-line summary of the impact.
4. **Sev 1:** also notify Werner directly.
5. **Sev 1:** send the EXCO leadership notification once root cause and a containment position are known, using the [Sev 1 Incident Email Template](Sev%201%20Incident%20Email%20Template.md). Send a closure note on the same thread when the fix is verified.
6. If severity needs to change after investigation, update it in ClickUp. The Bug Severity Classifier agent won't override a severity a person has set.

---

## 3. Step-by-Step Guide: Handling the Ticket in ClickUp

### Step 1 – Automatic alert

Notice of the logged ticket is flagged in the relevant ClickUp channel as an automatic alert for the team that owns that board.

### Step 2 – Bug Board only: dedupe and secondary review

1. An agent dedupes incoming bug tickets (a repurposed Bug Severity Classifier).
2. The Engineering team (Lebogang, Werner or Robin) performs a secondary review and decides whether the issue is **client-facing**.

### Step 3 – Client-facing bugs (Sev 1 to 3)

1. *Ticket investigated.* A squad member picks it up ahead of current sprint work.
2. *Ticket mitigated.* The client is unblocked. This may be a quick fix or hotfix, not necessarily the permanent fix.
3. If it was a quick fix, create a **user story for the permanent bug fix**.
4. Mark the ticket **closed / done** in ClickUp.

### Step 4 – Everything else (Sev 4 bugs, Intake Console, Platform Support list, Customer Success sprint list)

1. Bugs sit in *Ticket awaiting investigation* until a squad member is available. Other boards go straight to approval.
2. CTO/HODs decide whether the item enters the current sprint.
3. **Accepted:** mark *to-do*, work it in the sprint, then closed / done.
4. **Rejected:** the ticket stays on its board and is assigned to the next sprint, where it re-enters the approval step.

### Step 5 – Close the loop with the client

1. Once the ticket is closed / done in ClickUp, Support emails the client that the ticket is resolved.
2. The client confirms everything is in order.
3. Support **manually closes the ticket in Intercom**. ClickUp closures don't close Intercom tickets and vice versa; there's no two-way sync.
4. Addressed tickets are included in the Omnisient team ClickUp channel notification at month-end release.

An SLA monitoring dashboard tracks tickets from logging through to closure.

---

## 4. Step-by-Step Guide: Incident Management (Sev 1)

This runs alongside the ticket process and is governed by the Omnisient incident management policy.

### Step 1 – Classify

Is this a **suspected platform down, data or security breach, or API down**?

- **No (Sev 2 to 4):** handle through the ticket process in sections 2 and 3.
- **Yes (Sev 1):** continue.

### Step 2 – Management

1. **Activate the Incident Response Team.** Default members: CTO, COO and the Incident Response Lead (assigned by the CTO). The CTO convenes an incident review with the relevant stakeholders immediately on formal declaration.
2. Stakeholder comms.
3. Emergency action plan.
4. The account manager shares the **PIR (post-incident review) report** with affected clients.

### Step 3 – Recovery

1. Recovery plan.
2. Corrective actions.
3. Impact assessment.
4. Incident report. Once the Incident Manager declares the incident resolved, the report is compiled and circulated among the response team for comment. It contains:
   1. Incident background
   2. Incident summary
   3. Description of the process that led to the incident
   4. Individuals involved
   5. Root cause analysis
   6. Impact assessment
   7. Immediate and corrective actions taken
   8. Remediation
   9. Supporting evidence

### Step 4 – Post-incident

1. Post-incident review, incident risk, business impact.
2. Final report approval and recommendations.
3. Stakeholder feedback.
4. Report housed in the **Incident Management folder on SharePoint**.
5. The account manager shares the **final RCA (root cause analysis) report** with affected clients. Engineers write the RCA using the [RCA Template](RCA%20Template.md).
6. The ARC is informed of the incident and mitigating actions taken (3 meetings a year).

**PIR and RCA timing (from the policy):**

- A PIR and RCA are required for any Sev 1, 2 or 3 issue impacting clients.
- The PIR is due 3 business days after the incident: what occurred, start time, reported time, resolved time, and actions to prevent recurrence. It's augmented if new information comes to light.
- The RCA goes to the client once the root cause is identified and remediation requirements are clear. Write it from the [RCA Template](RCA%20Template.md) (incident summary, timeline, problem statement, root cause, impact, corrective and preventative actions, lessons learned, verification). For API SLA clients the RCA must cover an executive summary, a detailed breakdown of the incident, and short, medium and long-term remediation actions.

**Security vulnerability remediation timelines (API SLA):** the client can set deadlines for fixes to vulnerabilities found in the service.

| Rating | Remediation timeline |
| --- | --- |
| Critical | 30 calendar days |
| High | 60 calendar days |
| Medium | 60 to 120 calendar days, or accept the vulnerability if it poses no threat |
| Low | 120+ calendar days, or accept the vulnerability if it poses no threat |

**Monthly service review (API SLA clients):** the account manager and client review performance against service levels and any incidents for the month, and agree the service credit applicable, if any. Typical agenda: service reports, API service levels for the month, tickets and incidents for the period, process changes, major system changes (upgrades, disaster recovery), highlights and upcoming events. Sales reports monthly to clients on SLA performance, so the ticket-level timers in section 2 must be kept accurate.

---

## 5. Standard Operating Procedure

**Account managers, per ticket:**

1. Set category and severity in Intercom before converting. Decide Platform vs API.
2. Convert to a ticket. Confirm it appears on the right ClickUp board with a reference number.
3. Sev 1 or 2: post in the Production Issues channel (ticket link, client, one-line impact). Sev 1: also notify Werner directly.
4. Sev 1 that's a platform outage, breach or API outage: follow section 4, don't wait on the Bug Board.
5. On closed / done: email the client, get confirmation, close the Intercom ticket manually.
6. API SLA clients, monthly: prepare the SLA report (uptime, response time, resolution time, ticket detail, credits payable) and run the service review meeting.

**Engineers, per ticket:**

1. Bug Board: secondary review, decide client-facing yes/no.
2. Client-facing: investigate and mitigate now, create the permanent-fix user story, close.
3. Not client-facing: leave in awaiting investigation until capacity, then take to CTO/HODs for a sprint decision.
4. If you change severity after investigation, update ClickUp and tell Support so the client comms match.
5. Sev 1 to 3 and client-impacting: write the RCA from the [RCA Template](RCA%20Template.md) once the root cause is known, and hand it to the account manager.

**Escalation:**

- Sev 1 or 2, and any API issue at Sev 1 or 2: Production Issues channel plus Werner.
- Sev 1 incidents: Incident Response Team (CTO, COO, Incident Response Lead). The account manager owns PIR and RCA comms to the client.
- Sev 4 sprint entry: CTO/HODs. Don't promise the client a sprint slot before that decision.
- If [[Sharon]] is unavailable, Jacques covers Support triage and the toll-free line. If voicemails on the toll-free line go unanswered for an extended period, flag [[Aimee_Malan|Aimee]] (Head: Centre of Excellence) so cover can be arranged.
- If service levels are not met on a ticket, the OPLA escalation procedure applies: first [[Sharon]], then [[Anton_Grutzmacher|Anton]].
- SQLPad query issues after the custom and LAL project table change (April 2026): follow the [Support guide for custom and LAL project issues](https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-79832). Jupyter cases and column-access scenarios go to Customer Success or the account team, never resolved on the spot.
- If a client disagrees with the severity: per the OPLA, they raise it with the support manager. Acknowledge, document it in the ticket, and escalate to the support lead for a joint reassessment.

**What NOT to worry about:**

- Which channel a ticket came through. Severity is about impact, not route.
- The Bug Severity Classifier overriding your severity. It won't if a person set one.
- Closing a ClickUp ticket closing the Intercom one. It won't, so the manual Intercom close is always a step.

---

## 6. Open Items / To Confirm

- **Routing work loose ends** (from the DoR, June 2026): final OPLA severity mapping sign-off for the Bug Classifier; whether severity is required for non-bug categories.
- **SLA review action items** (from the SLA management review, mid-2026), status unknown: rewrite the Bug Severity Classifier rules to be impact-based rather than channel-based; add a Platform vs API tag at source in Intercom and as a ClickUp custom field; audit live contracts to list every client on an API SLA and their terms; stand up the monthly SLA dashboard fed from Intercom, ClickUp and uptime monitoring; notify Engineering of the API maintenance window.

---

## 7. Supporting Links

- [Severity Classification Guide for Support](https://app.clickup.com/9012824942/v/dc/8ck9jve-193532)
- [SLA management and severity reporting review](https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-80652): OPLA and API SLA terms, service credits, classifier gap analysis
- [SA support toll-free number](https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-139772): portal access and voicemail SOP
- [Support guide: custom and LAL project issues](https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-79832)
- [Record of changes on Intercom](https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-92332)
- [Support process](https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-82372): holds the July 2026 process diagram source file
- [Ticket routing into ClickUp workspaces](https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-91112)
- [Product Brief: Intercom → ClickUp Workspace Routing](https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-94892)
- [Intercom Ticket → ClickUp Workspace Routing (DoR)](https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-100012)
- [Bug process mapping](https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-81512)
- [As-is process whiteboard](https://app.clickup.com/9012824942/whiteboards/8ck9jve-44512)
- [RCA Template](RCA%20Template.md)
- [Sev 1 Incident Email Template](Sev%201%20Incident%20Email%20Template.md)
- Source process maps: supportIncidentProcessFlow.drawio.pdf
