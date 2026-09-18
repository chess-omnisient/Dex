---
name: intercom-article-custom
description: Write structured, evergreen Intercom knowledge base articles for a SaaS fintech product. Supports hub/index, overview, feature documentation, and step-by-step guide formats with audience-level calibration.
---

# Intercom Article Writer

Write structured, evergreen Intercom knowledge base articles that reduce direct support load on account managers and stand the test of time.

## Usage

- `/intercom-article-custom` – Guided mode (asks for type, topic, level)
- `/intercom-article-custom hub [topic]` – Write a hub/index article (parent with types, statuses, notifications)
- `/intercom-article-custom overview [topic]` – Write a feature overview article
- `/intercom-article-custom feature-doc [topic]` – Write feature documentation
- `/intercom-article-custom how-to [task]` – Write a step-by-step guide
- `/intercom-article-custom update [article-title]` – Revise an existing article with new or corrected information
- Add `--level technical` to any of the above for a technical audience (default: non-technical)

**Examples:**
- `/intercom-article-custom hub projects`
- `/intercom-article-custom feature-doc overlap`
- `/intercom-article-custom how-to create a dataset --level technical`
- `/intercom-article-custom overview projects`
- `/intercom-article-custom update validation issues`

---

## Article Hierarchy

Articles sit in a four-tier hierarchy. Always link up and down.

```
Hub / Index (authoritative parent – project types, statuses, notifications)
  └── Feature Doc (what is Overlap / what are datasets / how widgets work)
        └── Overview (what is X, how the product area works)
              └── How-To Guide (step-by-step from navigation to outcome)
```

Not every area needs all four tiers. A simple feature may only need a Feature Doc + How-To. A complex area like Projects needs a Hub at the top.

---

## Step 1: Gather Context

If type, topic, or level are not provided as arguments, ask:

1. **Article type**: `hub` | `overview` | `feature-doc` | `how-to`
2. **Topic or task**: What feature/functionality/action is this about?
3. **Audience level**: `non-technical` (default) | `technical`
4. **Related articles**: Are there existing articles this should link to or sit under?
5. **Existing source material**: Are there internal docs, meeting notes, or old articles to draw from?

**Choosing the right type:**
- Use `hub` when the topic has multiple variants, types, or states to document (e.g. Projects, Datasets)
- Use `feature-doc` when documenting a specific feature in depth (e.g. Overlap, Selections)
- Use `overview` when introducing a broad product area without variant tables
- Use `how-to` for task-oriented guides – but first check if the flow is short enough to be a section in the parent feature-doc instead

---

## Step 2: Consolidation Check

Before writing, ask:

> "Does an existing overview or feature-doc already cover this area? Could this be a new section in an existing article rather than a standalone one?"

If yes: suggest **adding a section** to the existing article + creating a linked how-to guide rather than a new isolated article. This prevents documentation sprawl (Feature A, B, C as separate articles when they all belong under D).

---

## Step 2b: Update an Existing Article

**Triggered by:** `/intercom-article-custom update [article-title]`

Use this when an existing article needs to be revised – not rewritten from scratch.

### Gather context

Ask the user:

1. **Paste the existing article** (or confirm you have it open)
2. **What needs to change?** (new feature, corrected information, restructure, tone pass, gap fill)
3. **Why is it changing?** (product update, customer confusion, AM feedback, audit)
4. **Audience level**: keep existing | `non-technical` | `technical`

### Update approach

- Make **targeted changes** – preserve what's accurate and well-structured
- Don't rewrite sections that don't need it
- If the change touches structure (e.g. a new section, a renamed feature), apply the relevant article type template from Step 3 to that section only
- If the scope of changes is large enough that a full rewrite is cleaner, say so and ask for confirmation before proceeding

### Output format

Output the **full revised article** (not just a diff), then immediately follow with a change summary:

```
---
**What changed:**
- [Section or element]: [What was changed and why]
- [Section or element]: [What was changed and why]
```

Then run the full **Step 4 Evergreen Quality Check** and **Step 5 Surface Gaps** as normal.

---

## Step 3: Write the Article

Use the structure for the chosen article type below.

---

### Article Type: Hub / Index

**When to use:** A product area that has multiple types, variants, or states – where users need to understand the landscape before going deeper. Acts as the authoritative parent that child feature-docs link back to.

**Examples:** Projects, Datasets, Selections, Connections

**Structure:**

