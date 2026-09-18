# User Stories and Estimation

# Work Item Allocation

**In order for Work Items to be allocated to Sprints, follow the process below:**

**Step 1:** Add the parent item (Epic, Theme, etc) to the Platform Backlog (or any other "Parent" backlog).
*   You don't have to add the child items, only the parent item.

These items will now appear in the **Platform Backlog**.
*   When you enable the "Lists" column you will see only the parent item will show that it is in the Product Roadmap (Parent List) and the Platform Backlog (Child List). This is correct.

Work items will be **allocated to sprints from this list**. Work items should not be added to sprints directly from any Parent List.

---

# What is a User Story?

A User Story consists of 2 components:

## User Story
*   A short, simple description of a feature or need, told from the end user's perspective.
*   Explains **what the end user wants** and **why it matters**, without technical detail.

## Acceptance Criteria
*   The minimum conditions that must be met for the story to be accepted as done.
*   Written from a **business perspective**, describing the required outcomes.
*   Acceptance Criteria helps stakeholders, QA, and developers agree on **"what success looks like."**

**Take Note:** All backlog items, whether **business features** or **technical tasks,** must be expressed as **user stories**. Even "purely technical" work should be framed in terms of **who benefits and why it matters**.

## User Story Format
We use a **simple template** to capture user stories: As a **[type of user],** I want **[what I need],** so that **[benefit / value].**

**Examples:**
*   _As a **customer**, I want **to reset my password online**, so that **I don't need to call support**._
*   _As a **data analyst,** I want **a daily sales report,** so that **I can track performance quickly**._

This format ensures the focus is on the **end user and the value delivered.**

## Good User Stories (INVEST)

| **Term** | **Purpose** |
| ---| --- |
| **Independent** | The story should stand on its own and not depend on other stories. |
| **Negotiable** | It's not a contract. Details can be discussed and refined with the team. |
| **Valuable** | The story must deliver value to the user or customer. |
| **Estimable** | The team must be able to size it (in story points or effort). |
| **Small** | It should be small enough for development to complete in 1 week - including design, testing and QA 2 weeks. |
| **Testable** | There should be **clear acceptance criteria,** so the team knows when it's done and so that QA can easily derive test cases. |

## Bad User Stories

**Should NOT describe technical tasks**
*   Bad: _"Create database table with 5 columns for storing customer data."_
*   Good: _"As a **sales rep**, I want **to capture customer details,** so that I can **follow up on leads**."_

**Should NOT be too big or vague**
*   Bad: _"Improve the reporting system."_
*   Good: _"As a **manager**, I want **a monthly sales summary by region**, so that **I can compare team performance**."_

**Should NOT dictate the solution**
*   Bad: _"Build this using Power BI and SQL stored procedures."_
*   Good: _"As a **business analyst**, I want **to visualize sales trends,** so that **I can spot growth opportunities**."_

**Should NOT miss the "why"**
*   Bad: _"As a user, I want a button to export data."_ (no context or benefit)
*   Good: _"As a **user**, I want **to export data to Excel,** so that **I can share reports with my team**."_

**Should NOT combine multiple unrelated needs**
*   Bad: _"As a customer, I want to reset my password, update my profile, and view my invoices."_
*   Good: Break this into **separate user stories, each delivering a clear value**.

---

# What are Acceptance Criteria

Acceptance criteria are **defined as part of the User Story.**
*   They are the **conditions that must be met for a user story to be considered complete**. They describe how the team and the business will know when the story delivers what was promised.
*   They are a **checklist of success**: If all the acceptance criteria are met, the story is done.

## How Acceptance Criteria fit in with User Stories
*   A **user story** explains **_who_** _needs_ **_what_** _and_ **_why_** (the business need).
*   The **acceptance criteria** explain _how we'll know it's been met_.
*   Together, they guide developers, testers, and business users so everyone is on the same page.

## The need for Acceptance Criteria

