---
name: shoprite-release-notes-custom
description: Produce a clean, client-facing summary of platform and data product work delivered each sprint that is relevant to Shoprite. Pulls from ClickUp sprint boards and Intercom-confirmed bug fixes, filters out anything client-sensitive or irrelevant, and drafts the SRX Sprint Release Summary for account team distribution.
---

# Shoprite Release Notes (SRX)

**Owner:** Product Development / CoE
**Cadence:** End of each sprint, before client delivery
**Audience:** Shoprite account team, then Shoprite directly (via email)
**Tone:** Plain-English, client-facing. No jargon, no ticket links, no internal detail.

Produces the sprint's client-facing release summary for Shoprite. Only include what a Shoprite user or stakeholder would actually notice or care about. Filter out everything internal.

---

## Step 1: Get the Sprint

Ask the user:

```
Which sprint is this for, and what's the date range?
(e.g. Sprint 7, 14 July – 28 July 2026)

Also, I need the link to the published Help Center release notes for this
period (e.g. https://help.omnisient.com/en/articles/XXXXX-release-notes-month-year).
This is required before I can finalize the draft. If the article genuinely
doesn't exist yet for this period, tell me that explicitly and I'll note it
in the draft instead of skipping the check silently.
```

Store as `{sprint}`, `{period}`, and `{help_center_url}` (may be empty).

**Hard requirement:** the draft cannot be finalized (Step 6 onward) until one of these is true:
- `{help_center_url}` is provided, or
- the user has explicitly confirmed the article doesn't exist yet for this period.

"I don't have it right now," silence, or changing the subject is not confirmation. Keep the request open (re-ask at Step 5) rather than assuming and moving on.

---

## Step 2: Pull Tickets from the Platform Sprint Board

1. Open the Platform Squad sprint board in ClickUp (`clickup_get_list` / `clickup_filter_tasks`) and filter for `{sprint}`.
2. Filter by status: **Closed / Done** only.
3. Scan each ticket and decide relevance to Shoprite:
   - **Include:** tagged `shoprite`, `srx`, or linked to a Shoprite-specific epic
   - **Include:** shared platform features that affect all clients (UX, stability, exports, activations), even if not Shoprite-tagged
   - **Exclude:** back-office only or purely internal tickets
4. Group the included tickets by product area for now (final headings come from the reference list at the bottom).

---

## Step 3: Check the Data Product Board

1. Open the Data Product Squad sprint board in ClickUp, filtered for `{period}`.
2. Look for Shoprite-specific data deliverables: new datasets, table builds, automations, QA runs, dedup migrations, feed changes, or data products built on Shoprite data.
3. Add relevant items under **Shoprite Data Feed**, or a standalone **Data Products** section if there are several.

---

## Step 4: Check Bugs Raised by Shoprite via Intercom

1. Open the Bugs board in ClickUp, filtered for tickets linked to Intercom conversations from Shoprite.
2. For each candidate bug, confirm **both**:
   - ClickUp status is **Resolved** or **Closed** within `{sprint}`'s time period.
   - The linked Intercom conversation (`search_conversations`, `get_conversation`) shows the client confirming the issue is fixed. If Intercom doesn't make this clear, ask the user to confirm with account management before including it.
3. Include only confirmed bugs, under **Platform Stability & Reliability**.
4. Exclude:
   - Bugs resolved internally but not yet confirmed by the client
   - Bugs from other clients
   - Internally-identified bugs (not raised by Shoprite), unless they're global, high-impact fixes worth flagging anyway

---

## Step 5: Cross-Check Against the Published Help Center Release Notes

**Why this step exists:** feature work is often tracked in ClickUp lists outside the Platform Squad's sprint-numbered list (e.g. a dedicated project list like "BME | Best Match Enhancements", or an Integrations backlog). The Steps 2-4 sprint-board pull can miss real, shipped, client-relevant work that the published customer-facing Help Center notes will already include.

1. **This is a hard gate.** If `{help_center_url}` wasn't provided in Step 1, do not proceed to Step 6. Ask again:
   ```
   Before I can finalize this, I need either the link to this period's
   published Help Center release notes, or your explicit confirmation
   that it doesn't exist yet for this period.
   ```
   Only two answers unblock the draft:
   - A URL: proceed to step 2 below.
   - An explicit statement that no such article exists yet for this period: proceed, but add a visible "Not cross-checked against Help Center release notes (none exists yet for this period)" line near the draft's status.

   "Not right now," "later," silence, or moving on to another topic does **not** count as either answer. Re-ask rather than treating a non-answer as permission to skip.
