---
title: Sev 1 Incident Email Template
type: template
created: 2026-10-15
---

# Sev 1 Incident Email Template

The internal notification email sent to EXCO leadership when a Sev 1 is raised. Sent by the Centre of Excellence as soon as root cause and a containment position are known, rather than waiting for the incident to close. The fuller postmortem follows as an incident report PDF (see `/incident-report`).

Based on the email sent for ClickUp 869fh1xwr, "Jupyter Notebook contents reachable outside the platform," 14 October 2026.

## How it works

Four headed sections after an opening paragraph: **Root cause**, **Exposure**, **Containment**, **Permanent fix**. Each is short, two to five sentences. No bullets, no severity tables, no timeline; those live in the incident report. Headings are plain text on their own line, not bold or numbered.

The opening paragraph names who flagged it, when, how they found it, and what they found, in one or two sentences. Tag the finder with `@`.

Tag every named owner with `@` so they are pulled into the thread. Name people against the specific control they own rather than listing them generally.

## Rules that matter

**Say what is provable, not what is reassuring.** "We have not received any client reports" is supportable. "No client was affected" usually is not, unless someone actually established it. If nobody has determined whether anyone outside found the issue, do not imply they have not.

**State the environment plainly.** If a fix is live in DEV only, the email says DEV only. Leadership reading "fixed" when it means "fixed in one environment" is the failure this format exists to prevent.

**Separate containment from the real fix.** The Containment section covers what stops the bleeding now; Permanent fix covers the controls that actually close it, with owners. If containment is partial, say so in the Permanent fix section.

**Name superseded approaches when the record changed.** If an initial proposed fix was ruled out on investigation, say it was and why. It protects you when someone asks why the approach changed.

**Keep the client-impact line in Exposure,** together with the bound on what access the flaw did and did not reach.

**No em dashes.** Comma, colon, semicolon or parentheses instead.

Close by committing to further updates and linking the ticket.

---

Subject: Sev 1 | <one-line description of what is exposed or broken> | <ClickUp ticket id>

Hi all,

@<Name> flagged a Sev 1 <when>. <How it was found, in a clause>, he/they found that <what happens, in plain terms>.

Root cause
<What the underlying cause actually is, technically but without jargon a non-engineer would stumble on.> <Whether this is a new defect or long-standing default behaviour.> It is Sev 1 because <the reason the severity is justified>, and it affects <scope: who and where>.

Exposure
<What the flaw reaches, and the bound on it: what it does NOT reach.> We have not received any client reports of this issue and are handling it internally for now. Exploiting it requires <what it actually takes>, rather than being reachable through "ordinary use".

Containment
<What was applied, and why that approach was chosen over alternatives.> <If an earlier attempt failed or was bypassed, say so and what changed.> <What is verified working, and what still works normally for users.>

The <fix/rule> is live and verified in <environment> only. We are rolling it out in stages: <next environment> next, then <subsequent>, checking <what is monitored> after each step.

Permanent fix
The <containment measure> is a containment measure, not the complete fix. The primary controls are still in progress: <control one> (@<Owner>) and <control two> (@<Owner>).

We will keep you posted on progress via email; alternatively, you can follow along in the bug ticket thread here.

Kind regards,
<Name>
