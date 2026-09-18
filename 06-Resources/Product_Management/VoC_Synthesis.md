# Voice of Customer Synthesis

**Source:** 8 VoC artifacts from `00-Inbox/` (SWOT analyses + meeting transcripts + feedback notes + burning issues workshop)
**Accounts covered:** FNB, Multichoice, Teljoy, Liberty, Shoprite (Lize + DS team), Nedbank, + general CX discussion
**Date range of source material:** Aug–Nov 2023, Nov 2025 (Shoprite burning issues)
**Synthesized:** 2026-02-28 | **Updated:** 2026-03-01 (Shoprite burning issues integration)

---

## Cross-Cutting Themes

### 1. Self-Service Gap (6/6 accounts — confirmed Nov 2025)
The most consistent finding, **reinforced strongly** by the Nov 2025 Shoprite burning issues workshop. Users across FNB, Teljoy, Liberty, Shoprite, Nedbank, and the CX discussion all rely heavily on Omnisient staff (Lee, Ronnie, Sharon) to create projects, extract data, and run analyses. The 80/20 self-service push is underway but hasn't fully landed.

**Evidence:**
- FNB: Don't create own projects, use Rainmaker's attribution reports
- Teljoy: Jonathan can't create own projects, gets Lee to set them up
- Liberty: "Often get Lee to run projects for them" — convenience factor on support availability
- Shoprite (Lize): Asks Ronnie to add engineered features to projects, can't extract scored data herself
- **Shoprite DS team (Nov 2025):** "Clients don't understand how to set up own projects... reliant on Omnisient to create projects, turnaround time getting longer and longer." Cannot add datasets to client projects themselves. Omnisient has to educate clients on data structure & sharing. "Omnisient steps in and does everything... clients repeat the same mistakes, creates more work and delays."
- CX Discussion (FNB): Previously Omnisient did everything, now transitioning to self-service
- Nedbank: Navigation confusion, education required before changes

### 2. Jupyter & Data Science Tools = Highest Value (3/6 accounts)
Jupyter Notebooks and SQL Pad are the most valued features for power users. Strong demand for more data science capabilities.

**Evidence:**
- Nedbank: Jupyter is "most valuable" feature — upload code, compare models, save work, document with markdown
- Shoprite (Lize): Jupyter is a "big value add," previously constrained by Azure environment delays
- CX Discussion: SQL Pad interest high, Jupiter Pad anticipation
- FNB: Strong Microsoft SQL background, SQL Pad access not yet explored despite being available

### 3. Performance & Stability (3/6 accounts — confirmed Nov 2025)
Timeout issues, slow loading, and processing waits create user anxiety and erode trust.

**Evidence:**
- Nedbank: Timeout "very bad" — kicks users out while working, creates anxiety and stress, feels "under pressure and on the clock"
- Shoprite: Old projects take a long time to load or fail to load entirely
- **Shoprite DS team (Nov 2025):** "You have to wait after every step for something to process or to get permission." Three primary waits: data upload, table registration, project creation. Bug resolution timelines "very unclear and usually very long." Processing dependencies mean navigating away kills running queries.
- FNB (SWOT): App slow when accessing reports and times out, slow when making selections

### 4. Feature Awareness Gap (3/6 accounts)
Users don't know what's available to them — features sit unused.

**Evidence:**
- FNB: Didn't know SQL Pad was available ("I had no idea")
- Shoprite (Lize): Didn't see the feedback button, didn't know about Canny
- Nedbank: Didn't know you could upload a notebook to Jupyter
- FNB: Didn't know about chat/knowledge base feature

### 5. Data Export & Download Friction (3/6 accounts — deepened Nov 2025)
Multiple accounts want to get data out of the platform more easily. The Nov 2025 workshop revealed this is not just about downloads — it's about the inability to work with aggregated results inline.