```markdown
# [Product Area]

[1–2 sentence description of what this area of the Omnisient Platform does and why it exists.]

---

## [Types / Variants]

[Intro sentence if needed.]

| [Type] | Description | [Attribute] | [Attribute] | [Attribute] |
|--------|-------------|-------------|-------------|-------------|
| **[Name]** | [Description] | [Value] | [Value] | [Value] |

> [Callout for any nuance – e.g. subscription access, availability note, evolving feature]

---

## Creating a [item]

[Navigation path and creation flow. Keep concise – full how-to only if the flow is complex enough to warrant it.]

---

## [Item] roles

[Roles table if permissions vary within this area.]

| Role | Can do |
|------|--------|
| **Owner** | ... |
| **Read and Write** | ... |
| **Read Only** | ... |

---

## [Item] status

| Status | What it means |
|--------|--------------|
| **[Status]** | [Description] |

---

## Notifications

| Event | Email | In-app | Who receives it |
|-------|-------|--------|-----------------|
| [Trigger] | ✅/– | ✅/– | [Receiver] |

---

## Related

- [Child feature-doc](#)
- [Child feature-doc](#)
- [Supporting article](#)
```

**Reusable table patterns for hub articles:**

*Types table* – use when comparing variants with multiple attributes:
```markdown
| Type | Description | Refreshable | Subscription | Approver |
```

*Status table* – use when items have lifecycle states:
```markdown
| Status | What it means |
```

*Notification table* – use when events trigger communications:
```markdown
| Event | Email | In-app | Who receives it |
```

---

### Article Type: Overview

**When to use:** Introducing a product area or major capability. Serves as the entry point that links to feature-docs and how-to guides beneath it.

**Structure:**

```markdown
# [Product Area / Feature Name]

[1–2 sentence intro. What this area of the Omnisient Platform does and why it matters.
No "new feature" language. Write as if this will be read in 2 years.]

## Where to find [Feature Name]

In the Omnisient Platform, go to **[Top Level]** → **[Feature Name]**. [1-line description of what this feature does.]

[Screenshot: navigation to [Top Level] → [Feature Name]]

## What's included

- **[Sub-feature or component]** – [One-line description]
- **[Sub-feature or component]** – [One-line description]
- ...

## How it works

[Concise explanation of the underlying logic or mechanism.
Non-technical: use plain language and analogies.
Technical: precise terminology, no hand-holding.]

## Who can use this

[User roles or permission levels required. Be specific.]

## Related guides

- [How to do X](#)
- [How to do Y](#)
- [Understanding [Feature Doc]](#)
```

---

### Article Type: Feature Documentation

**When to use:** A deep-dive on a specific feature or concept. Sits between overview and how-to. Explains what something is, how it behaves, and its options.

**Structure:**

```markdown
# [Feature Name]

[2–3 sentence overview. What this feature is, what it's used for.]

## Where to find [Feature Name]

In the Omnisient Platform, go to **[Top Level]** → **[Feature Name]**. [1-line description of what this feature does.]

[Screenshot: navigation to [Top Level] → [Feature Name]]

## Key concepts

[Any terminology the user needs before reading further.
Keep to what's genuinely needed – don't define obvious things.]

## How [Feature] works

[Mechanics, logic, configuration. Calibrate depth to audience level.
Non-technical: explain the why before the how.
Technical: precision over hand-holding.]

## Options / Configuration

[Settings, variants, modes, or types if applicable.
Use a table if there are multiple options to compare.]

## Related articles

[What connects to this? Link to related feature-docs that interact with this one.]

## Guides

- [How to do X](#)
- [How to set up Y](#)
```

---

### Article Type: Step-by-Step Guide (How-To)

**When to use:** Task-oriented. Gets a user from intent to completed outcome. Always references a parent feature-doc or overview.

**Structure:**

```markdown
# How to [specific task]

[1 sentence: what this guide covers and what the user will be able to do after.]

## Before you start

- **Permissions required:** [Role or access level needed]
- **Prerequisites:** [Anything that must be set up first, if applicable]

## Getting there

[Full navigation path from the main landing page.
Example: Dashboard → Projects → [Project name] → Datasets → Add Dataset]

## Steps

1. [Clear, action-oriented step. One action per step.]
2. [What to click, select, or enter.]
3. [Continue until task is complete.]

> **Note:** [Add inline callouts for anything that commonly trips users up.]

## What to expect

[What confirmation, output, or screen state the user should see when done correctly.
This is the "did it work?" check.]

## Common issues

| Issue | Likely cause | Fix |
|-------|--------------|-----|
| [Error message or symptom] | [Why it happens] | [How to resolve it] |
| [Another common issue] | [Cause] | [Fix] |

## Related

- [Parent feature doc](#)
- [Overview article for this area](#)
- [Related how-to guide](#)
```

