---
name: release-notes-custom
description: Generate internal release notes for sales and account management teams. Structured by feature area with links to user stories and KB articles. One doc per sprint.
---

# Release Notes (Internal Sales & Accounts)

Generate an internal release notes document to brief the sales and account management team on what shipped this sprint. Contains feature descriptions, links to user stories (ClickUp) and knowledge base articles (Intercom). Direct and structured — focused on enabling conversations, not client communication.

**Audience:** Sales, account managers, customer success
**Tone:** Direct, informative, practical — written for people who need to understand what has been released confidently and easily

---

## Process

### Step 1: Gather Context

Ask the user:

```
To write the release notes, I need:

1. **Which sprint/release?** (e.g. Sprint 2, March Release)
2. **Feature list** — all features and changes shipping in this release, grouped by area if possible
3. **Links** — ClickUp user story links and/or Intercom KB article links for each feature (paste them matched to feature names)
4. **Where to save?** (default: 06-Resources/Knowledge/Internal Staff/Release_Notes_[Sprint_Name].md)
```

Wait for the feature list before writing. Do not generate placeholder content.

### Step 2: Generate the Release Notes

Save to the agreed location. Use the structure below.

**Output format:**

```markdown
# Release Notes — [Sprint / Release Name]

---

## [Feature Area 1]

**[Feature name or ticket reference]**

[1–3 sentences. What it does, what changed, why it matters. No marketing language — just clear description.]

- [User Story](clickup-link)

**[Feature name]**

[Description.]

- [KB Article Title](intercom-link)

---

## [Feature Area 2]

**[Feature name]**

[Description.]

- [User Story](clickup-link)

Knowledge base:
- [Article 1](link)
- [Article 2](link)

---

## [Feature Area 3]

...
```

### Formatting rules

1. **Group features by area** — use `##` headings for each area (e.g. "Audience Activation", "Platform UX", "Data Infrastructure")
2. **Bold feature names** — use `**Feature name**` under each area heading
3. **One description per feature** — 1–3 sentences, plain language, no filler
4. **Links go under the feature they belong to:**
   - ClickUp user stories: `- [User Story](url)`
   - Single KB article: `- [Article Title](url)`
   - Multiple KB articles for an area: use a `Knowledge base:` block with bullet links
5. **No links? No problem** — if a feature has no user story or KB article, just include the description. Don't flag missing links.
6. **No caveats, talking points, or objection handling** — this is a reference doc, not a feature alert. Keep it factual.
7. **No "Conclusion" section** — the doc ends after the last feature area.

### Step 3: Review Prompt

After generating, ask:

```
Anything to add or adjust?

- Missing features or links?
- Descriptions need more/less detail?
- Feature groupings make sense?
```

---

## Notes

- This skill produces a markdown file saved to the knowledge base — not Slack copy.
- One file per sprint. Name format: `Release_Notes_Sprint_[N].md`
- Pairs with `/feature-alert-custom` (Slack alert for the same release) and `/intercom-article-custom` (KB articles linked in the notes).
- If the user provides a feature alert or newsletter draft for the same release, use it as context for consistent descriptions.

---

## Related Skills

- `/feature-alert-custom` — Slack-ready internal alert with talking points and objection handling
- `/intercom-article-custom` — Write or update Intercom KB articles linked in the release notes
