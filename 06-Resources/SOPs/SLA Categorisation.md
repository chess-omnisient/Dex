---
title: SLA Categorisation
type: reference
source_task: Standard OPLA Table 1 (Call Priority & Response Times) and Table 2 (Support Hours), supplied by Chess; SLA management and severity reporting review (https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-80652)
created: 2026-09-29
claude_doc: https://claude.ai/code/artifact/7a7ae57b-f001-4bf7-9022-2c0e259d0bac
---

# SLA Categorisation

**As of:** 2026-09-29
**Related:** [[Support and Incident Process]]

## Purpose and scope

Every support call is assigned one of 4 severity levels when it is logged, and that severity sets the response and resolution time the client is owed. This document defines the 4 levels, the times attached to each, and the hours in which those times apply.

It covers all support calls handled by the support desk. Anything not defined in the source material is listed as an open question at the end rather than assumed.

## Severity levels and response times

Severity is set by business impact at the point of logging. The 4 levels below are the standard OPLA (Omnisient Platform Licence Agreement) terms, and the same levels apply to Freeware licence agreements.

| Severity | Definition | Response time | Resolution time |
| --- | --- | --- | --- |
| Severity 1 | System unavailable. Also covers security vulnerabilities that could compromise the client's infrastructure, systems or data, and data breaches (confidential data copied, viewed, transmitted, stolen or used by someone without authorised access). Raised through an emergency call between the Client Support Manager and Omnisient, where an action plan with roles and responsibilities is agreed. | 1 hour | 8 hours |
| Severity 2 | Business critical. An error stops the user from performing a critical task. | 4 hours | 24 hours |
| Severity 3 | Non-business critical. An error stops the user from performing an important function, but a workaround exists so there is no critical business impact. | 24 hours | 3 working days |
| Severity 4 | Low business impact. Nice-to-haves and small irritations. | 48 hours | 5 working days |

If a client disagrees with the severity assigned to a call, they raise it with their Support Manager. Where service levels are not met, the escalation contacts in the OPLA are [[Sharon]] and [[Anton_Grutzmacher|Anton Grutzmacher]]. Definitions are from the [SLA management and severity reporting review](https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-80652) page in ClickUp; times are from Table 1 of the standard OPLA.

## Support hours

The response and resolution clocks above run within standard support hours. Outside those hours only Severity 1 and Severity 2 are worked, and only where after-hours cover is contracted. After-hours cover is currently contracted for Standard Bank and Shoprite; FNB and AirVantage are in negotiation.

| Period | Times | Days | Severities covered | Type |
| --- | --- | --- | --- | --- |
| Normal hours | 09:00 to 17:00 CAT | Mon to Fri | All (1 to 4) | Standard |
| After hours, critical incidents | 17:00 to 09:00 CAT | Mon to Fri | Severity 1: resolve. Severity 2: resolve, fix may be temporary. | Contracted, at additional cost |
| After hours, critical incidents | All day | Sat and Sun | Severity 1: resolve. Severity 2: resolve, fix may be temporary. | Contracted, at additional cost |

The platform itself is available 24 hours a day, Monday to Sunday, with an expected uptime of 99.9%. The Support Team can be made available 24 x 7 under a separate Service Level Agreement so that Severity 1 issues are resolved immediately. Public holidays are not working days: the 3 and 5 working day resolution times for Severity 3 and 4 exclude them.

Source: Table 2 of the standard OPLA and the support hours section of the [ClickUp SLA review page](https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-80652).

## How to categorise a call

Work down from Severity 1. The first level whose definition fits is the severity, and where two could apply the higher one wins. Severity is assigned at the point of logging in Intercom by the Intercom severity assessor together with the account manager; when the ticket reaches ClickUp, the bug severity assessor runs and adjusts the severity if required.

