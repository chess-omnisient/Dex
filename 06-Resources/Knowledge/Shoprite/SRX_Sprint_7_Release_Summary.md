# Omnisient Platform – Sprint 7 Release Summary

**Period:** 6 July – 2 August 2026 | **Prepared for:** Shoprite

**Status: DRAFT – pending 1 item below and full sign-off (see checklist)**

---

## Platform Enhancements

- **Best Match now supports Passport, SSN, and credit card matching:** When creating a new Overlap or Custom project, Best Match can now match on passport number, social security number, and full credit card number as exact-match fields, in addition to existing fields.
- **Project expiry visibility and advance-warning emails:** The project table now shows an effective expiry date (whichever comes first: dataset subscription end or share expiry). Project creators get automatic email warnings 14 days and 3 days before a project locks, flagging which audiences and campaigns will be affected.

## Integrations

- **Google BigQuery data connector:** Platform users can now connect directly to Google BigQuery through Desktop Connect and Server Connect, using the same setup and upload workflow as other data sources, with secure service account authentication and automatic schema mapping.

## Platform UX

- **Clearer dataset upload status:** The Available Datasets table now shows upload counts and a color-coded status (ready, processing/under review, or action needed) at a glance. Clicking the count opens the dataset history for more detail.
- **Selection Builder now warns on unapplied filter changes:** If you change a filter but haven't applied it yet, the Apply Filters button now flags it clearly, and you'll be prompted to apply or discard before moving on.
- **General platform polish:** Tables now load pre-sorted with a visible sort indicator; key actions on detail pages (Share, Approve, Register, Accept) now show as buttons instead of a dropdown; a clearer on-screen error now flags PII mismatches during project creation instead of a popup; and several screens (dataset mapping/reports/upload activity, partner activity logs, admin API keys/audit trail/users) have been upgraded to the latest interface.

## Shoprite Data Feed

- **Resolved upload issues on the AHT health data feed:** Intermittent upload failures affecting treatment, diagnosis, and medication records from the Altron HealthTech feed that powers the Shoprite x AHT health audience segments were resolved this sprint.

## Platform Stability & Reliability

- **Fixed SQL query errors on reserved-word column names:** Selections that included a column name matching a SQL reserved word (or containing spaces/special characters) could previously fail. These are now handled automatically wherever selections are built.
- **Fixed intermittent Jupyter Notebook and SQLPad login failures:** A backend issue with duplicate connection records was occasionally preventing Jupyter Notebook and SQLPad from loading. This has been resolved.

---

## Pending decision (not yet included)

1. **Shoprite_PRJ_00430 duplicate-dataset issue:** Fix appears deployed, but Intercom doesn't show the client confirming resolution (SLA missed, no reply to AM follow-up). Waiting on your confirmation with account management before this goes in.

---

## Excluded from this draft

- A large "project creation wizard" epic (buyer dataset selection, auto key-detection, field-mapping validation, approval flow). Confirmed not relevant to Shoprite.
- Several TransUnion/ABSA-specific BI Viz and Cleanroom Analytics tickets. Different client.
- Etisalat, Property24, and Riskx-specific tickets. Different clients.
- Routine automated "upload hydration failure" retries on Shoprite datasets. Internally detected via monitoring, not client-raised, and not global or high-impact enough to flag.
- SHOPRITE_PRJ_00419 project generation failure. Internally detected (no Intercom link, no client tag), not client-raised.
- Internal-only work: QA process steps, deploy/DoR checkpoints, CodeTour onboarding tasks, OmniCheck stored-proc refactor. No user-facing impact.

---

## Review Checklist (sign-off required before sending)

- [ ] Product Manager: confirms all items are correctly described and nothing is missing
- [ ] Account Manager / CoE: confirms nothing is client-sensitive or premature
- [ ] Head of Data Product Growth
- [ ] Head of Product Development
- [ ] CTO

Once signed off, paste into the ClickUp sub-page **"SRX - Sprint 7 Release Summary"** under Shoprite Release Notes, and send via the agreed email channel. Dex does not create ClickUp docs or send anything directly.