| **Purpose** | **Definition** |
| ---| --- |
| **Alignment** | They ensure business and technical teams have the same understanding of the requirement. |
| **Clarity** | They remove ambiguity by clearly defining what "done" means. |
| **Testability** | They allow QA/testers (and even business users) to verify that the story works as expected. |
| **Focus on value** | They tie the delivery back to the user's need and benefit, not just the technical output. |

## QA (Testing) and Acceptance Criteria
*   **QA considerations** are captured as part of **acceptance criteria** (the "T" in INVEST: _Testable_).
*   If the acceptance criteria are clear, unambiguous, and testable, QA can derive tests from them.
*   You don't need to write all test cases before the sprint, but you do need enough clarity, so QA knows **_how they'll verify the story_**.

---

# Good User Story Examples

## Business-Facing Feature
**User Story:** _As a **customer**, I want to **reset my password** via email so that **I can regain access to my account without calling support**._

**Acceptance Criteria**
*   Given I am on the login page, when I click **"Forgot Password"**, then I am prompted to enter my registered email.
*   When I enter a registered email, then I receive a password reset email within 5 minutes.
*   When I click the reset link, then I am taken to a secure page to set a new password.
*   The reset link expires after 24 hours.
*   If the email is not registered, then I see a generic message ("If this email exists, you will receive a reset link") for security reasons.

**This user story follows INVEST Principles:**
*   **Independent**: Doesn't rely on other stories.
*   **Negotiable**: Email vs SMS reset could be discussed.
*   **Valuable**: Saves customer and support time.
*   **Estimable**: Clear scope, easy to size.
*   **Small**: Can be done in one sprint.
*   **Testable**: Criteria are explicit and verifiable.

## Technical/Platform Story
**User Story:** _As a **DevOps engineer**, I want **application logs centralized in Azure Log Analytics** so that we can **monitor and troubleshoot production issues more effectively**._

**Acceptance Criteria**
*   All app services stream logs to the defined Log Analytics workspace.
*   Logs are searchable within 5 minutes of being generated.
*   Access to logs is restricted by RBAC (only DevOps + Support can query).
*   When a log ingestion failure occurs, an alert is triggered.

**This user story follows INVEST Principles:**
*   **Independent**: Can be implemented without waiting on other backlog items.
*   **Negotiable**: The destination could be Splunk or another tool if needed.
*   **Valuable**: Directly improves observability and MTTR.
*   **Estimable**: Config and testing are bounded.
*   **Small**: Narrow focus (just logging, no metrics or dashboards or anything like that).
*   **Testable**: Acceptance criteria map directly to QA/monitoring checks.

---

# Story Points

The purpose of story points is to serve as an abstract estimate of effort and complexity.
The story points should be assigned based on 'similar' historic stories. If this is the first sprint, these will become our baseline stories to compare with in the future, and we will assign this sprint by comparing the stories in the sprint with each other. This should provide a better view of progress over time as stories are completed, because pure time estimates have a tendency to be inaccurate or incomplete especially in the face of uncertainty.

| Points | Delivery Speed | Complexity Level | Effort Guide | Risk / Uncertainty |
| ---| ---| ---| ---| --- |
| 1 | Quickest delivery | Minimal complexity | Very small / trivial (a few hours) | Almost no risk |
| 2 | Quick delivery | Low complexity | Small (less than a day's work) | Low risk |
| 3 | Quick–moderate delivery | Straightforward complexity | Small–medium (1–2 days) | Low–moderate risk |
| 5 | Moderate delivery | Moderate complexity | Medium (a couple of days) | Moderate risk |
| 8 | Longer delivery | High complexity | Large (a week, multiple moving parts, needs collaboration) | High risk |
| 13 | Longest delivery | Highest complexity | Very large (multi-day across team) | High uncertainty / cross-team risk |
| 20+ | Too large for sprint | Too complex | Epic-level | Must be broken down before sprint |
