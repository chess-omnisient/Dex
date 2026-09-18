---
title: Brazil Febraban Conference Set-up – Standard Operating Procedure
type: sop
source_task: https://app.clickup.com/9012824942/docs/8ck9jve-181672/8ck9jve-143992
created: 2026-08-21
---

# Brazil Febraban Conference Set-up – Standard Operating Procedure

## 1. Introduction

This SOP covers setting up and running the Omnisient platform demo used at conferences like Febraban – showing an executive or prospect the full flow from raw data upload through to a live marketing audience and a Jupyter-based lift report. It's a recurring process: the same demo environment and script get reused across conferences, not just Febraban.

The demo runs on two connected demo companies:
- **Casas Iraci** – the data owner (retailer)
- **Banco Boitata** – the data partner (bank), who receives and activates the shared audience

Both are accessed with **bobby** login details on the Omnisient demo platform.

---

## 2. Step-by-Step Guide: Setting Up the Demo Environment (This has already been configured)

### Step 1 – Get Desktop Connect
If you don't already have the Demo version of Desktop Connect:
- Log in to the Demo version of the Platform at [https://demo-v2.omnisient.com/](https://demo-v2.omnisient.com/)
- Click the grid icon in the top right
- Download Desktop Connect from there

![Desktop Connect demo download](https://t9012824942.p.clickup-attachments.com/t9012824942/5a15f2bd-f641-4bc2-83ff-61bc26bebb29/desktop%20connect%20demo.png)

[Video: Upload single hash](https://t9012824942.p.clickup-attachments.com/t9012824942/2ea50fcf-b6cc-4fee-8a43-9ea88bafcaae/Upload%20single%20hash.mp4?view=open)

### Step 2 – Upload the dataset via Desktop Connect
1. Log in with **bobby** details, into company **Casas Iraci**
2. Upload to a **new dataset**
3. Turn the **"Use for campaign activation"** toggle on

### Step 3 – Register and share the dataset in the Omnisient App
1. Log in with **bobby** details, into company **Casas Iraci**
2. Register a dataset
3. Share the dataset with your partner:
   1. Select partner – **BancoBoitata**
   2. Set access duration and usage terms
   3. Allow all data in overlap
   4. Select all Analysis fields
   5. Turn on **Allow Partner Selections** – this is required for the partner to create a selection later (used for audiences). Select all.
   6. Check **"I accept responsibility"** and click **Share Dataset**

[Video: Register and share a dataset](https://t9012824942.p.clickup-attachments.com/t9012824942/084bb99d-d37f-4bdb-9e29-2f1b8e60fa6d/Register%20and%20share%20a%20dataset.mp4?view=open)

---

## 3. Standard Operating Procedure

**Running the demo:**

### Project creation
1. Log into company **Banco Boitata**
2. Create an Overlap report using your **BancoBoitataBaseDePropostasV2** dataset and your partner's **CasasIraciBaseDeFidelizacao** dataset

### Creating a selection for audience creation
1. Open the **Casas_Iraci_Banco_Boitata_Audience_Selections** Overlap project
2. Scroll to **Selections**
3. Click **Make Selection**
4. Choose **own customer base** and make sure **Activate via Supported Channels** (Meta & TikTok) is selected under **Intended use**
5. Click **Add Rule**

![Add rule screenshot](https://t9012824942.p.clickup-attachments.com/t9012824942/ef3939cb-d9a8-428e-bd23-3f1ae6a9c504/Screenshot%202026-08-20%20at%2014.44.41.png)

6. Add filters per the image

1. Click **Apply Filters**
2. Scroll down and click **Next**
3. Give the selection a friendly name and click **Create**
4. Open a completed selection by clicking **View**
5. Click **Share to Ad Account**

![Share to ad account screenshot](https://t9012824942.p.clickup-attachments.com/t9012824942/0bcff010-fd08-4789-974f-23828d3ca11f/Screenshot%202026-08-20%20at%2014.47.16.png)

6. Click **Submit**

[Video: Making a selection for ad accounts](https://t9012824942.p.clickup-attachments.com/t9012824942/5eafa071-c6ad-428f-9011-489e9a6e6041/making%20a%20selection%20for%20ad%20accounts.mp4?view=open)

### Sharing to Marketplace and Audience Manager
1. Click **Marketplace**
2. Select **Mobile Contract Renewal Window**
3. Select the **Meta Account**
4. Give the audience a friendly name so Back Office know what they're approving
5. Select an **Audience End Date**
6. Click **Create**

![Marketplace creation screenshot](https://t9012824942.p.clickup-attachments.com/t9012824942/6c626758-3c42-4ebe-9a9f-2f7747b78445/Screenshot%202026-08-21%20at%2011.04.23.png)

7. This goes to Back Office for approval
8. Click **Audience Manager**
9. View the details of the audience, such as segment size

![Audience Manager screenshot](https://t9012824942.p.clickup-attachments.com/t9012824942/55ee9a34-6333-4b08-8fce-eceba28c858e/Screenshot%202026-08-21%20at%2011.07.33.png)

[Video: Marketplace walkthrough](https://t9012824942.p.clickup-attachments.com/t9012824942/ed1f727d-f8e5-4fd8-b357-1dc1d930ded6/bruna%20marketplace.mp4?view=open)

### Accessing the Jupyter Report
1. Go to the Projects Dashboard and select the custom project **Casas_Iraci_Banco_Boitata_RetailLiftCreditScore**
2. Open with **Jupyter Notebook**
3. Select **Standard workspace** and click **Confirm**
4. See [[Bank Overlap Report Walkthrough]] for step 4 onward (trusting the file, reviewing report contents, and presenting to a client)

**Escalation:**
- If the demo environment breaks during setup (login, dataset upload, sharing), flag Support.

**What NOT to worry about:**
- Back Office approvals – this is handled by Back Office, not something the person running the demo needs to chase.

---

## 4. Open Items / To Confirm

- **Jupyter Report, step 4 onward:** resolved – see [[Bank Overlap Report Walkthrough]]. Note that SOP's video uses "Large workspace" rather than "Standard workspace" – worth confirming which is correct.