2. If a URL is available, extract the article ID from it and fetch it with `get_article` (Intercom MCP), not `WebFetch`. These Help Center pages are gated and `WebFetch` will 401.
3. List every feature or fix mentioned in the article.
4. Cross-reference against what Steps 2-4 already found:
   - Already captured and consistent: leave as-is, this is just confirmation.
   - Already captured but the article's wording is clearer or more accurate: prefer the article's framing.
   - New item, platform-wide (not scoped to a different named client): add it, running it through the same Shoprite-relevance filter as Step 2.
   - New item, clearly scoped to a different client: exclude, same as any other client-specific ticket.

---

## Step 6: Filter the Draft

Before formatting, strip out:

- Back-office or admin features not accessible to Shoprite users
- Infrastructure/platform work with no user-facing impact, or no relevance to Shoprite
- Features built for other clients (FNB, TransUnion, etc.), unless explicitly relevant to Shoprite (e.g. a data product that happens to run on Shoprite data, like the FNB batch enablement work)
- Bugs that were internally identified rather than client-raised, unless global and high-impact
- All ClickUp ticket links and IDs. Internal reference only, never shown to the client

Flag anything that's a **pre-announcement** (upcoming change, migration, new environment not yet live). These go in a clearly labelled **Upcoming Changes** section, never mixed into delivered work.

If something is ambiguous (decision pending, TBC, awaiting a session outcome), don't guess. List it separately and ask the user how to handle it rather than silently including or excluding it.

---

## Step 7: Format

```markdown
# Omnisient Platform – Sprint {N} Release Summary

**Period:** {start date} – {end date} | **Prepared for:** Shoprite

---

## [Section Heading]
- **Feature name:** One to two sentence plain-English description of what changed and why it matters to the user.
```

Rules:
- Only include section headings that have content (see reference list below).
- Bullet points: bold feature name, colon, plain description.
- Max two sentences per bullet.
- No jargon, no internal ticket IDs, no technical implementation detail, no links.
- No em dashes anywhere in the draft. Use a period, colon, semicolon, or en dash (–) instead. Scan the finished draft for the — character before presenting it.

---

## Step 8: Review Checklist

Before this goes anywhere near the client, the SOP requires sign-off from:

- Product Manager: confirms all items are correctly described and nothing is missing
- Account Manager / CoE: confirms nothing is client-sensitive or premature
- Head of Data Product Growth
- Head of Product Development
- CTO

Dex can't collect these sign-offs itself. Present the draft and this checklist to the user, and wait for confirmation that the review chain is complete (or that they're handling it outside Dex) before treating the doc as final.

---

## Step 9: Save

Save the final draft to the vault at:

```
06-Resources/Knowledge/Shoprite/SRX_Sprint_{N}_Release_Summary.md
```

(confirm location with the user if this is the first time, default to the path above).

**Do not create a ClickUp document or page for this.** Once the draft is finalized and signed off, tell the user to:
1. Paste the content into the sub-page under **Shoprite Release Notes** in ClickUp themselves (named `SRX - Sprint {N} Release Summary`)
2. Send to the Shoprite account team via the agreed channel (currently email)

This keeps the vault copy as the source of truth for future sprint comparisons without Dex touching ClickUp docs directly.

---

## Reference: Section Headings

Use only where there's content:

- Shoprite Data Feed
- Audience Activation
- Platform Enhancements
- Integrations
- Platform Stability & Reliability
- Data Infrastructure
- Platform UX
- Upcoming Changes (pre-announcements only)

---

## Notes

- This is a custom skill, protected from Dex updates.
- Edit `.claude/skills/shoprite-release-notes-custom/SKILL.md` to modify.
- Never create ClickUp documents/pages from this skill. Save to the vault and let the user publish to ClickUp and send the client email themselves. (Standing rule across all Dex skills, not specific to Shoprite.)
- Pairs with `/release-notes-custom` (internal sales/AM version of the same sprint) and `/intercom-article-custom` (KB articles referenced in the "Proposed Comms" for each feature, though article links themselves never appear in the client-facing output).
- Also pairs with the published Help Center "Release Notes: {Month} {Year}" article (Step 5). That article isn't Shoprite-specific, it's the compiled customer-facing list for the period, which is exactly why it catches platform-wide work the Platform Squad's sprint board alone can miss.