1. **Judge impact, never channel.** A Severity 1 logged through Intercom chat, email or WhatsApp is still a Severity 1. The bug severity assessor re-checks the level once the ticket is in ClickUp, but the first assignment in Intercom is on impact.
2. **Security and data exposure are Severity 1.** A vulnerability that could compromise client infrastructure, systems or data counts whether or not it has been exploited. A possible unauthorised data export is checked against the data breach definition, never filed as Severity 2.
3. **Escalation is a priority signal, not a severity signal.** A client escalating a call does not move it up a level. Track urgency separately as high, medium or low.
4. **Severity 2 versus 3 turns on the workaround.** A critical task blocked with no way round is Severity 2. An important function blocked, with the work still possible another way, is Severity 3.
5. **Severity 4 is user-facing low impact.** Internal, automated or cosmetic bugs with no user impact carry no client SLA and need a separate internal-only tag.
6. **Record the environment.** A bug from DEV or UAT is tagged DEV or UAT instead of a severity.

| Call as reported | Severity | Why |
| --- | --- | --- |
| Bank cannot reach the platform, logged via Intercom chat | 1 | System unavailable. Channel does not matter. |
| Online scoring API down | 1 | A client-facing component is unavailable. |
| Possible unauthorised export of client data identified | 1 | Data exposure is Severity 1 even before it is confirmed. |
| User cannot complete a critical task, no workaround, account manager escalates | 2 | Critical task blocked. Escalation does not change the level. |
| Important function fails but the user can finish the work another way | 3 | Workaround exists, no critical business impact. |
| Small cosmetic irritation or nice-to-have | 4 | Low business impact. |
| Automated bug found in UAT, no user affected | DEV/UAT tag, no client SLA | Not a client-facing call. |

Rules and examples are drawn from the severity rules and the differences table on the [ClickUp SLA review page](https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-80652).

## Clients on an API SLA

Clients whose contracts carry a separate API SLA are categorised on different definitions and hours, and a service credit of up to 20% of the monthly API fee is payable if availability falls below 99.5% in a calendar month. The API SLA is currently contracted for Standard Bank; FNB and AirVantage are in negotiation. Each call for these clients must be tagged as API at source so the right terms apply.

| Severity | API SLA definition | Response time | Resolution |
| --- | --- | --- | --- |
| 1 | Critical problem with availability or multiple fundamental functions that precludes productive use and has, or is likely to have, immediate and material impact on a critical business activity. Must be reported by telephone. | 1 hour | Worked 24 x 7 x 365 until resolved or a workaround is provided |
| 2 | Significant functionality problem or degraded availability that does not preclude productive use and does not materially impact a critical business activity. Must be reported by telephone. | 4 hours | Worked by dedicated resources during business hours until resolved |
| 3 | Inconvenient problem that inhibits a feature but does not preclude productive use. | 1 business day | Worked primarily during business hours |
| 4 | General questions, service requests, minor or cosmetic errors, or enhancement requests. | 2 business days | Worked primarily during business hours |

Support hours under the API SLA are 07:00 to 22:00 CAT, Monday to Sunday including public holidays, covering all 4 severities. After-hours cover is baseline rather than a paid add-on. Scheduled maintenance runs Sunday 22:00 to Monday 07:00 CAT. Severity 1 and 2 incidents can be logged at any time by emailing support@omnisient.com, with telephone escalation to the Account Manager or after-hours contact.

Severity 1, 2 and 3 incidents affecting an API SLA client need a post incident review within 3 business days. Severity 1 and 2 also need a root cause analysis report once the cause and remediation are clear. Terms are from section 4 of the [ClickUp SLA review page](https://app.clickup.com/9012824942/v/dc/8ck9jve-112572/8ck9jve-80652).

## Open questions

These are gaps the source material leaves open. Each needs a decision before the categorisation can be applied consistently.

- [ ] When does the Platform versus API tag go live in Intercom and ClickUp? Without it the API SLA terms cannot be applied per call.
- [ ] Do the standard OPLA "24 hours" and "48 hours" response times for Severity 3 and 4 run through weekends? The API SLA uses business days instead.
- [ ] Does a temporary Severity 2 fix delivered after hours stop the resolution clock, or does the clock run until the permanent fix?
