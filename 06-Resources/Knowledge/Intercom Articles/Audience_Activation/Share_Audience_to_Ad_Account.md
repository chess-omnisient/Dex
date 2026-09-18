> **Status:** Draft — pending review

# How to share an audience to an ad account

This guide covers the two ways to share an audience with a connected ad account on Meta or TikTok — from a project selection or from a marketplace segment.

---

## Before you start

- **To connect an ad account:** You must have an **Admin** role. Ad accounts are connected per user and are only accessible to the user who authenticated them.
- **To create and share a selection:** You must have an **Owner** or **Read and Write** role on the project. Admins have Read and Write access by default.
- **Dataset prepared for activation:** The dataset used in your audience must have been marked as Activation Ready during Desktop Connect or Server Connect processing. If this step was skipped, the dataset will need to be re-uploaded and reprocessed. See [Preparing a dataset for campaign activation](#).

---

## Step 1: Connect your ad account

If your ad account is already connected, skip to Step 2.

1. Navigate to **Ad Accounts** under the **Admin** section.
2. Select the activation platform you'd like to connect — **Meta** or **TikTok**.
3. Follow the on-screen instructions. You'll be redirected to authenticate the account on the selected platform.
4. Once connected, link the **Ad Account** associated with that platform.

> **TikTok:** Accept all requested permissions during authentication. If permissions are changed or declined at any point after setup, the share will fail and will require reauthentication to resolve.

---

## Step 2: Share your audience

Choose the path that matches how your audience was created.

---

### From a project selection

**Create your selection**

1. Go to **Projects** and open the project where you want to build your audience.
2. Confirm your project type supports audience selections. Compatible types include:
   - Overlap
   - ACE
   - Collaborative ACE
   - Rainmaker
3. Open the **Selections** widget and select **Make Selection**.
4. Set your **Customer Base** and configure your filter criteria using the selection builder.
5. For **Intended Use**, select **Activate via Supported Channels**.

> **Important:** Selecting Export or Save Criteria as the intended use will produce an audience that cannot be pushed to an ad platform.

6. Assign a friendly name and complete the selection setup.
7. Your selection will go through an internal review. Once approved, it will appear under the **Selections** tab in your project.

**Share to your ad account**

1. Open the approved selection to access its detail view.
2. Scroll to the **Activation Channels** section.
3. Click **Share to Ad Account**. A panel will appear.
4. Select **Add Ad Account**.
5. In the setup modal:
   - Select the **Ad Account** you'd like to share to.
   - Assign a **Friendly Name** to help identify this activation across multiple campaigns or projects.
   - Select your **Matching Fields** — the data points Meta or TikTok will use to match your audience:
     - Email
     - Phone Number
   - Including both fields maximises your match rate. Meta and TikTok use OR logic, so a record only needs to match on one field to be included.
6. Submit the request.

You can add multiple ad account destinations from this view.

---

### From a marketplace segment

Marketplace segments are predefined audiences available within the platform for activation.

1. Navigate to **Marketplace**.
2. Select the **Market Segment** you want to activate.
3. Open the sharing modal and complete the ad account details:
   - Select your connected Ad Account.
   - Assign a **Friendly Name**. This is appended to the end of the audience name for reference.
   - If you're activating on behalf of a client or another organization, check **Activate on behalf of someone else** and enter the client's name. This name is included in the audience name so the activation can be easily identified.
   - Matching fields are pre-configured for each segment — no selection needed.
4. Submit the request.

Once submitted, the segment will surface in **Audience Manager**.

> **Note:** Marketplace segments support a single ad account destination per share. Project selections allow multiple destinations to be added in one flow.

---

## What to expect

After submitting, your audience goes through an internal review before being handed off for delivery. You can track progress in the **Activation Channels** section of your selection (project path) or in **Audience Manager** (marketplace path).

| Status | What it means |
|--------|--------------|
| **Requested** | Submitted and under internal review. |
| **Rejected** | Did not pass the review. You can revise and resubmit, or contact support. |
| **Working** | Approved and actively being synced to your ad platform. |
| **Completed** | Successfully synced. The audience is ready to use in your campaigns. |
| **Failed** | The sync was not successful. You'll receive an email with the reason and recommended next steps. |

For a full breakdown of each status and how to respond to failures, see [Understanding the audience activation lifecycle](#).

---

## Related

- [Preparing a dataset for campaign activation](#)
- [Understanding the audience activation lifecycle](#)
- [Projects](#)
