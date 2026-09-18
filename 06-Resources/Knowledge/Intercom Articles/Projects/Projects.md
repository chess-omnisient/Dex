> **Status:** Draft — not yet published

# Projects

A project is a workspace for data analysis and visualisation. Each project contains the datasets, reports, and selections needed to run a specific type of analysis. Projects are created from templates that define what type of analysis is performed and what data is required.

---

## Project types

Projects are created from templates. The available templates depend on your organisation's subscriptions and partner agreements.

| Project type | Description | Refreshable | Subscription | Approver |
|---|---|---|---|---|
| **Overlap** | Compare your customer dataset against a partner's shared dataset to identify shared and exclusive customers. | Yes | No | Partner dataset owner |
| **ACE** | Generate an ACE report using the Strive data universe and one of your own datasets. ACE (Anonymised Campaign Engine) evaluates partnership value and synergy using Omnisient's data — including credit bureau, deeds, CIPC & Home Affairs, and marketing data. | No | Yes | Strive |
| **Collaborative ACE** | Generate an ACE report using a shared dataset from a partner organisation, Strive data, and your own data. | No | Yes | Internal review |
| **Manual ACE** | Create an ACE report by manually entering project details and configuring the client, demographic, link, and partner tables. | No | Yes | Internal review |
| **Rainmaker Attribution** | Measure campaign effectiveness by comparing new sales data against a Lookalike or Rainmaker marketing audience. Identifies which new sales are attributable to the campaign by fusing your data with campaign trend and consumer shopping datasets. | No | Yes | Internal review |
| **Financial Inclusion** | Develop a bespoke credit score using retail features to assess credit risk for loan applicants — supporting credit access for thin-file consumers and improved offers for thick-file consumers. Runs in a cleanroom environment with real-time API access to features or the developed score. | No | Yes | Shoprite |
| **BasketScore Retro Analysis** | Test the predictiveness of the pre-built BasketScore against your consumer data to assess credit risk for loan applicants — supporting credit access for thin-file consumers and improved offers for thick-file consumers. Runs in a cleanroom environment with real-time API access to the BasketScore. | No | Yes | Shoprite |
| **Custom** | Create a personalised analysis by merging any of your own datasets. | No | Yes | Internal review |
| **Manual** | Create a project tailored for a specific use case, with an optional Power BI report link. | No | No | Internal review |

> Some project types are only available to organisations with specific partner agreements or active subscriptions. If a template is not visible in your project creation options, contact your account manager.

> **Refreshable projects** allow you to re-run the analysis against updated data without creating a new project. This capability is currently available for Overlap and is being expanded to additional project types.

---

## Creating a project

Projects are created from the **Projects** section of the platform, accessible via the side navigation.

**Two ways to start:**

1. **Side navigation shortcut** — Click the **+** icon next to Projects in the side navigation. This opens the project creation bottomsheet directly.
2. **Projects screen** — Click the Projects navigation link to open the full project table, then select **Create Project** in the top right corner. This opens the same bottomsheet.

From the bottomsheet, select the project type you want to create. Each project type opens a setup wizard to guide you through configuration.

**Step 1 — Project details and user access**

All project types begin with a project details step where you can:

- Add a project name and description
- Add users from your organisation and assign their roles

You are automatically set as the project **Owner**. All additional users default to **Read Only** — you can update this using the role dropdown next to each user's name.

> See [Roles and Permissions](#) for a full breakdown of what each role can do.

---

## Project roles

| Role | Can do |
|---|---|
| **Owner** | Full control — manage users, edit content, update permissions, delete project |
| **Read and Write** | View and edit the project, manage data and reports, perform selections |
| **Read Only** | View only — cannot edit the project, data, or reports |

All added users default to **Read Only**. Roles can be updated during project creation or afterwards if you are the Owner.

---

## Project status

| Status | What it means |
|---|---|
| **Awaiting Approval** | The project has been submitted and is pending approval from the partner dataset owner, subscription provider, or Omnisient. |
| **Processing** | The project has been approved and analysis is running. |
| **Active** | The project is ready to use. |
| **Failed** | Processing did not complete successfully. Contact your account manager. |
| **Rejected** | The project was not approved. A rejection reason is included in the notification. |
| **Locked** | The project's dataset share or subscription has expired and the project cannot be used until access is renewed. |

**Locked notifications**

You are notified before a project becomes locked:

- Dataset share expiry: 15 days, 3 days, and on the day of expiry
- Subscription expiry: 30 days, 15 days, and 1 day before expiry

---

## Approvals

Some project types require approval before processing begins. The approver depends on the project type — this may be the partner dataset owner, a subscription provider, or an internal review. In all cases, Omnisient can also action approvals.

Once submitted, your project status changes to **Awaiting Approval**. You will receive a notification when the project is approved or rejected.

> For full details on the approval process, see [Project Approvals](#).

---

## Notifications

You receive both an email and an in-app notification when your project status changes.

| Event | Email | In-app | Who receives it |
|---|---|---|---|
| Project submitted for approval | ✅ | ✅ | Project owner |
| Project approved and processing | ✅ | ✅ | Project owner |
| Project ready | ✅ | ✅ | Project owner |
| Project rejected | ✅ | ✅ | Project owner |
| Selection ready | ✅ | — | Selection creator |

---

## Related

- [Overlap Projects](#)
- [Roles and Permissions](#)
- [Project Approvals](#)
- [Datasets](#)
- [Selections](#)
