# Newsletter Copy & Layout

The complete rule set for how the Omnisient product newsletter reads and renders. Derived from the
September 2026 edition, which is the reference standard. Colours and type come from
`06-Resources/Omnisient_Brand.md`; this file does not redefine them, it says how they're used in email.

---

## 1. What this email is

A 2-up "what's new" email to platform users. It is the short form: the release notes article is the
long form, and this email points at it. One screen of reading, 2 news pieces as a rule, 3 at the
outside. More than 3 means the month needed an article, not a longer email.

The reader is a platform user, not a buyer and not an engineer. They want to know what changed in the
product they already use and whether they need to do anything.

---

## 2. Voice

Follows the release-notes voice (`release-notes-writer/references/release-notes-tone-and-structure.md`),
tightened for email:

- **Second person.** "You can now see every blocking issue." Not "users are able to".
- **Present tense, active.** The feature is live when this lands. No "will be able to".
- **Announcement framing is correct here** – "now", "new", "you can now" are all expected.
- **"We" only for things Omnisient does to the platform** ("Omnisient may remove records that could
  constitute a re-identification risk"). Never as the default voice.
- **No marketing adjectives.** The September edition says "see every blocking issue at once", not
  "a powerful new experience". Specific beats enthusiastic.
- **Write per the user's global writing rules.** No banned vocabulary. No "this isn't X, it's Y"
  reframing.
- **En dashes, never em dashes – anywhere in the file,** including the `<title>`, image placeholder
  labels and comments, not just the reader-facing copy.

---

## 3. Headlines

**Formula:** the user-facing outcome, title case, 3–8 words. Name the thing, then what you get.

From the September edition:

- `Locked Projects: See Every Blocking Issue At Once`
- `How We Protect Your Data From Re-identification`

The colon form works when the feature area needs naming first. The plain form works when the outcome
is self-explanatory. Both are fine; don't force either.

**Never:**

- The ticket name verbatim ("Locked project screen shows every locking reason at once" is a ticket,
  not a headline).
- Internal names, codenames, squad names, ticket IDs.
- Questions, unless the piece genuinely answers a user's question ("Where did my records go?").

---

## 4. Body paragraphs

2–3 sentences. One paragraph per piece, or 2 short ones when there's a distinct second beat (the
September "Locked Projects" piece does this: what you see, then what happens when you act).

**Shape:**

1. **What changed, from the reader's seat.** Open with the situation, not the feature name:
   "When a project locks for more than one reason, you can now see every blocking issue at once."
2. **What they gain, or what to do about it.** "Contact support opens a pre-filled chat, so it all
   gets sorted in one conversation."

**Condensing from the ticket.** The `### Release Comms Description` is written for the article and
usually carries a bullet list. For the email, keep the opening claim and the single most useful
detail; drop the rest. The article is where the full list lives, and the intro already links to it.

**Length budget:** 35–55 words per piece. The September pieces are 38 and 46.

**Expectation-setting matters.** Where a change could look like a bug (data shrinking, a screen
moving), say plainly that it's expected: "This can reduce the size of your dataset, which is expected
and not an error." That sentence prevents support tickets and belongs in the email.

---

## 5. Intro

"Hi there," then 1–2 sentences naming what the release focuses on, written **after** the pieces so it
reflects them. The September edition:

> This release focuses on two updates that make it easier to manage your projects: see every reason a
> locked project is locked in one place, and understand at a glance why your data may look different
> once it's added to a project.

Name the count ("two updates"), then each piece in a clause. If the pieces share no theme, say what
they share factually ("two unrelated improvements to projects and data handling") rather than
inventing a narrative.

Below the intro, always:

- `Read the full release notes →` linking the Intercom release notes article for the comms month.
- The login reminder line: `💡 Remember to login to the Omnisient platform to view release notes.`

---

## 6. Editorial check

Run before using any ticket copy. Flag to the user, never publish:

- Internal-only names, codenames, squad or sprint references.
- Client names (`Shoprite`, `TransUnion`, …) in a cross-client email.
- Competitor references.
- Ticket jargon: "ACE", "DCR", "PSI", "3-way", "OLAP" and similar, unless the platform UI itself uses
  the term where the user will see it.
- Anything described as live that isn't.

---

## 7. Layout

**Email, not web.** Table-based layout, inline styles on every element, no flexbox, no grid, no
external CSS, no `<style>` block relied on for layout. Outlook drops all of it.

**Structure, top to bottom:**

| Band | Background | Contents |
|---|---|---|
| Header | Blue gradient | Logo, "Release Notes.", "What's new in [Month Year]" |
| Intro | White | Greeting, focus sentences, full-notes link, login reminder |
| Images | Blue / violet-blue wash | One screenshot per piece, side by side |
| Pieces | White | Headline + body + "Learn more →" per piece, side by side |
| Footer | Blue gradient | LinkedIn line, the 4 office addresses |
| Legal | White | Unsubscribe · Manage Preferences · Contact Us |

**Width:** 800px fixed, centred on `#f2f2f2`.

**Type:** Poppins with web-safe fallbacks (`'Poppins',"Segoe UI",Helvetica,Arial,sans-serif`). Email
clients often won't load the webfont, so the fallback must be acceptable on its own. Body 15px/1.7,
headline 19px bold, header title 44px.