---

## Step 4: Evergreen Quality Check

Run this checklist before outputting the final article:

**Language – flag and rewrite any of these:**
- [ ] No "new", "recently added", "now you can", "we've just launched", "exciting new", "brand new"
- [ ] No "revolutionizes", "supercharge", "powerful", "seamless", "game-changing"
- [ ] No "We're excited to announce", "We're committed to improving your experience"
- [ ] No "Thank you for your continued use of our Omnisient Platform" or similar sign-offs
- [ ] No "Try it out!" or "Jump in and experience..." CTAs
- [ ] Only use this emoji for very important bullet points (📌)
- [ ] Do not use these emoji bullet points✨, 🎉– these age poorly and look unprofessional
- [ ] No date-specific references unless genuinely permanent
- [ ] No "simply" or "just" – condescending when something is hard
- [ ] Emoji: ⚠️ for warning callouts, 💡 for tips, 🚀 for a notable/higher-tier feature, ✅/❌ for table booleans, 👉 before "Learn more" / "See [X] article" links. No 📌, ✨, or 🎉 – see `references/visual-style-guide.md` for full callout and table conventions


**Structure:**
- [ ] Links to parent article if this is a feature-doc or how-to
- [ ] Links down to child articles if this is a hub or feature-doc
- [ ] Navigation path is complete (how-to only)
- [ ] Permissions section present (how-to only)
- [ ] Common issues section covers known pain points (how-to only)
- [ ] Could this be a section in an existing article rather than a standalone?
- [ ] For how-to articles: is the flow short enough to be a section in the parent feature-doc instead?

**Tone:**
- [ ] Professional and friendly – not cold, not overly casual
- [ ] Straight to the point – answer first, context second
- [ ] No filler sentences – every line earns its place
- [ ] Not condescending – assume competence, explain clearly

**Support usability:**
- [ ] Would an AM be comfortable sending this as a direct reply to a customer?
- [ ] Does it answer the likely follow-up questions, not just the surface question?


---

## Step 5: Surface Gaps

After writing, always close with a gaps section covering:

1. **Missing information** – anything that couldn't be written with confidence and needs verification before publishing
2. **Articles that need to exist** – child articles this links to that don't exist yet
3. **Articles that can be retired** – existing articles made redundant by this one
4. **Needs confirmation** – content marked TBC or uncertain in source material

Format:
```
---
**Before publishing:**
- [ ] [Information needed / question to answer]
- [ ] [Article to create: title]
- [ ] [Article to retire: title – replaced by this]
- [ ] [Confirm: specific detail that needs verification]
```

---

## Audience Level Calibration

### Non-technical (default)
- Plain language – avoid or define jargon on first use
- Explain *why* before *how* where it helps comprehension
- UI-based instructions (click, navigate, select, toggle)
- Use analogies for complex concepts
- Include more context in the "Getting there" navigation section

### Technical
- Use product and domain terminology without defining it
- Shorter explanations – assume familiarity with the Omnisient Platform
- Can reference configuration, API behaviour, or data structures where relevant
- Focus on precision over hand-holding
- Skip analogies

---

## Tone Reference

**Good:**
> "Datasets are collections of records used across your projects. Each dataset is linked to one or more project types and determines what data is available to widgets within that project."

**Avoid:**
> "We're excited to introduce our brand new Datasets feature! Simply navigate to your dashboard and you'll find this powerful new tool waiting for you."

**The test:** Would a busy account manager send this to a frustrated customer and feel confident it answers their question completely?

---

## Notes

- This is a custom skill, protected from Dex updates
- Edit `.claude/skills/intercom-article-custom/SKILL.md` to modify
- See `references/visual-style-guide.md` for callout colors, table formatting, header rules, and emoji conventions, derived from an audit of five published articles
- Product context: SaaS fintech, mixed technical audience
- **Product name:** always refer to the product as "Omnisient Platform" – never "the platform," "our platform," "the app," or "the product" generically
- Default audience level: non-technical unless specified
- Always check consolidation before creating a standalone article
