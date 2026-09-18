> **Status:** Draft — needs review before publishing

# Creating Connections

Creating connections on the Omnisient platform allows companies to securely share and collaborate on datasets with selected partners.

---

## Before you start

- **Permissions required:** Admin rights on your organisation's Omnisient account
- **Prerequisites:** The company you wish to connect with must be listed on the Omnisient platform

---

## Creating a connection

### Step 1: Access the Connections menu

Log in to the Omnisient platform, navigate to the **Data Collaboration** section in the side navigation, and select **Connections**.

### Step 2: Create a new connection

On the Connections screen, you will see existing connections and a free-form text box to create a new one. Enter the name of the company you wish to connect with. Make sure the name is spelled correctly to avoid delays.

### Step 3: Send connection request

Click **Send Request**. This notifies the Omnisient client support team, who will verify the company is listed on the platform and forward your request.

### Step 4: Partner receives the request

The partner company receives a notification of the connection request. They can either accept or reject based on their preference.

### Step 5: Admin approval on your side

If the partner accepts, your company's admin must also approve the connection. Navigate to **Connections** and look for the pending connection, then click **Accept** to finalise.

> Only users with admin rights can approve connection requests. Ensure the appropriate individuals in your organisation are handling these tasks.

### Step 6: Private collaboration space established

Once both companies have accepted, a private collaboration space is established where you can securely share specific datasets between your company and your partner.

---

## Subscription-based connections

When Omnisient sets up a subscription, a connection invitation must be accepted by both the **subscription owner** and the **subscription user** before it becomes active.

### What is a subscription?

A subscription grants access to a specific project type. Think of it as a "pass" for creating different project templates (like ACE or Financial Inclusion), defining which project types are available and for how long.

### How subscription connections work

**Step 1: Omnisient configures a subscription**

Omnisient sets up a subscription that links the subscription owner and the subscription user. Once configured, a **connection invitation** is sent to both parties.

**Step 2: Review the connection invitation**

Both parties receive a notification with the connection details.

- The **subscription user** can verify that the correct subscription owner was connected. This connection request needs to be actioned in the system.
- The **subscription owner** has visibility on who wants to use their subscription. This connection request needs to be actioned in the system.

**Step 3: Accept or decline the invitation**

Both the subscription owner and the subscription user must independently accept the invitation.

| Scenario | Outcome |
|----------|---------|
| **Both parties accept** | The subscription is enabled and the project type becomes available to the subscription user. |
| **Either party declines** | The subscription will not be enabled. No data is shared. |

**Step 4: Create a project**

Once the connection is active, the subscription user can create projects using the subscribed project type. When a project is created, an **approval request** is sent to the subscription owner. This project approval request must be actioned in the system before processing begins.

> For full details on the approval process, see [Approving Projects](https://help.omnisient.com/en/articles/approving-projects).

---

## Project types requiring Data Owner approval

Data Owners (subscription owners) can approve or decline the following project types:

| Project type | Description |
|---|---|
| **Overlap** | Compare customer datasets to identify shared and exclusive customers. |
| **ACE** | Anonymised Campaign Engine — evaluates partnership value using Omnisient's data universe. |
| **Financial Inclusion** | Bespoke credit scoring using retail features for thin-file and thick-file consumers. |
| **BasketScore Retro Analysis** | Test pre-built BasketScore predictiveness against consumer data for credit risk assessment. |
| **Predictive Modeling** | Predictive modeling capabilities. Available in the USA only. |

---

## What to expect

After both parties accept and a project is created:

1. The subscription owner receives an approval request notification.
2. The subscription owner reviews and approves or rejects the project.
3. If approved, the project moves to **Processing** and then **Active** status.
4. If rejected, the subscription user receives a notification with the rejection reason.

---

## Best practices

- **Clear communication:** Ensure both parties are aware of the connection request and the purpose of the collaboration before initiating.
- **Verify permissions:** Only admins can accept or reject connection requests. Make sure the appropriate individuals in your organisation are handling these tasks.
- **Select datasets wisely:** Choose datasets that are relevant and necessary for the collaboration to maintain data security and privacy.

---

## Common issues

| Issue | Likely cause | Fix |
|-------|--------------|-----|
| Connection request not received | Company name entered incorrectly, or the company is not listed on the platform | Verify the spelling and confirm they are on Omnisient |
| Unable to approve connection | You do not have admin permissions | Ensure the correct permissions are set for the approving user |
| No subscription invitation received | Subscription has not been configured yet | Contact your account manager to confirm the subscription setup |
| Project type not available after connection | Subscription may not cover that project type | Verify which project types are included in your subscription with your account manager |
| Approval request not received by subscription owner | Connection may not be fully accepted by both parties | Confirm both parties have accepted the connection invitation |

---

## Related

- [Projects](https://help.omnisient.com/en/articles/projects)
- [Approving Projects](https://help.omnisient.com/en/articles/approving-projects)
- [Datasets](https://help.omnisient.com/en/articles/datasets)
- [User Permissions](https://help.omnisient.com/en/articles/user-permissions)

---

**Before publishing:**
- [ ] Confirm: does the subscription user also go through Admin > Approvals to accept the connection, or is there a separate UI?
- [ ] Confirm: exact notification channels for connection invitations (email only, in-app only, or both?)
- [ ] Confirm: can a declined connection invitation be re-sent, or must Omnisient configure a new subscription?
- [ ] Confirm: is Predictive Modeling limited to USA only at the subscription level, or only at the project creation level?
- [ ] Confirm: are there additional project types beyond the five listed that Data Owners can approve?