**Evidence:**
- Shoprite (Lize): Can't download scored data from Azure environment — waiting on Ronnie to extract member keys
- **Shoprite DS team (Nov 2025):** "Limited visualization tools available on the platform, only able to create visuals in Jupyter notebook (from which only screenshots can be taken)." No way to share insights with non-technical stakeholders. Quality checks and summary stats produce small tables that ideally you'd copy-paste into spreadsheets — but single-cell copy-paste is the only option. Model documentation (bad rate, accept rate, take-up rate tables) requires manual screenshot workflows.
- Nedbank: Wants to download notebook output/graphs directly from the app (Ronnie currently sends them)
- Liberty: Wants bulk download for "Save for own use" selections

### 6. Navigation & Onboarding (3/6 accounts)
First-time and occasional users struggle with navigation. Changes need better communication.

**Evidence:**
- Multichoice: Limited onboarding, some users prefer landing on datasets rather than dashboard
- Nedbank: Confused with navigation after mid-Jan layout change — "should have shown them before it happened"
- Shoprite (Lize): Initially confusing but "becoming more user-friendly over time"

### 7. Support Quality (6/6 accounts — universally strong)
Every single account praised support responsiveness and quality. This is Omnisient's strongest asset.

**Named in feedback:** Sharon, Lee, Ronnie/Rodney, Rudy
**Quotes:**
- Nedbank: "Happy with support"
- Shoprite: "You guys are really responsive... always available... very impressed"
- CX Discussion: "Fantastically happy... good relationship"
- Liberty/Teljoy: Support team availability noted as a convenience factor (but also a crutch blocking self-service)

### 8. Pricing Sensitivity (2/6 accounts)
Cost is a barrier for some use cases.

**Evidence:**
- Teljoy: Finds Shoprite/Rainmaker costs expensive, wants costs laid out upfront
- Nedbank: Can't justify Shoprite data cost for unbanked user identification alone — expanding to other bank teams may make it viable

### 9. Competitive Pressure (2/6 accounts)
- FNB: Finding Rainmaker helpful but thinks "Omnisient should be even easier and more feature-packed"
- Multichoice: "Competition from other analytics platforms may offer more competitive onboarding and user support"

### 10. Reusability & IP Preservation (1/6 accounts — NEW, Nov 2025)
Work created in projects is effectively trapped. Locked projects prevent code reuse, creating massive rework cycles. This is the second-largest pain point from the Shoprite burning issues workshop.

**Evidence:**
- Shoprite DS team: "Basically recreating the same work" — can't make small adjustments to existing code for different work. Projects lock quickly, preventing SQL copy. Can't download Jupyter notebooks. "Creates a lot of rework, and makes it impossible to reference old code for auditability/handover purposes."
- Examples: SBSA persona notebooks, Basketscore training and feature reduction notebooks all had to be rebuilt from scratch.
- Workaround: Start coding from scratch each project, or ask Omnisient to review and manually download/email notebooks.

### 11. Multi-Project Workflow (1/6 accounts — NEW, Nov 2025)
Users can only work on one project at a time. Any navigation away (to share a dataset, accept data, add a user, check sharing agreements) kills the running Jupyter VM or interrupts SQL queries.

**Evidence:**
- Shoprite DS team: "You are waiting for a big query like the lookalike to run, so you are stuck watching your query run without being able to navigate away." A 3-minute admin task interrupts hours of compute. Multiple user accounts offered as workaround but not sufficient.
- Omnisient acknowledged: "The team has done some research on this... current idea is to build a tab-like structure in the webapp that enables one browser tab to have multiple sessions open."

### 12. Database Organization & Discoverability (1/6 accounts — NEW, Nov 2025)
Growing data environments are becoming unnavigable without tribal knowledge.

**Evidence:**
- Shoprite DS team: "What is production vs dev vs sandbox tables? Getting messier by the day." At least 23 tables contain the word 'affluence' in the shoprite_a database. Workaround: ask each other or Omnisient what the correct table name is.
- Omnisient acknowledged: Thinking about table 'groups' or folders, initially for user permissions but could also serve as navigation.

