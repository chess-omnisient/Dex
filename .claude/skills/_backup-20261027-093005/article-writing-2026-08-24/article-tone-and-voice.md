# Tone & Voice in Help Center Articles

Standards for how a sentence should sound in a help article — word choice, person, tense, and
framing. Complementary to `article-structure.md` (how content is organized) and
`image-usage-in-help-articles.md` (when and how images are used). This is purely informational
content, not marketing — every rule here exists to keep the voice functional and out of the way
of the reader.

---

## Table of Contents

1. [Present tense, always](#present-tense-always)
2. [Second person for the reader's actions; imperative in steps](#second-person-for-the-readers-actions-imperative-in-steps)
3. [No "we" / "our" / "us"](#no-we--our--us)
4. [Drop "please" from instructions](#drop-please-from-instructions)
5. [No promotional or efficiency language](#no-promotional-or-efficiency-language)
6. [No anthropomorphizing the system](#no-anthropomorphizing-the-system)
7. [Timeless framing, never announcement framing](#timeless-framing-never-announcement-framing)
8. [Gender-neutral language](#gender-neutral-language)
9. [Write for a non-native-English audience](#write-for-a-non-native-english-audience)
10. [Contractions are fine](#contractions-are-fine)
11. [Reserve hedging for genuine conditionality](#reserve-hedging-for-genuine-conditionality)
12. [Consistent terminology](#consistent-terminology)
13. [No meta-commentary](#no-meta-commentary)
14. [Pre-write checklist](#pre-write-checklist)
15. [Sources](#sources)

---

## Present tense, always

Every article — reference, how-to, or explanation — is written in present tense, describing the
platform as it currently behaves. Never past tense, and future tense only for a direct, immediate
consequence ("a bottom sheet will open"), never for describing the feature itself.

> "A project is a workspace for data analysis and visualization."
> "Selections let you create a filtered sub-set of customers..."

---

## Second person for the reader's actions; imperative in steps

Once an article has stated what a thing *is* (see `article-structure.md`'s opening rule), switch
to second person — "you" — for anything the reader does or sees. Reserve third-person passive
voice for reference tables, where it reads naturally ("Datasets are grouped based on their
current processing, registration, and sharing status").

| Context | Voice | Example |
|---|---|---|
| Describing a reader action | Second person ("you") | "You can build a selection from your own data, from a partner's data..." |
| A numbered step's instruction | Imperative | "Choose one of the following ways to authenticate." / "Start by specifying who you're targeting and what you plan to do with the audience." |
| Reference table row | Third-person passive | "Fields are grouped into Required fields and Additional fields." |

This is the standard convention across Google's, Microsoft's, and GitLab's documentation style
guides. Don't slide into third person mid-paragraph when the subject is the reader's own action —
"the user selects a dataset type" should be "you select a dataset type."

---

## No "we" / "our" / "us"

**Standard: don't use "we"/"our"/"us."** State requirements and recommendations neutrally, without
a speaker, so the article reads as documentation of the system rather than a message from the team
writing it.

| Instead of | Write |
|---|---|
| "We'll need a few key details from your IdP." | "Required from your IdP:" (followed by a table) |
| "We recommend following this order." | "Recommended order:" or "Map dimension datasets before transactional datasets." |
| "Start by telling **us** who you're targeting." | "Start by specifying who you're targeting." |

This keeps the article's voice consistent with the "purely informational, not marketing" standard
— a first-person team voice reads as relationship/sales-adjacent, which is exactly what this
system avoids everywhere else.

---

## Drop "please" from instructions

A reference or how-to voice doesn't need politeness markers — state the instruction or requirement
directly. "Please contact Omnisient Support" becomes "Contact Omnisient Support." This is standard
across technical-writing style guides (Google's is explicit about it): "please" reads as a request
between people, not documentation of a system.

---

## No promotional or efficiency language

Don't describe how well something works — describe what it does and let the reader judge.

**Banned** (non-exhaustive, extend by pattern-matching): seamlessly, streamlining, enhanced
productivity, versatile, effortlessly, powerful, robust, cutting-edge, game-changing, intuitive
(as a claim rather than a demonstrated fact), simplifies (as filler — state the specific
simplification instead).

> **Bad:** "facilitates the automation of tasks and processes, streamlining workflow for enhanced
> productivity and efficiency."
> **Better:** state what the feature actually lets the reader do, concretely — "lets you run code,
> visualizations, and narrative text in a single document."

---

## No anthropomorphizing the system

Describe what the platform *does*, not what it "wants," "thinks," or "decides." State behavior as
fact: "the system validates the token" rather than "the system checks whether it trusts the
token." This is an easy habit to slip into, especially when describing automated logic or
validation.

---

## Timeless framing, never announcement framing

No "now," "new," "just launched," "standard on every X," or "faster [than before]" — no temporal
or comparative language implying a before/after change, even when describing something that
genuinely did just change. Write the permanent current state of the functionality, not the fact
that it changed.

This is the single most important rule in this document. It's not about word choice — a flat,
unpromotional sentence can still violate it if it's structured as "before vs. after" instead of
"here's what this is."

**Why:** the platform ships functionality changes every sprint. An article that describes a
feature as "new" or "now faster" is stale the moment something else changes, and can't flex as the
functionality it documents grows or shrinks. A help article has no publish date attached to its
voice — it should read the same whether it's six days old or two years old.

> **Bad:** "Faster Filtering and Clear Credit Metrics, Standard on Every BI Viz Project... now
> standard on every BI Viz project."
> **Better:** "The BI Viz project template pre-aggregates credit score, affordability, DTI, and
> affluency segment, giving fast, stable filtering on these fields. Credit score, affordability,
> and DTI are presented as labelled bands rather than raw numbers."

Announcement/changelog framing has exactly one legitimate home: **release notes**, which are a
distinct article type with their own (separate, not-yet-written) guidelines. If you're not writing
a release note, this rule applies without exception.

---

## Gender-neutral language

Use "they"/"them" for a generic person if a pronoun is unavoidable, or restructure the sentence so
no pronoun is needed at all. Never default to "he" or "she" for a generic user, admin, or partner
contact. This is standard across every major technical-writing style guide.

---

## Write for a non-native-English audience

Avoid idioms, colloquialisms, culturally specific references, and humor that may not translate.
The platform serves multiple markets — plain, literal phrasing travels; a turn of phrase that
sounds natural to one reader can be confusing or unintentionally comic to another.

---

## Contractions are fine

Don't force artificial formality. Contractions read naturally — "you'll," "doesn't," "isn't." Use
them; don't "correct" them to "will not," "does not" in a misguided attempt to sound more formal.
A plain, direct voice is the goal, not a stiff one.

---

## Reserve hedging for genuine conditionality

"May," "might," and "could" should signal an outcome that's genuinely uncertain — not stand in for
an if-then relationship that's actually deterministic. If a stated condition fully determines the
outcome, the "if" clause already carries all the conditionality; adding "may" on top wrongly
suggests the outcome is still up in the air even once the condition is met. The hedge is only
earned when the outcome isn't fully pinned down by what's stated — real approver/human discretion,
real variability, or conditions the article doesn't (and can't) fully enumerate.

> **Bad:** "May be greyed out if the partner has not enabled selections on their dataset share
> agreement." This reads as a hedge but describes a fully deterministic UI state — if that one
> setting is off, the option is *always* greyed out, not sometimes.
> **Good:** "**Greyed out** if the partner has not enabled selections on their dataset share
> agreement." (Present tense, no "may" — see the present-tense rule above.)
> **Correct use of "may":** "A project may be rejected during approval" — the outcome depends on
> the approver's judgment, not on one stated condition that would fully determine it either way.
> **Incorrect use:** "The dataset may take a few minutes to process" when it always does — that's
> not a hedge, it's a fact; state it as one ("The dataset takes a few minutes to process").

---

## Consistent terminology

Pick one term per concept and use it everywhere — within an article and across articles. Don't
alternate between synonyms for the same thing; a reader scanning for a term will assume two
different words mean two different things.

> If an article's title calls a feature "Audiences" but the body calls it "Selections" throughout,
> a reader skimming both has no signal these are the same thing. Pick one term — ideally whichever
> matches the feature's actual UI name — and use it everywhere, including the title.

---

## No meta-commentary

Don't narrate the article itself. No "in this article we'll cover...", "let's dive into...", "this
guide will walk you through..." Open with the thing the article is about — see
`article-structure.md`'s opening rule — not a description of the article.

---

## Pre-write checklist

Before drafting, confirm:

- [ ] Every sentence is present tense (or immediate-consequence future tense only).
- [ ] "You" is used for reader actions; imperative is used inside numbered steps; third-person
      passive is reserved for reference tables.
- [ ] No "we"/"our"/"us" — requirements and recommendations are stated neutrally.
- [ ] No "please" in instructions.
- [ ] No promotional or efficiency adjectives.
- [ ] No anthropomorphizing the system — behavior is stated as fact, not intent.
- [ ] No temporal or comparative framing ("now," "new," "faster than," "standard on every X").
- [ ] No gendered pronouns for a generic person.
- [ ] No idioms, colloquialisms, or humor that might not translate for a global audience.
- [ ] Contractions are used naturally, not stripped out for false formality.
- [ ] "May"/"might"/"could" appear only where the outcome isn't already fully determined by a
      stated "if" clause — a deterministic if-then gets present tense, no hedge.
- [ ] The same term is used for the same concept throughout — including the title.
- [ ] No meta-commentary about the article itself.

## Sources

Cross-checked against industry technical-writing style guides — Google Developer Documentation
Style Guide, Microsoft Writing Style Guide, and GitLab Docs Style Guide — for consistency with
established norms.
