# Agile Process

# What is Agile Development
**Agile** is a way of working that delivers value in **small, usable pieces**, instead of waiting for one big release.
*   The business defines what is important.
*   Teams build it in short cycles (2 to 4 weeks), get feedback, and adjust quickly.
*   The focus is on **collaboration, transparency, and continuous improvement**, so we deliver what users actually need.
*   A key benefit is that projects and features are delivered to **end users faster**, creating value sooner.

# Typical Agile Development Flow
1. **Product Owner Prioritizes the Product Backlog**
    1. Continuously refines and prioritizes backlog items based on business value, stakeholder input, and user feedback.
    2. Ensures that the backlog reflects the current strategic goals of the business.
2. **Product Owner Creates User Stories**
    1. Prioritised projects and work items are broken down into user stories from the end-user's perspective.
3. **Product Backlog Refinement with Technical Team**
    1. Product Owner and Technical Team collaborate to review and refine user stories.
    2. Estimate effort (story points or duration) and clarify requirements.
4. **Technical Team Defines Technical Stories where needed**
    1. These stories may or may not be linked directly to user stories, but they must be scheduled in the sprint just like user stories.
5. **Team breaks Stories into Tasks**
    1. Each story is broken down into executable tasks.
    2. Tasks can include coding, configuration, test setup, and documentation.
6. **Test-Driven Development (TDD) and Test Case Creation**
    1. Before writing the code, the team writes test cases.
    2. Tests cover unit, integration, and acceptance testing.
7. **Development and Testing in Parallel**
    1. Developers write code to make the tests pass.
    2. Tests are continuously run via automated CI pipelines or through manual testing.
8. **Sprint Review / Demo**
    1. At the end of each sprint, the team demos what was built.
    2. Stakeholders provide feedback.
9. **Retrospective**
    1. The team reflects on what went well and what can improve.
    2. Action items are logged and tracked.
10. **Repeat**
    1. The cycle continues — each sprint builds on what was learned and delivered before.

# What is a Sprint
A **sprint** is a **fixed-length development cycle** (typically 2–4 weeks) where the team commits to delivering a specific set of work items.

## The core definitions of the sprint process
*   **Sprint Backlog:** The sprint backlog is the list of work committed to for that sprint.
    *   The sprint backlog should include a healthy mix of items between:
        *   Features (User and Technical Stories from the Product Backlog)
        *   Bugs
        *   Technical Debt
*   **Sprint Goals:** A short statement that describes the **most important outcomes** the team aims to achieve in the sprint.
    *   Sprint goals help focus the team's efforts and guide decision-making during the sprint. They give meaning to the work beyond just "finishing tickets."
*   **Sprint Review / Demo:** A session at the end of each sprint where the team **demonstrates completed work** to stakeholders and collects feedback.
*   **Retrospective:** A team-internal meeting at the end of each sprint to reflect on what went well, what didn't, and what can improve.

## Ownership in Agile
*   **Product Owner / Manager** — Owns the "what" and "why." Defines priorities, writes stories, and ensures the team builds the right thing.
*   **Tech Lead / Engineering Manager** — Owns the "how." Ensures technical quality, architecture alignment, and delivery feasibility.
*   **Team Members** — Own task execution. Responsible for estimation, delivery, and quality within their scope.
*   **QA** — Owns validation. Ensures acceptance criteria are met and quality is maintained.

## Sprint Goals
Sprint goals should be aligned to the broader quarterly or business goals and reviewed each sprint.

## Sprint Planning
Sprint planning is a collaborative session where the team selects items from the product backlog to commit to for the upcoming sprint.

# How does work get from the Product Backlog into Sprints
The **Product Backlog** is the single, prioritised list of all work the team could do. It is owned and maintained by the Product Owner, and is the source from which work is pulled into sprints.

**Work flows into a sprint through the following process:**
1. The Product Owner prioritizes items in the Product Backlog.
2. The team refines the top items (adds details, acceptance criteria, estimates).
3. During Sprint Planning, the team pulls the highest-priority, "ready" items into the Sprint Backlog.
4. Only items that meet the **Definition of Ready** should be pulled in.

## Understanding our Product Backlog
*   Our Product Backlog is separated into a number of lists, namely:
    *   **Product Backlog (Product Roadmap):** Will contain all the features and priorities from the product backlog.
    *   **Platform Backlog (Sprint Backlog):** Will contain all the items that are allocated to sprints.
    *   **Bug Backlog:** Will contain all the bugs and they should also be allocated to Sprints.
    *   **Technical Debt/Refactoring:** Will contain work items to refactor code or architecture.
    *   **Enhancements**: Will contain enhancements to existing features/product capabilities.
    *   **R&D (Spikes)**: Will contain **Spikes**, i.e. work that requires investigation.

## Backlog prioritization Techniques
*   **MoSCoW** — Must have, Should have, Could have, Won't have (this time). Good for scope discussions.
*   **RICE** — Reach, Impact, Confidence, Effort. Scores items to rank objectively (see [RICE Framework](RICE_Framework.md)).
*   **Weighted Shortest Job First (WSJF)** — Factors in cost of delay and duration for flow-based teams.
*   **Kano Model** — Classifies features by customer satisfaction impact (must-haves vs. delighters).
*   **Value vs. Effort Matrix** — Quick visual sorting into quick wins, big bets, money pits, and thankless tasks.

## Other types of Backlogs
*   **Bug Backlog:** Will contain all the bugs and they should also be allocated to Sprints.
*   **Technical Debt/Refactoring:** Will contain work items to refactor code or architecture.
*   **Enhancements**: Will contain enhancements to existing features/product capabilities.
*   **R&D (Spikes)**: Will contain **Spikes**, i.e. work that requires investigation.

# Retrospective
## Discussion Guidelines
*   What went well?
*   What didn't go well?
*   What can we do differently?
*   Start / Stop / Continue — What should we start doing, stop doing, and keep doing?
*   Action items from the retro should be tracked and followed up in the next sprint.

## Techniques
*   **Start, Stop, Continue** — Simple and fast.
*   **4Ls** — Liked, Learned, Lacked, Longed For.
*   **Fishbone / 5 Whys** — Root cause analysis for recurring problems.

# Other common terms
*   **Velocity** — The average number of story points a team completes per sprint. Used for forecasting, not performance measurement.
*   **Burndown** — A chart showing remaining work in a sprint or release. Helps visualize if the team is on track.
*   **WIP Limit** — A cap on how many items a person or team can have "in progress" at once. Encourages focus and reduces context-switching.
