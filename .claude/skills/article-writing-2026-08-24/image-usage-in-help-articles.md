# Image Usage in Help Center Articles

Standards for deciding whether, what kind, and where to use an image in a help article. Forward-looking: applies to new and edited articles, not a retrofit of what's already published.

Placement follows the image's purpose, not a fixed position. This mirrors established practice: Google, Microsoft, and GitLab's documentation style guides all place screenshots by function, not by a single layout rule. What's fixed here: the test for whether an image belongs at all, image type selection, accessibility, and privacy.

---

## Table of Contents

1. [The core test](#the-core-test)
2. [Deciding whether to use an image](#deciding-whether-to-use-an-image)
3. [Choosing the image type](#choosing-the-image-type)
4. [Placement: match the job](#placement-match-the-job)
5. [Screenshot and diagram craft standards](#screenshot-and-diagram-craft-standards)
6. [Accessibility](#accessibility)
7. [Privacy: PII in screenshots](#privacy-pii-in-screenshots)
8. [Maintenance and staleness](#maintenance-and-staleness)
9. [Pre-publish checklist](#pre-publish-checklist)
10. [Sources](#sources)

---

## The core test

> Use an image only when it communicates something faster or more clearly than text — never because it "looks nice" or fills space.

Two equivalent phrasings, from Google and Microsoft's style guides respectively:
- **Google:** use images only for information that's difficult to express in words, or for a UI screenshot that's central to the discussion.
- **Microsoft:** use a screenshot when it saves words.

If you can't finish the sentence *"without this image, the reader would have to..."* with something concrete, don't add it.

This cuts both ways. GitLab's guidance is the counterweight: use images **sparingly**, because every image is a standing liability — it goes stale the moment the UI changes, it's expensive to localize, and it's invisible to screen readers. On a platform that ships UI changes every sprint, an unnecessary screenshot isn't neutral — it's a future correction waiting to happen.

---

## Deciding whether to use an image

Answer these in order. Any "stop" answer means don't add the image.

1. **Does the surrounding text already answer what to click, what to expect, or how it works?**
   - Yes → **stop.** The image would be decoration, not information.
   - No → continue.
2. **Could a bolded UI label, a short table, or a numbered list answer it instead, at similar length?**
   - Yes → **stop.** Use the cheaper option — same clarity, no maintenance cost.
   - No → continue.
3. **The image is justified. Which job is it doing?** This decides its placement (see [Placement](#placement-match-the-job)) — pick whichever fits best; it's fine if it does two:
   - **Orient** — shows the reader a screen or section they haven't seen yet.
   - **Confirm** — shows the result of an action or command just described.
   - **Explain** — shows a flow, process, or relationship that would take several sentences to describe.

---

## Choosing the image type

| Image type | Use when | Don't use when |
|---|---|---|
| **Full or cropped screenshot** | Orienting the reader to a real screen, or confirming what an action/command produces. | The thing being shown is mostly text or code — use a real code block instead (screenshotted text can't be copied, searched, or read by a screen reader). |
| **Diagram** (flowchart, sequence, relationship map) | A multi-step process, a multi-party interaction, or conditional/branching logic that would take several paragraphs to describe in prose. | The concept is a simple 2-3 item list or a single linear fact — a table or bullets will do. |
| **Decorative/hero image** | Release note article headers, or similar visual-identity banners. Doesn't carry information the reader needs to complete a task. | As a substitute for an orientation screenshot — decorative images convey no functional information, so they shouldn't be relied on to teach anything. |

---

## Placement: match the job

| Job | Where it goes | Why |
|---|---|---|
| **Orient** | After a short intro sentence naming what the reader is about to see, before the detailed prose or table that follows. | The reader needs a line of context first, then the screen, then the detail — not the screen cold with no framing. |
| **Confirm** | Immediately after the instruction, command, or code snippet it illustrates. | Cause and effect should sit together — text says "run this," image shows what came back. |
| **Explain** (diagrams) | After a one-sentence lead-in ("Here's what happens during sign-in:"), inside its own heading if the concept is substantial enough to warrant one. | The image needs a frame before it lands; a dedicated heading signals "this is worth slowing down for." |

If you're placing an image and none of these three descriptions fit what it's doing, that's a sign the image itself isn't earning its place — revisit [the core test](#the-core-test).

> **Step-by-step and setup guides:** Confirm can repeat once per step rather than once per section — a guide like configuring SSO or connecting a database, where each step is a distinct, unfamiliar field or screen, earns a screenshot at each step. This doesn't override the core test: each screenshot still has to pass "would the reader be lost without it" on its own. Don't screenshot self-evident steps (e.g., "click Save") just to keep a visual rhythm going.

---

## Screenshot and diagram craft standards

**Data.** Use dummy data, never real platform data — build screenshots from a demo/sandboxed setup with realistic-looking but fabricated content. This removes PII redaction as a step entirely: if nothing real is ever in frame, there's nothing to hide after the fact.

**Framing.** Crop and frame to match the image's job. Orient screenshots can show full context (whole screen, sidebar included) to establish where things are. Confirm/step-detail screenshots can be tightly cropped or zoomed to a specific element — once the reader's oriented, precision matters more than context. Consistency means your Orient shots resemble each other and your Confirm shots resemble each other.

**Capture technique.** If the instruction is "click this," capture the element in its hover state, not its resting state. Add the cursor icon back in afterward in Figma — most screen-capture tools don't include it cleanly.

**Visual identity.** Every image — screenshot or diagram — is exported as PNG (Intercom doesn't support SVG), at 2x resolution to reduce blurring when the reader zooms in, with a 1px solid border in Gray03 (`#DBDCDD`) and 5px rounded corners.

**Annotation toolkit.** The fixed set of tools for drawing attention within a screenshot — pick whichever fits the moment, but apply it the same way every time it appears:
- **Blur** — emphasis only, never redaction. De-focuses the UI around a specific element to draw the eye there.
- **Numbered circles** — use when a screenshot (or diagram) has several distinct elements you want to call out individually, each described in the surrounding text. Primary blue ramp (Light/Normal/Dark); vary the shade across badges in the same image for visual interest.
- **Highlight border** — use to draw the eye to a specific action or function, similar to blur but more visually assertive — well suited to step-by-step articles calling out one thing at a time. 2px solid `#FF0000`, 5px rounded corners.

**Diagrams.** Keep diagrams simple enough to read at a glance — if a diagram needs its own explanation to be understood, it's doing the job prose should be doing. Introduce every diagram with a complete sentence before it appears, and follow Google's guidance: don't rely on the diagram alone to carry information a screen-reader user would otherwise miss — restate the key steps in the surrounding text.

---

## Accessibility

- **Every informative image gets alt text** that summarizes its *intent*, not just its contents — describe what the reader should take away, in 155 characters or fewer.
- **Purely decorative images get empty alt text** (`alt=""`) — don't force a description onto an image that carries no information (a title banner, for example).
- **If an image carries more information than fits in alt text**, put a short summary in the alt attribute and the fuller explanation in the surrounding text — never only in the image.
- **Name image files descriptively before export** (e.g. "How OIDC Works in Omnisient.png," not "Frame 5.png") — Intercom surfaces the filename to screen readers, so a generic export name is itself an accessibility gap, not just an asset-organization one.

---

## Privacy: PII in screenshots

This matters more for us than for a typical SaaS product, given what the platform handles.

- **Fake the data before you capture, not after.** Use a demo/sandboxed environment, or fake the data directly via the console, so no real customer or partner data is ever in frame to begin with.
- **Never rely on blur or mosaic effects** to obscure PII — both can be reversed to recover the original data. This is why faking the data upfront matters more than any redaction technique after capture.

---

## Maintenance and staleness

- Screenshots of frequently changing UI (project creation flows, dataset configuration, anything actively in sprint work) carry the highest staleness risk — flag these for review whenever the underlying feature ships a UI change.
- Diagrams of architecture or multi-system flows carry the same risk if the *underlying mechanism* changes, even if no screenshot is involved — an OIDC flow diagram would need a revisit if the auth sequence itself changed, independent of any UI change.
- When restructuring or substantially editing an article, treat outdated images as a launch blocker for that edit, not a "someday" cleanup item.
- **Keep the editable Figma file for every image**, not just the exported PNG. When the underlying UI or flow changes, you can update the source and re-export instead of rebuilding the capture, border, and annotations from scratch.

---

## Pre-publish checklist

Before an image goes into a published article, confirm:

- [ ] I can finish "without this image, the reader would have to..." with something concrete.
- [ ] The image type (screenshot vs. diagram vs. decorative) matches what I'm actually trying to show.
- [ ] Placement matches the image's job (orient / confirm / explain).
- [ ] Screenshot/diagram uses dummy data, not real platform data.
- [ ] Framing matches the image's job — full context for Orient, tight crop/zoom for Confirm.
- [ ] If it shows a clickable element, it's captured in hover state with the cursor added in Figma.
- [ ] Border (1px Gray03), 5px corners, and 2x export resolution are applied.
- [ ] Alt text is set (or intentionally empty, for decorative images).
- [ ] Filename is descriptive, not a generic export name.
- [ ] Editable Figma source is saved, not just the exported PNG.

---

## Sources

- [Diagrams, figures, and other images — Google developer documentation style guide](https://developers.google.com/style/images)
- [Write accessible documentation — Google developer documentation style guide](https://developers.google.com/style/accessibility)
- [Write helpful alt text — Google Technical Writing](https://developers.google.com/tech-writing/accessibility/self-study/write-alt-text)
- [Documentation Style Guide — GitLab Docs](https://docs.gitlab.com/development/documentation/styleguide/)
- [Screenshots — Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/writing-style-guide-msft-internal/images-video/screenshots)
- [Documentation diagrams: when to use them and how to keep them accurate — Mintlify](https://www.mintlify.com/library/when-and-how-to-use-diagrams)
- [A Simple Guide to Using Screenshots in Technical Documentation — Archbee](https://www.archbee.com/blog/screenshots-in-technical-documentation)
- [Visual Documentation: Best Practices for Tech Docs — Heretto](https://www.heretto.com/blog/visuals-in-technical-documentation)
