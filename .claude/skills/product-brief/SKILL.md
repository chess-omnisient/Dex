---
name: product-brief
description: Extract product ideas through guided Socratic questioning and generate a Shaped Solution PRD
---

## Purpose

Extract product ideas from your head through guided questioning, then generate a Shaped Solution PRD. Acts as your product thought partner — asking the right questions, challenging assumptions, and pushing for evidence before structuring everything into a PRD ready for stakeholder review.

## The Problem This Solves

You have an idea for a product or feature but need help articulating it clearly and rigorously. This command walks you through each PRD section conversationally, using Socratic questioning to sharpen your thinking — then generates a Shaped Solution PRD in the format your team uses.

## Usage

```
/product-brief [initial idea]
```

**Examples:**
- `/product-brief Add a notification system to our app`
- `/product-brief Build a customer feedback portal`
- `/product-brief` (prompts you for the idea)

---

## Context Loading (Silent)

On invocation, silently read:
1. `System/user-profile.yaml` — company context, role, communication preferences
2. `System/pillars.yaml` — strategic pillars for alignment checks
3. `.claude/skills/ada/references/company-tech-stack.md` — platform and tools
4. `.claude/skills/ada/references/operational-constraints.md` — cost, compliance, capacity constraints
5. `.claude/skills/product-brief/references/socratic-techniques.md` — questioning techniques

Do not recite this context. Use it naturally to inform questions and challenge answers. Reference marketplace dynamics (buyer/seller), tech stack constraints, and strategic pillars where relevant.

---

## Process Flow

### Phase 1: Capture Initial Idea

**If no idea is provided:**
Ask: "What product or feature are you thinking about?"

**If idea is provided:**
Start with whatever the user provides — 1 sentence to several paragraphs. Don't judge, just absorb.

Display:

```markdown
## Initial Idea

[User's description]

---

**Next:** I'll walk you through the key sections of the PRD — Problem, Appetite, Solution, Boundaries, and Success Metrics. We'll have a conversation about each one.
```

---

### Phase 2: Problem Framing

**Goal:** Ensure the problem is real, specific, and worth solving now.

Ask 2-3 questions at a time from this set, adapting based on answers:

- **What specific pain point are we solving?** (For data buyers, sellers, or both?)
- **What evidence do we have that this is a real problem?** (Customer feedback, usage data, lost deals, seller churn?)
- **Who experiences this problem most acutely?** (Segment, vertical, use case?)
- **What happens if we don't solve this?** (Revenue impact, competitive disadvantage, user friction?)
- **How does this problem impact our key metrics?** (Adoption, engagement, monetization, marketplace liquidity?)