### 13. Change Control & Incident Communication (1/6 accounts — NEW, Nov 2025)
Changes to the platform break existing processes without warning. Bug resolution lacks visibility.

**Evidence:**
- Shoprite DS team: "Sometimes changes are made that affect our existing processes with no communication." Discover broken code mid-project, then email Omnisient and wait. Examples: changes to lookalike, changes to retrospective prepared features table creation.
- Omnisient response: "We are redesigning our approach to testing... need to get better at communicating changes. There is usually a lot changing, and it's tricky to know what to communicate with whom."

### 14. Code Editing Limitations (1/6 accounts — NEW, Nov 2025)
Platform security constraints create friction in legitimate coding workflows.

**Evidence:**
- Shoprite DS team: Copy-paste limited to 250 characters in Jupyter, "quite tedious in terms of coding efficiently." Omnisient confirmed this is a security measure to protect the other party's data — clipboard rules apply globally to prevent data exfiltration via Jupyter.

---

## Feature Requests (Aggregated)

| Request | Accounts | Theme | Status (as of Feb 2026) |
|---------|----------|-------|------------------------|
| Self-service project creation | FNB, Teljoy, Liberty | Self-service | Open |
| Campaign activation / Activations capability | FNB, Liberty | New capability | **Addressed** — CENSUS implementation |
| Bulk download for selections | Liberty | Data export | Open |
| Download scored data from Azure | Shoprite | Data export | Open |
| Download notebook outputs/graphs from app | Nedbank | Data export | **Partial** — Aggregated exports from SQL Pad available under approval process. Spreadsheet.js embedding in progress (see ClickUp) may reduce need further. |
| Maximize Jupyter screen real estate | Nedbank | UX | **Addressed** — Jupyter opens in desktop app with less clutter |
| Learning Academy / structured training | Teljoy, Liberty | Onboarding | **Partial** — Academy exists but still emerging, not yet encouraged to clients |
| Dashboard redesign with interactive widgets | Teljoy, Liberty | UX | **Done** — Enhancing with Dashboard AI Builder agent (agentic approach) |
| Better project loading performance | Shoprite | Performance | Open |
| Timeout reduction | Nedbank, FNB | Performance | Open |
| Pre-change communication for UI updates | Nedbank | Change mgmt | **Addressed** — Pre-release emails, post-release emails, account manager warnings for big changes, Intercom articles, and popup showcases on first login after release |
| Self-service pricing/billing engine | Teljoy | Pricing | Open |
| CRM for customer onboarding trial | Teljoy | Internal ops | Open |
| Feature recommendation engine | Teljoy | Adoption | Open |
| Project/notebook/SQL reusability across projects | Shoprite DS | Reusability | Open — Omnisient considering a saved notebook/query library with approval process |
| Multi-project / multi-tab workflow | Shoprite DS | Productivity | Open — Omnisient researching tab-like structure with multiple sessions ([CU: 869ahgjhe](https://app.clickup.com/t/869ahgjhe)) |
| Project shareability with clients | Shoprite DS | Collaboration | Open — Security tension: projects designed as one-directional to protect IP ([CU: 869a700t2](https://app.clickup.com/t/869a700t2)) |
| Database table organization (groups/folders) | Shoprite DS | Data mgmt | Open — Omnisient considering table groups for navigation + permissions ([CU: 869a700tf](https://app.clickup.com/t/869a700tf)) |
| In-platform BI / visualization tools | Shoprite DS | Data export | Open — Related to spreadsheet.js embedding effort |
| Inline aggregated data copy-paste from SQL | Shoprite DS | Data export | **Partial** — Approval engine for aggregated downloads in progress ([CU: 8699hbn4k](https://app.clickup.com/t/8699hbn4k)) |
| Release communication to affected parties | Shoprite DS | Change mgmt | Open — Omnisient acknowledged gap, communicated with team |
| Increase Jupyter clipboard character limit | Shoprite DS | Productivity | Open — Security constraint, no clear resolution path |
| Contractor project creation on shared data | Shoprite DS | Self-service | Open — Prioritized, challenge is re-identification risk on features ([CU: 8699hxpp1](https://app.clickup.com/t/8699hxpp1)) |

**Removed from list:**
- ~~Access to engineered features in web app (Shoprite)~~ — Not a platform feature; this is a data-layer concern
- ~~Cleanroom module (Teljoy)~~ — Likely a misunderstanding during the original VoC session

---

## Strategic Implications

### For Product Strategy
- **Self-service is the #1 priority.** Every account touches this. Current reliance on staff doesn't scale. The Nov 2025 Shoprite workshop confirms the problem is getting worse, not better — "turnaround time getting longer and longer."
- **Jupyter/data science is the stickiest part of the platform** — but also the most friction-laden. Power users build workflows around it, yet can't reuse notebooks, can't work on multiple projects, and have a 250-char clipboard limit. Invest here for retention *and* productivity.
- **Reusability is an emerging strategic theme.** Locked projects destroy institutional knowledge and force rework. A notebook/query library with approval workflow could be a differentiator.
- **Feature discoverability needs work.** Users aren't finding existing features — the Learning Academy exists but isn't being encouraged to clients yet.

### For Product Delivery
- **Performance (timeouts, slow loading) still open.** The Nedbank "anxiety" feedback is a red flag. Shoprite DS team confirms: bug resolution timelines are "very unclear and usually very long."
- **Data export is progressing.** Approval engine for aggregated downloads in progress. Spreadsheet.js embedding underway. But inline BI tools still missing — users resort to screenshots from Jupyter.
- **Multi-project workflow is a major unaddressed pain.** Tab-like structure research underway but not yet prioritized. This is a daily productivity drain for data science teams.
- **Dashboard AI Builder agent** is the next evolution of the already-completed dashboard redesign.

### For Product & Market Performance
- **Competitive positioning against Rainmaker** needs attention — FNB explicitly compared them. CENSUS implementation addressed the activations gap.
- **Pricing transparency** could unlock Teljoy and Nedbank expansion.
- **Support quality is a strong differentiator** — protect it even as you push self-service.
- **Shoprite DS team's frustration level is high.** 10 burning issues documented in a formal workshop suggests risk to account health if velocity on fixes doesn't improve.

### For Process Excellence
- **Change communication: partially addressed.** Pre-release emails, popup showcases etc. now in place for general releases, but Shoprite DS team still reports broken processes without warning. Gap may be in communicating data/backend changes vs. UI changes.
- **Learning Academy exists but needs activation.** Flagged independently by Teljoy and Liberty — the infrastructure is there but needs to be encouraged to clients to reduce support dependency.
- **Database organization** is a growing tech debt problem. Table naming conventions and environment separation need attention before data environments become unmanageable.

---

## Source Files

| File | Account | Format |
|------|---------|--------|
| `00-Inbox/FNB.png` | FNB | SWOT screenshot |
| `00-Inbox/Multichoice.png` | Multichoice | SWOT screenshot |
| `00-Inbox/Teljoy.png` | Teljoy | SWOT screenshot |
| `00-Inbox/liberty.png` | Liberty | SWOT screenshot |
| `00-Inbox/CX Discussion...docx` | FNB (Brian, MJ, Karab) | Meeting transcript |
| `00-Inbox/Lize Shoprite...docx` | Shoprite (Lize) | Meeting transcript |
| `00-Inbox/Nedbank Feedback.rtf` | Nedbank | Feedback notes |
| `00-Inbox/202511 - Omnisient Burning Issues - Tickets.xlsx` | Shoprite DS team | Burning issues workshop (10 issues, 3 sheets incl. simplified categorization) |

---

*Created: 2026-02-28 | Updated: 2026-03-01*
