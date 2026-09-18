# Definition of Ready and Done

# The Definition of Ready (DoR)

The **Definition of Ready** is a **checklist** that ensures a user story is clear, complete, and understood before the team starts working on it.
It answers the question: _"Is this story ready for the team to pick up in a sprint?"_
If a story doesn't meet the Definition of Ready, **it goes back for refinement** before being added to a sprint.

## The importance of the Definition of Ready

| **Purpose** | **Explanation** |
| ---| --- |
| **Clarity for everyone** | Business and technical teams share the same understanding of the work. |
| **Prevents wasted effort** | Developers don't start on incomplete or unclear stories. |
| **Speeds up delivery** | Work flows smoothly in the sprint because the team doesn't need to pause to get information and potentially back track to redo work. |
| **Improves quality** | Well-prepared stories include acceptance criteria and dependencies, reducing rework. |

## Definition of Ready Checklist

| **Item** | **Description** | **Ready** |
| ---| ---| --- |
| Clear and concise | Story is written in INVEST style |  |
| Acceptance criteria defined | The criteria are well defined |  |
|  | The criteria are Testable |  |
|  | Functional requirements are defined |  |
|  | Non-Functional requirements are defined |  |
| UI/Design | Screen flows, wireframes, or mock-ups are available |  |
|  | New vs. Existing elements are clear |  |
|  | Information that should surface on the UI is defined |  |
| Dependencies identified | External teams |  |
|  | Data, such as data for testing |  |
|  | New Azure or other Resources |  |
| Effort estimated | Story has been sized by the team (e.g., story points). |  |
| Architecture (ARB) reviewed | The **Simple ARB Process** has been consulted to determine if the change needs an ARB review. Private ([https://app.clickup.com/9012824942/docs/8ck9jve-22052/8ck9jve-22172](https://app.clickup.com/9012824942/docs/8ck9jve-22052/8ck9jve-22172)) |  |
| Priority established | Product Owner has ranked the Epic/User Story |  |

---

# Done vs. Closed Guidelines

## When is something Done?

The concept of _Done_ is about ensuring transparency on the state of work. Agile emphasizes small, testable increments. By defining _Done_ as "ready for QA," we allow faster feedback and avoid bottlenecks, while keeping progress visible.

*   **Done** means the scoped work for the task is complete.
*   For a development task, done means the following:
    *   The task is ready for **QA to test**. The task is ready for QA to test when the following is true:
        *   The task has been **dev tested** locally.
        *   The task has been released to the relevant environment (Dev, QA, Demo).
        *   The task has been **dev tested** on the relevant environment (Dev, QA, Demo).
*   If QA discovers a bug during testing, they will log a **new task**. Ideally, that bug should be linked back to the original task to preserve traceability.

## When is something Closed?

Closure reflects true _value delivery_. A task is considered **Closed** once all of the following are true:
*   The **Acceptance Criteria (AC)** for the user story have been met and checked off.
*   It has been **released**.
*   It has been **tested in production**.
    *   QA has **validated the results.**

---

# Bug Tracking Guidelines

The below approach keeps the board clean, avoids confusion about what's "Done," and ensures bugs are tracked, prioritized, and resolved transparently.

## Why separate bug tickets?
Bugs can easily get lost if they're just comments or checklist items inside a larger task. Having **dedicated bug ticket(s)** ensures visibility, proper prioritization, and clear reporting. It also makes it easier to track bug trends, ownership, and resolution times.

## How we handle bugs
1. **Create a separate ticket** for every bug found.
    *   Give the bug ticket a clear title.
    *   Include reproduction steps, screenshots/logs if available.
2. **Link the bug ticket to the original task.**
    *   This maintains **traceability** back to the source work.
3. **Close the bug ticket separately.**
    *   Once fixed and verified, rather than rolling it into the original feature task.