**Socratic techniques to apply:**
- **Evidence pressure** — if answers are vague ("users want better..."), push: "How do we know? What data or conversations support that?"
- **Inversion** — "What happens if we DON'T build this? What's the real cost of inaction?"
- **Red flag detection** — watch for solution-first thinking (describes feature but can't articulate problem), vague language, no evidence

After answers, briefly synthesize:
> "So the core problem is [X], primarily affecting [Y], with evidence from [Z]. Moving on to appetite..."

---

### Phase 3: Appetite & Constraints

**Goal:** Set a time box and understand strategic fit. The appetite constrains the scope — the solution must fit within this box.

Ask 2-3 questions:

- **How much time are we willing to invest?** (Small batch = 2 weeks, Big batch = 6 weeks)
- **What's the opportunity cost?** What are we NOT doing if we pursue this?
- **Why is this the right thing to build RIGHT NOW?** What changes if we wait 6 months?
- **What resources are available?** (Team composition, availability, dependencies)
- **Does this align with our quarterly priorities and strategic pillars?**

**Socratic techniques to apply:**
- **Strategic timing test** — "Why now versus next quarter? What's truly urgent here?"
- **Resource forcing** — "If you had half the time, what would you cut from this?"
- **Pillar alignment** — silently check against `pillars.yaml` and surface fit or misalignment

---

### Phase 4: Solution Shaping

**Goal:** Define the solution at "fat marker sketch" altitude — high enough to leave room for the build team, specific enough to be implementable.

Ask 2-3 questions:

- **What's the core concept in 2-3 sentences?**
- **How will data buyers interact with this? How will data sellers?**
- **What's the simplest version that solves the core problem?**
- **Are there existing patterns in our platform we can leverage?**
- **What does the basic user flow look like?** (Walk me through the steps)

**Socratic techniques to apply:**
- **Alternative challenge** — "What other approaches did you consider? Why this one over [obvious alternative]?"
- **Evidence pressure** — "Why is this the right solution for that problem? What's the logical connection?"
- **Resource forcing** — "Is there a simpler version that gets us 80% of the value?"
- **Tech stack awareness** — silently consider the company's tech stack and architecture (loaded from company-tech-stack.md). If the solution implies significant technical lift, flag it: "This touches [system] — have you validated feasibility with engineering?"

#### Visual Shaping (Optional)

After the user describes their solution and user flow, offer:

> "You've described a clear flow. Want me to generate a breadboard diagram to visualize the places and connections? It helps spot missing paths and makes the PRD more concrete for stakeholders."

If yes:
1. Extract Places, Affordances, and Connections from the conversation so far
2. Silently load `.claude/skills/shape/references/breadboard-patterns.md` and `.claude/skills/shape/references/fat-marker-patterns.md`
3. Generate a Mermaid breadboard diagram inline and confirm with the user
4. If the user also described screen layouts, offer a fat marker sketch
5. Include generated diagrams in the PRD's Solution section when Phase 8 generates the document

If no, proceed to Phase 5 as normal.

This invokes `/shape` logic inline — it does not require the user to exit the product-brief flow. The diagrams become part of the PRD output.

---

### Phase 5: Boundaries

**Goal:** Identify rabbit holes that could derail the project and explicitly define what's out of scope.

**Rabbit Holes** — ask:
- **What technical unknowns could balloon scope?** (Complex integrations, data quality issues, scalability?)
- **Where might we get stuck on data seller requirements or customizations?**
- **What dependencies on external parties exist?**
- **What perfectionist tendencies might derail us?** (Over-engineering, endless design iterations?)

**No-Gos** — ask:
- **What features are "nice to have" but NOT essential for this version?**
- **Which user segments or verticals are we explicitly not targeting in v1?**
- **What integrations or third-party tools are out of scope?**

**Socratic techniques to apply:**
- **Inversion** — "What would make this project fail? What's the most likely way we blow past the appetite?"
- **Scope discipline** — if scope sounds large, flag early: "That sounds like it might exceed a [X]-week appetite. What could we cut?"

---

### Phase 6: Success Criteria

**Goal:** Define measurable outcomes so we know if this worked.

Ask 2-3 questions:

- **What's the primary metric we're trying to move? By how much?**
- **What would make you consider this feature a failure?**
- **What's the adoption target?** (Not all features need 100% adoption)
- **What would you check 30 days after launch?**
- **Are there leading indicators we can track before the primary metric moves?**

**Socratic techniques to apply:**
- **Specificity pressure** — "Improve engagement" isn't a metric. Push: "Increase what, for whom, by how much, in what timeframe?"
- **Inversion** — "What outcome would tell us we got this completely wrong?"

---

### Phase 7: Confirm Understanding

Before generating the PRD, play back what was captured and confirm:

```markdown
## What I Heard

**Problem:** [Synthesized problem statement with evidence]

**Target:** [Who this is for — segment, persona]

**Appetite:** [Time box and resources]

**Solution:** [Core concept at fat marker level]

**Rabbit Holes:** [Top 3 risks and mitigations]

**No-Gos:** [Key exclusions]

**Success:** [Primary metric and target]

**Pillar Alignment:** [Which strategic pillar this supports]

---

### Definition of Done Check
- [ ] Problem is specific with supporting evidence
- [ ] Appetite is clear with time box and resources
- [ ] Solution is at the right altitude (not too detailed, not too vague)
- [ ] Rabbit holes are identified with mitigations
- [ ] No-gos are explicit
- [ ] Success metrics are measurable
- [ ] Both buyer and seller impact is considered
- [ ] This can realistically be built within the stated appetite

---

**Does this capture your thinking? Type "yes" to generate the PRD, or correct anything above.**
```

If user corrects, update and re-confirm.

---

### Phase 8: Generate PRD

User triggers with: `yes`, `generate`, `create prd`

Generate the Shaped Solution PRD using the template in `references/shaped-prd-template.md`. Fill in all sections with the information gathered during Phases 2-6.

**Output quality checks before finalizing:**
- Every section has substance (no empty placeholders)
- Problem statement includes evidence, not just assertions
- Appetite has specific time box and resource allocation
- Solution describes buyer AND seller elements
- At least 3 rabbit holes with mitigations
- No-gos are explicit enough to prevent scope creep during execution
- Success metrics are specific and measurable
- Completion checklist is honestly assessed

If any section is thin, flag it:
> "The [section] feels light — we didn't discuss [specific gap] during our conversation. Want to flesh it out now, or leave it as an open question in the PRD?"

---

### Phase 9: Save & Integrate

After generating the PRD:

1. **Save the document:**
   - Create folder: `04-Projects/[Product Name]/`
   - Save as: `04-Projects/[Product Name]/PRD.md`

2. **Create person pages** (if stakeholders mentioned):
   - For each stakeholder, check if person page exists
   - Create/update pages in `05-Areas/People/Internal/` or `05-Areas/People/External/`
   - Add note referencing this project

3. **Link to tasks:**
   - If immediate actions were mentioned, suggest creating tasks in `03-Tasks/Tasks.md`

4. **Pillar linkage:**
   - If a strategic pillar was identified, note it in the project folder

5. **Confirm completion:**

```markdown
## PRD Created

**Saved to:** `04-Projects/[Product Name]/PRD.md`

**Want to:**
- **Stress-test it** → Run `/ada review` to get engineering + product pushback before sharing
- **Revise a section** → Just tell me what to change
- **Create tasks** → Say "create tasks" to extract action items
- **Share with stakeholders** → I can draft a summary email
```

---

## Navigation Commands

At any phase, users can:

- `back` or `previous` — Return to previous phase
- `skip to prd` — Jump directly to PRD generation (uses whatever info gathered so far)
- `jump to [section]` — Jump to specific section (problem, appetite, solution, boundaries, success)
- `revise [section]` — Edit specific section
- `start over` — Begin from scratch
- `save progress` — Save current state as draft
- `definition of done` — Show the DoD checklist for current section
- `challenge me` — Ask for harder Socratic pushback on current section

---

## Conversational Style

- **Be a thought partner, not an interrogator** — 2-3 questions max before acknowledging
- **Challenge constructively** — "That's interesting, but help me understand..." not "That's wrong"
- **Adapt to depth** — if user gives detailed, evidence-backed answers, move faster. If vague, probe deeper
- **Keep momentum** — don't let it feel like homework. Acknowledge strong answers, build on them
- **Coach when stuck** — if user struggles with a question, offer options or examples from their context
- **Reference their world** — use company context naturally (marketplace dynamics, buyer/seller, data products — loaded from user profile and tech stack reference)

**Good:**
> "Interesting — if this is primarily for data buyers, how does the seller side benefit? Or are we creating value asymmetry that could hurt marketplace balance?"

**Bad:**
> "Question 4: Please describe the impact on data sellers."

---

## When to Use This Command

**Use `/product-brief` when:**
- You have a product idea but need help articulating it rigorously
- You need to write a PRD and want conversational guidance through each section
- You want your assumptions challenged before writing them down
- You're preparing a pitch for stakeholders

**Don't use it for:**
- Simple feature requests (just describe them normally)
- Already-written PRDs that need review (use `/ada review` instead)
- Technical implementation details (that's engineering's job, or use `/ada` in architecture mode)

---

## Integration with Dex System

- **Pillars:** Link PRD to relevant strategic pillar
- **Quarter Goals:** If this supports a quarterly goal, note it
- **Week Priorities:** Suggest adding "finalize PRD" to this week if urgent
- **People pages:** Auto-update stakeholders mentioned in the PRD
- **Tasks:** Offer to create tasks from the PRD's next steps
- **Ada:** Suggest `/ada review` as natural next step after generation

---

## Refinement After Creation

The PRD isn't set in stone. After creation:

- Say "refine the problem section" to iterate on any section
- Say "this scope is too big, help me cut it down" to trim
- Say "add a section on [topic]" to expand
- Run `/ada review` for engineering/product stress-testing

Dex will update the PRD file directly and maintain version history.

---

## Output Quality Checks

Before finalizing the PRD, verify:

- [ ] Clear problem statement
- [ ] Specific target audience
- [ ] Measurable success metrics
- [ ] Prioritized feature list (MVP vs later)
- [ ] Explicit out-of-scope items
- [ ] Key assumptions identified
- [ ] Dependencies called out
- [ ] Open questions captured

If any are missing, prompt user to fill gaps before finalizing.

---

## Track Usage (Silent)

Update `System/usage_log.md` to mark product brief as used.

**Analytics (Silent):**

Call `track_event` with event_name `product_brief_created`.

This only fires if the user has opted into analytics. No action needed if it returns "analytics_disabled".