**Colour:** `--brand` `#3272B9` and `--brand-dark` `#30297E` from the brand file, as literal hexes
(custom properties don't survive email clients). Header and footer gradient runs `#3272B9` →
`#30297E`. Links `#1a73c7`, underlined. Body text `#333333`, muted `#6B7280`.

**Two-column rule:** the image row and the text row are separate tables, each 50/50. Keeping them
separate is what holds the two headlines on the same baseline when the bodies differ in length. With
one piece, both rows go full width. With three, stack at 100% rather than cramming a third column.

---

## 8. Image placeholders

Never generate these. Emit a labelled box stating what belongs there and at what size.

Required per edition:

| id | What it needs | Size |
|---|---|---|
| `img-header` | Gradient banner with the comms month on it | 800 × 250 |
| `img-piece-1` | Product screenshot of piece 1 | 400 × 300 |
| `img-piece-2` | Product screenshot of piece 2 | 400 × 300 |

Placeholder markup, inline-styled so it renders as a visible labelled box:

```html
<div id="img-piece-1" style="height:300px;background:#e8eefb;border:2px dashed #3272B9;
     display:flex;align-items:center;justify-content:center;text-align:center;
     font-family:'Poppins',Helvetica,Arial,sans-serif;font-size:13px;color:#30297E;padding:16px;">
  IMAGE PLACEHOLDER – img-piece-1<br>
  Screenshot: [feature name]<br>
  400 × 300
</div>
```

Swapping in the real image means replacing the `<div>` with
`<img src="..." width="400" style="display:block;width:100%;height:auto;" alt="[feature]">`. Keep the
`id` on the `<img>` so the next edition's pass can find it.

---

## 9. Footer

Fixed content, carried forward unchanged every edition. Verify before reuse; don't retype from memory.

- LinkedIn line: `Never miss an update, follow us on LinkedIn.`
- **United States of America** – 838 Walker Road, Suite 21-2, Dover, DE 19904
- **United Kingdom** – 5 Churchill Place, Canary Wharf, London E14 5HU
- **South Africa** – Great Westerford, Unit SG110, 240 Main Road, Rondebosch, Cape Town 7700
- **United Arab Emirates** – Office 225, Floor 38, API Trio Tower, Al Barsha, Dubai
- Legal row: Unsubscribe · Manage Preferences · Contact Us

---

## 10. Worked example – September 2026

Two pieces, from tickets
[Locked project screen shows every locking reason at once](https://app.clickup.com/t/869edjq5q) and
the KANON re-identification help work.

**Piece 1**

> **Locked Projects: See Every Blocking Issue At Once**
>
> When a project locks for more than one reason, you can now see every blocking issue at once, each
> with the details you need to fix it.
>
> Contact support opens a pre-filled chat, so it all gets sorted in one conversation.

**Piece 2**

> **How We Protect Your Data From Re-identification**
>
> When you add a dataset to a project, Omnisient may remove records or columns that could constitute a
> re-identification risk. This can reduce the size of your dataset, which is expected and not an
> error. Select the shield icon to investigate what changed and why.

Note what both do: open with the reader's situation, state the change in one sentence, close with the
action available. Neither mentions a ticket, a sprint, or a client.

---

## 11. Disclosure checklist

Run against the fully assembled copy before saving – intro, every headline, every body, every image
label, every link. This email reaches every platform user, so a leak here reaches customers.

- **No client names.** `Shoprite`, `SRX`, `TransUnion`, `TU`, `Absa`, `Standard Bank`, `Rainmaker`,
  `FNB`, `AirVantage`, `Altron`, `ZIP` and any other client, in any form including abbreviations. A
  cross-client email names no client, even as an example. Watch the Development Summary especially:
  it routinely names the client who asked for the feature.
- **No person names, emails or ClickUp handles**, including whoever wrote the ticket.
- **No ticket IDs, dev story codes** (`MAC 01-03`, `FMCG 04a-02`), **sprint numbers, squad names,
  codenames or board URLs.**
- **No internal-only roadmap language** – "planned to adopt next", "a follow-on story", "coming in a
  future sprint". The email covers what shipped.
- **Nothing described as live that isn't.** Check the ticket for a DO NOT PUBLISH warning or a
  not-yet-shipped note before using its copy at all.
- **No competitor references.**

A hit is not something to fix silently. Name it, show the line, and ask before changing or cutting
it. If any hit is unresolved, don't save.

---

## 12. How newsletter items are marked on the board

The board nests comms deliverables as subtasks under the thing they describe. Two different tickets
are both called "newsletter" and only one is a news piece:

- **`Newsletter Section`** – a subtask hanging off a **feature ticket**. The feature ticket (its
  parent) holds the copy. **This is a news piece.** Example: `Newsletter Section` (`869f9p04k`)
  under [Dataset Discovery Widget in SQLPad](https://app.clickup.com/t/869f9nzy0).
- **`Newsletter`** – a subtask under the `[Month] Release [Year]` container, with an empty
  description. It means "the newsletter must go out" and carries no content. **Never a news piece.**

So a news piece is always **the parent of a `Newsletter Section` subtask**, never the subtask and
never the container.

Two traps worth knowing, both seen on the live board:

- **Board templates carry the same subtask names.** The `Major Release` / `Minor Release` /
  `Patch Release` / `Hotfix Release` template tasks each have their own `Newsletter Section` child.
  These are blank scaffolding, not features. A real news piece's parent has a Release Window set and
  real copy under `### Release Comms Description`.
- **A marked ticket can belong to another window.** Check the parent's `Release Window` against the
  sprint window before keeping it; a `Newsletter Section` marked early sits on a future month's
  ticket.
