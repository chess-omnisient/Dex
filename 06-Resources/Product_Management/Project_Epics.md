# Project Epics



# BackEnd Revamp - Foundation Support Processes and 1st Spark Step (BERFSP1)

# Link to relevant Epic
Private ([https://app.clickup.com/t/8699cq04z](https://app.clickup.com/t/8699cq04z))

# As-Is
The following documents show the existing objects (stored procs, pipelines, etc) in Synapse:

[Core Data - All Synapse Objects.xlsx](https://t9012824942.p.clickup-attachments.com/t9012824942/6f438bd9-ca47-489f-a15f-4ec28b5a06e5/Core%20Data%20-%20All%20Synapse%20Objects.xlsx)

[Core Data - High level processes (BE Revamp).xlsx](https://t9012824942.p.clickup-attachments.com/t9012824942/4f3715f5-931f-47c6-ac3a-1387eb7c7c43/Core%20Data%20-%20High%20level%20processes%20(BE%20Revamp).xlsx)

[Core Data - High level processes.docx](https://t9012824942.p.clickup-attachments.com/t9012824942/7e1a2805-c990-4a8f-a50b-153f2563218d/Core%20Data%20-%20High%20level%20processes.docx)

This excel shows the steps for each of the different data types in the order they would be executed.

[OmniConnect DataType Steps.xlsx](https://t9012824942.p.clickup-attachments.com/t9012824942/93e24ca7-2bdc-4960-9a7c-e09d4d808b13/OmniConnect%20DataType%20Steps.xlsx)

# Build GraphDB Matching MVP

# Architecture Review Board Submission

### **Project Details**

| Field | Description |
| ---| --- |
| **Project Name** | Graph-Based Entity Resolution (Graph Matching MVP) |
| **Project Description** | Introduce a graph-driven matching framework to enrich Omnisient’s matching capabilities across multi-party datasets. The solution uses Spark-based graph algorithms (Adamic-Adar and Label Propagation) to infer entity relationships and assign a consistent cross-table `omni_id` for use in project joins. |
| **ClickUp Link** |  |
| **Presenter(s)** | Donovan Wilson – Head of Data Science |
| **Date** |  |
| **Review Type** | New Technology Introduction + Architecture Pattern Review |

* * *
### **Desired ARB Outcome**
We request input and guidance on the following:
1. **Technology Stack Alignment** – Confirm that the use of Fabric Spark and GraphFrames for large-scale graph computation aligns with platform principles and standards.
2. **Scalability Strategy** – Validate our approach to scaling Spark jobs (horizontal vs vertical scaling, partitioning by subgraphs).
3. **Software & Package Approval** – Approve the use of `GraphFrames`.
4. **Security & Compliance** – Confirm that the proposed Spark-based graph resolution process meets platform data security principles (no unencrypted data persistence, controlled identity access).
5. **Monitoring & Observability** – Advise on best practices for Spark job telemetry, performance metrics, and failure notifications integrated into our monitoring ecosystem.
6. **Matching Interpretability & Auditability** – Agree on standards for per-link explainability so we can inspect how matches were formed (e.g., Adamic–Adar scores, contributing hashed-PII categories/attributes, neighbor degrees, thresholds/tie-break rules), and define the persistence/visualization approach (audit tables, lineage, review dashboards).

* * *
### **As-Is Architecture**

| Layer | Current Approach |
| ---| --- |
| **Data Source** | Synapse Dedicated SQL Pools host anonymized and hashed datasets for each project. |
| **Processing Engine** | All joins and matching currently done through SQL-based rulesets and hashed equality logic (non-graph). |
| **Output** | Matched tables on a one-to-one level with project-level join keys. |
| **Orchestration** | Synapse Pipelines manage batch processing and job execution. |

* * *
### **To-Be Architecture**
#### **High-Level Flow**
1. **Input Preparation**
    *   Synapse exports relevant project datasets to **Parquet** in the Data Lake (staging area).
2. **Graph Construction (Spark in Fabric)**
    *   Spark job reads Parquet data.
    *   Builds **bipartite or multi-partite graphs** using hashed PII keys (e.g., phone, email, name).
3. **Entity Resolution Algorithms**
    *   **Option A:** Adamic-Adar only
        *   Compute similarity scores across edges.
        *   Apply configurable threshold to determine entity groupings.
    *   **Option B:** Adamic-Adar + Label Propagation
        *   Same as Option A, followed by label propagation to consolidate entities across connected components.
4. **Result Publishing**
    *   Resolved entity assignments are written back to the Data Lake.
    *   Synapse pipeline picks up results and appends a new **graph-derived** **`omni_id`** column to each table.
5. **Downstream Use**
    *   Updated tables are reused in standard project workflows, enabling record-level joins across multiple datasets.
* * *
### **Proposed Technology Stack**

| **Category** | **Technology** | **Purpose** |
| ---| ---| --- |
| **Existing** | Azure Synapse Analytics | Source storage, orchestration, and pipelines |
|  | Azure Data Lake (ADLS Gen2) | Parquet staging area |
| **New / Proposed** | **Fabric Spark** | Graph computation engine for scalable, distributed processing |
|  | **GraphFrames** | Spark library for graph algorithms (Adamic-Adar, Connected Components, Label Propagation) |
| **Orchestration** | Synapse Pipeline → Fabric Spark Job API | Job submission and retrieval of results |
| **Security / Identity** | Managed Identity + RBAC | Secure data access from Synapse to Fabric |
| **Monitoring** | Azure Monitor / Fabric Job Telemetry | Job success/failure notifications, metrics, and logs |

* * *
### **Security Considerations**
*   Data remains **hashed/anonymized** end-to-end.
*   No intermediate unencrypted storage; all processing occurs in memory within Fabric Spark.
*   Managed Identities control Fabric workspace access (Synapse ↔ Fabric).
*   Execution metadata and results are logged in existing **audit tables** for traceability.
*   Job definitions and thresholds are version-controlled in Git for reproducibility.
* * *
### **Performance & Scalability Considerations**

| Concern | Description | Questions for ARB |
| ---| ---| --- |
| **Job Duration** | Current project pipelines can exceed 1 hour; we must ensure this module doesn’t add disproportionate latency. | How should we balance horizontal vs vertical scaling in Fabric Spark for graph workloads? |
| **Parallelism** | Graph jobs could be **partitioned into sub-graphs** by key attributes (e.g., gender, age, hashed PII category) and run in parallel Spark sessions. | Is this an acceptable parallelization pattern within Fabric’s cost and scheduling model? |
| **Cluster Sizing** | Need to evaluate Spark pool auto-scaling vs dedicated cluster setup. | Are there existing Fabric cluster guidelines for intensive graph workloads? |
| **Monitoring** | Require alerting on job failure or degraded performance. | Can we integrate Fabric job telemetry with Azure Monitor or an existing Ops dashboard? |

* * *
### **Impact Summary**

| Area | Impact |
| ---| --- |
| **Systems** | Introduces Fabric Spark as a new processing engine linked to Synapse. |
| **Teams** | Data Science & Platform Engineering collaboration for setup and maintenance. |
| **Security** | No additional risk beyond existing managed identity policies. |
| **Cost** | Additional Fabric compute consumption during graph resolution runs. |
| **Scalability** | Improved scalability for entity resolution across large multi-table datasets. |

* * *
### **To-Be Diagram**

* * *
### **Review Questions for ARB**
1. Does this proposed architecture align with our current **data-processing principles** and **technology standards**?
2. Is **Fabric Spark** an appropriate and approved engine for this type of workload?
3. Are there recommended **cluster configurations** for large-scale graph computation?
4. What are best practices for **monitoring and alerting** of Fabric Spark job health within our environment?
5. What are the best mechanisms for storing, surfacing and archiving audit reports for matching interpretability and explainability.
* * *

[undefined](undefined)

# Convert Online APIs to a More Stable BackEnd

# Architecture Review Board Submission

# Desired ARB Outcome

### **1\. Executive Summary**
This proposal outlines a backend change for the data processing API from traditional relational storage or data warehouse access to a **Parquet-based architecture using DuckDB**.
The goal is to improve query performance, reduce cloud costs, and simplify data access by leveraging **columnar Parquet files stored in Azure Blob Storage** as the primary data source.
DuckDB acts as an **embedded analytical engine**, enabling SQL queries to execute directly on Parquet files without the need to first load data into a database system.

### **2\. Business Justification**
The change is driven by the following key business and technical factors:

| **Challenge** | **Proposed Solution** | **Expected Benefit** |
| ---| ---| --- |
| Growing data volumes resulting in higher query latency and cost in relational DBs | Query directly on Parquet files using DuckDB | Sub-second access for analytic queries on compressed, columnar data |
| Increased cloud storage and compute cost | Store data once in Azure Data Lake Storage (ADLS) | Lower cost and operational overhead (no redundant DB storage) |
| Need for flexibility and rapid analytics | Ad-hoc SQL on Parquet with DuckDB’s in-memory execution | Faster iteration |

### **3\. Technical Design**
#### **3.1 Architecture Overview**
*   **Data Storage:**
    *   All data resides in **Azure Blob Storage**, organized in logical folders (e.g., `/segments/client_data/`).
    *   Files are stored in **Apache Parquet** format for optimized analytical reads.
*   **Query Engine:**
    *   **DuckDB** (embedded OLAP engine) executes SQL queries directly on the Parquet files.
*   **API Layer:**
    *   Azure function
    *   Python environment
    *   **FastAPI** provides a lightweight REST interface.
    *   Each request dynamically reads the target Parquet file, executes the SQL, and returns a JSON response.
*   **Security & Access:**
    *   Azure Blob access is authenticated via **SAS tokens.**
    *   API Keys, HMAC, IP whitelisting
*   **Indexing**
    *   lightweight metadata index table
    *   ![](https://t9012824942.p.clickup-attachments.com/t9012824942/59346356-27d0-466d-aade-1c879c523353/image.png)

**Security Considerations**
Will have to do a pen test as this is a new implementation but will use current implementation stack as guideline for security implementations.

**Latency Testing**

No optimisation
![](https://t9012824942.p.clickup-attachments.com/t9012824942/7858b4a6-adcd-4838-8381-5e26a221fb3b/image.png)

**Optimised testing**

# To-Be Diagram

# Create Spark Pool Orchestrator

# Architecture Review Board Submission

# Project Details

| **Project Name** | Create Spark Pool Orchestrator |
| ---| --- |
| **Project Description** | Develop a centralized application for managing and monitoring Spark job executions. The system will support job submissions via a scheduler and API requests, provide real-time monitoring of job statuses, and send automated notifications upon completion or failure. |
| **ClickUp Link** | OMNI-1445 |

# Desired ARB Outcome
### **Tech Stack**
The solution will leverage **Azure Functions** for serverless execution, **Azure Key Vault** for secure secret management, and **SQL Server** for storing job metadata and status information. The selected components align with organizational principles and standards for cloud-based, scalable solutions.
### **Software Stack**
The application will be developed in **C#** and made available exclusively to internal systems. All external integrations will adhere to internal software usage and approval policies.
### **Security**
Sensitive credentials and connection strings will be managed through **Azure Key Vault**, ensuring secure access and compliance with internal security requirements. Network and access controls will restrict the application to internal environments only.
### **Monitoring**
Uptime monitoring and automated notifications will be implemented to track the performance and health of submitted Spark jobs. The system will alert relevant teams of job failures or other critical events to ensure timely response and resolution.

# Process Flow

![](https://t9012824942.p.clickup-attachments.com/t9012824942/3b683232-e018-4a33-ad15-806ed448a6f3/SparkProcessController.drawio.png)

# Electron WebApp Conversion

# Architecture Review Board Submission

# Project Details

| **Project Name** | Electron WebApp Conversion |
| ---| --- |
| **Project Description** | To help implement our security measures of the client not allowed to download data from our platform. We're moving our embedded tools like SQLPad and Jupyter Notebook to be served in a Electron wrapper with enhanced security capabilities. |
| **ClickUp Link** | Private ([https://app.clickup.com/t/869afvn8t](https://app.clickup.com/t/869afvn8t)) |

# Desired ARB Outcome
**Get input from Architects and fellow tech members about the following:**
**Tech Stack**:
*   Azure Static App / App Services
*   Cloudflare
*   Blob Storage (For desktop app deployment)
**Software Stack:**
*   Electron.js
*   Angular
**Security:**
*   Application will be code signed
*   CSP implemented on Web App
*   We need to block the web app from being loaded by a browser. It could possible be done from Cloudflare security rules or mTLS (will require App Services)
# To-Be Diagram
![](https://t9012824942.p.clickup-attachments.com/t9012824942/79328d86-a4e8-4483-aa0e-538b272f8fd2/Electron%20App%20Conversion.png)

# Enable Refresh Capability for Projects

## Epic Description
Private ([https://app.clickup.com/t/869ajdvny](https://app.clickup.com/t/869ajdvny))
As a user of the Projects workspace, I want the ability to refresh my project data without losing project integrity (custom tables, queries, access tokens, notebooks), so that I can update my project with the latest data while continuing my work seamlessly.
### Decision Log

| Date | Decision | Decision made by |
| ---| ---| --- |
| 13/01/2026 | Out of scope decision: Multiple users working in a project: If someone wants to start a refresh and there is someone else is in the project alert the user in the confirmation modal that someone else is using the project and therefore they cannot refresh.<br><br>[](https://app.clickup.com/t/869brh0rt) | Platform Squad Story Playback (13/01/2026) |
| 13/01/2026 | The new temp project will show in the UI because it'll be in a processing state.<br><br>Add a new status? | [@Rudolph K](#user_mention#87829005) [@Robin Cleland](#user_mention#93609644) |
| 12/02/2026 | <br><br>Admins can refresh project due to their implied read-write permissions. | [@Rudolph K](#user_mention#87829005) [@Werner Hurter](#user_mention#93628072) [@Olivia de Kok](#user_mention#87874670) |

### High-level flow

![](https://t9012824942.p.clickup-attachments.com/t9012824942/cb708db7-9cac-428a-9b6c-1f2ac1c61ea2/image.png)

# Architecture



# Design

### Option 1: Robin's suggestion

The above flow describes a way in which we could potentially refresh any project without having to modify the individual project pipelines.
*   Start Refresh: kick off refresh project pipeline and provide it with the original project\_ID.
*   The project will fetch the required metadata from the front-end database.
*   The refresh process will execute the required project type (using the original metadata/parameters) as a new project. I am not 100% sure on how we achieve this in an ADF pipeline. Will require assistance from ENG possibly
*   Once the new refresh project has completed successfully, all data created in it will be pushed to the original project replacing what is there. I suggest renaming the original object, the transferring the refreshed object, and only on success of the entire process, remove the renamed backups
*   This will not overwrite any custom objects added to the original project by the user. It will overwrite any modifications made by the client to project generated tables, ie. added columns
*   On success, the refresh project will be removed both physically and from metadata.
*   If the refresh project fails for any reason, the refresh project can be dropped, and a retry can be attempted.

The main advantage to the above approach is that the original project schema remains and any linked objects (from SQLPad or Jupyter should be unaffected)
In case of a refresh failure, the original project remains unaffected. Even in the case of an object failing while being refreshed, there will be backups to recover from.

Will require assistance from ENG on projects which do not require parameters, but pull that data from DB. We will need some way in which to create a copy of the metadata in order to kick off the refresh project. Example of this is Custom Project.
#### Questions
1. The new temp project will show in the UI because it'll be in a processing state.
    1. Add a new status?

### Option 2: Rudi's Suggestion
We add a new parameter to the existing pipeline which is @refresh and instead of reusing the same project code as the project already exists, we generate a new project code.

From what I can see the rest of the code should flow normally as it will use the new project code to generate the schema and then at the end of the custom pipeline, you just copy all the assets from the new project code back to the original project code. Everything else should work as before.

# Infrastructure



# Testing



# Enable single sign-on authentication (SSO)

## Epic Description
Private ([https://app.clickup.com/t/8699pzmet](https://app.clickup.com/t/8699pzmet))
Companies using the platform allow both SSO and password-based authentication. To enhance security and streamline authentication, we want to introduce an SSO enforcement option at a company level.
### Decision Log

| **Date** | **Decision** | **Decision made by** |
| ---| ---| --- |
| 23/09/2025 | Handing guest authentication and access should be managed by the organization owner's security policy (i.e, add a guest to their identity provider). | [@Leigh Williams](#user_mention#87829008) [@Rudolph K](#user_mention#87829005) [@Olivia de Kok](#user_mention#87874670) |
|  | Omnisient super users can switch organizations without authentication via the organization's authentication configuration for now. |  |
|  | Users will not be created when logging into the system for the first time using SSO. |  |
|  | No automatic logout for users that are removed from the organization's identity provider. |  |
| 10/10/2025 | Switching organization will work as is, the user will authenticate using their default companies authentication configuration. From there, they can switch organizations freely. | [@Olivia de Kok](#user_mention#87874670) [@Rudolph K](#user_mention#87829005) |
| 03/11/2025 | Organization "Security" page will be hidden a User role. Only an Admin will see this navigation item and be able to navigate to it. A role check will be done on the URL. | [@Olivia de Kok](#user_mention#87874670) [@Diego Jeptha](#user_mention#93615988) |
|  | Default to Locally Managed Authentication with both Local sign in and Microsoft options toggled on. |  |
| 10/11/2025 | We will authentication according to the organization's authentication settings first and then do any additional checks after the authentication is successful i.e, a locked or deactivated check, if either of these are true, we will show the user the appropriate screen or toast notification. | [@Olivia de Kok](#user_mention#87874670) [@Diego Jeptha](#user_mention#93615988) [@MOTLALEPULE M TSHAKELA](#user_mention#212675662) |
| 11/11/2025 | The password reset option remains enabled in the "Back Office Edit User" modal, as users may belong to multiple organizations that use different authentication methods. | [@Rudolph K](#user_mention#87829005) [@Diego Jeptha](#user_mention#93615988) |
| 20/11/2025 | This user story does not support email aliasing for authentication. Authentication is validated against the **base email** returned by the Identity Provider (IdP). In some IdPs for example, Google Workspace signing in using an alias such as [`user+alias@gmail.com`](mailto:user+alias@gmail.com) will still resolve to the primary account [`user@gmail.com`](mailto:user@gmail.com). If the primary email does not exist as a user in Omnisient, authentication will fail. | [@Rudolph K](#user_mention#87829005) [@Olivia de Kok](#user_mention#87874670) [@Diego Jeptha](#user_mention#93615988) [@Pardon](#user_mention#200468952) |

### High-level flow

# Architecture



# Design



# Infrastructure



# Testing



# FMCG Customer Intelligence Hub

## Epic Description
FMCG Customer Intelligence Hub is a 3-way project/cleanroom between a FMCG client, Shoprite and Strive. It outputs tables for analysis in SQLPad and Jupyter as well as a Power-BI overlap report (to be automated in Sprint 6). The Strive and Shoprite datasets are embedded in the subscription using a "shadow" share, which shares the datasets, but marks them as invisible everywhere on the app, other than this project.

## Decision Log

| Date | Decision | Decision made by |
| ---| ---| --- |
| 17 November 2025 | 3-way overlap held over to sprint 6 due to capacity issues | Ronny |
| 17 November 2025 | Remove view relations button for now. To be added in future enhancement ticket | Chess |
| 27 Nov 2025 | Enhancement ticked added to the backlog to enable the view relations button and corresponding graphic | Chess |
| 24 November 2025 | The "shadow" datasets will be implemented automatically with the subscription (Shoprite and Strive) | Ronny |
| 12 Jan 2025 | It is very possible we might come across an FMCG that might have IDs. New ticket has been created to address this issue | Paul |
| 13 January 2025 | Definition:<br>Shoprite clients → customers<br>FMCG clients → clients (FMCG Client → refers to Coca Cola/Pepsi etc) | Motlalepule |
| 15 Jan 2026 | We need to allow for DW\_ID\_Keys, a user story has been added to the backlog | Paul |
| 16 Jan 2026 | Consolidated link table to be used as the link table | Neels |
| 16 Jan 2026 | The configuration table is linked to a company subscription, which is already linked to a company. So each subscription should have exactly one configuration record. | Motlalepule |
| 20 Jan 2026 | Motla will go ahead with building the automated report using the existing 3 party Venn report, which we can change at a later stage | Paul |
| 29 Jan 2026 | For the additional views, should Shoprite also be flagged in the link table? Meaning we would have 4 parties (client, partner, strive, Shoprite)?<br><br>Ronny Tack<br>No. Shoprite is the Partner in the FMCG project type | Ronny |

## Documentation

### Linking Table
![](https://t9012824942.p.clickup-attachments.com/t9012824942/dd05f620-7d80-4d1b-ac81-f8563ecd2824/image.png)
## High Level Flow
![](https://t9012824942.p.clickup-attachments.com/t9012824942/06aa2741-13cf-4472-bf83-1ccb13539549/image.png)
### Notes/Definitions regarding ticket Private ([https://app.clickup.com/t/9012824942/OMNI-4230](https://app.clickup.com/t/9012824942/OMNI-4230)) :
**Indirect Customer Base:** These are customers who have purchased the FMCG’s products via the retailer, but are not part of the FMCG’s first-party data.

Setting up mock data/dummy data should be done during development.

# Architecture

## Pipeline Design
[@Neels Oosthuizen](#user_mention#93615981) please supply me with a diagram of your pipeline and the requirements

# FMCG 01 | FMCG Customer Intelligence Hub | Static DCR MVP



# Testing

[@Pardon](#user_mention#200468952) please publish your testing on this document (you can refer to the SQLPad doc here Private ([https://app.clickup.com/9012824942/docs/8ck9jve-78532/8ck9jve-28892](https://app.clickup.com/9012824942/docs/8ck9jve-78532/8ck9jve-28892)))
[@Pardon](#user_mention#200468952) just a reminder to please publish your testing on this document.
/Testing Activities

FMCG 01b-US01 | Enable Subscription Based Dataset Share Capability for FMCG Project Template Type

[https://app.clickup.com/t/869b925yc](https://app.clickup.com/t/869b925yc)

FMCG 01-US02b | Enhance Project for Static 3-way Overlap between FMCG, Shoprite & Strive

[https://app.clickup.com/t/869b1pt06](https://app.clickup.com/t/869b1pt06)

# Testing Outcomes and Vulnerabilities

[@Pardon](#user_mention#200468952) , please publish your testing outcomes on this document (you can refer to this document as an example Private ([https://app.clickup.com/9012824942/docs/8ck9jve-78532/8ck9jve-28932](https://app.clickup.com/9012824942/docs/8ck9jve-78532/8ck9jve-28932)))

# Manage Audience Expiration

## Epic Description
Within the platform, users can create selections they wish to target for marketing campaigns across activation channels such as **Meta** and **TikTok**. When a selection is created, the system facilitates first uploading the audience to the **Omnisient’s Business account**, which then shares access with the **user’s ad account** to enable campaign creation.

To maintain control and ensure security, datasets remain stored under the Omnisient business accounts. Certain system events can necessitate **revoking an audience share.**

This epic aims to **address existing gaps** and **ensure automatic and consistent unsharing of audiences** whenever predefined security or lifecycle conditions occur, thereby strengthening data governance and minimizing exposure risks.

The goal of this epic is to:
**🏆 Prioritize prevention**
*   Prevent locked projects & locked dataset shares
    *   Resulting in unnecessary audience expiry
*   Alert users in a timely manner so that they can deal with campaigns appropriately

### Decision Log

| Date | Decision | Decision made by |
| ---| ---| --- |
|  |  |  |

### Planning

[

www.figma.com

https://www.figma.com/board/NHwA9lfptMTXVU4CWzzpvQ/Meta-%7C-Activations---Integrations?node-id=735-629&t=mxAC2NENa7hislY4-1

](https://www.figma.com/board/NHwA9lfptMTXVU4CWzzpvQ/Meta-%7C-Activations---Integrations?node-id=735-629&t=mxAC2NENa7hislY4-1)

# Parquet Query System

# Architecture Review Board Submission

# Project Details

| **Project Name** | API To query parquet |
| ---| --- |
| **Project Description** | Query Parquet files from adls gen 2 storage for sub second response times |
| **ClickUp Link** | OMNI-1445 |

# Desired ARB Outcome

## Executive Summary
The proposed solution is a centralized Python web application designed for submitting, scheduling, and monitoring Spark jobs while efficiently querying analytical data from Azure Data Lake Storage (ADLS) Gen2. The approach leverages DuckDB for subsecond analytical performance and utilizes an accumulo-style bucket hashing technique to organize Parquet data, significantly reducing the reliance on SQL Server for query workloads.

## Goals / Non-Goals
*       *   **Goals:**
    *   Enable subsecond query response times using DuckDB on top of Parquet data stored in ADLS Gen2.
    *   Offload analytical query processing from SQL Server to improve performance and reduce risk of contention.
## Technical Overview
### 1\. Application Stack
*   **Language:** Python (FastAPI or Flask for high-performance web APIs)
*   **Data Storage:** ADLS Gen2 (storing Parquet files hashed by accumulo-style bucket partitioning)
*   **Query Engine:** DuckDB (embedded analytical engine for local, low-latency queries)
* * *

### 2\. Architecture Overview
1. **Python Web Application (Frontend/API Layer)**
    *   Provides endpoints for job submission and query requests.
    *   Uses DuckDB to directly read and query Parquet files in ADLS Gen2.
2. **ADLS Gen2 Storage Layer**
    *   Stores analytical Parquet data.
    *   Implements accumulo-style bucket hashing to improve data locality and query performance.
3. **Monitoring & Notifications**
    *   Uses Azure Monitor and Application Insights for telemetry.
    *   Alerts and dashboards notify teams of job outcomes or failures.
* * *

## Performance Advantages
*   DuckDB enables near in-memory analytics on Parquet datasets.
*   Hash partitioning minimizes full-scan queries and ensures balanced data distribution.
*   Direct ADLS access bypasses SQL Server ingestion and improves overall throughput.
*   The system design ensures low-latency data uploads without overloading SQL infrastructure.
* * *

## Security
*   All sensitive secrets and keys are managed through Azure Key Vault.
*   Managed Identities ensure secure, passwordless access to Azure resources.
*   Network restrictions enforce access from internal systems only.

###   

# Process Flow

# Project Approvals (PRJA)

## Epic Description
#### Private ([https://app.clickup.com/t/8699b6pr2](https://app.clickup.com/t/8699b6pr2))

#### Terminology

| **Term** | **Description** |
| ---| --- |
| User | A role within the system to describe a user who does not have admin privileges. They belong to a company. |
| Admin | A role within the system to describe a user who has admin privileges. They belong to a company. |
| Admin Contact | A user who is marked as being a primary contact for a specific company. |

#### Permission & Notification Matrix

|  |  | **Admin** | **User** |
| ---| ---| ---| --- |
| **Dataset Share** | Create | ✅ | ✅ |
| Edit Notifications | ✅ | ✅ |
| **Project Creation** | Approve | ✅ | 🚫 |
| Receive Notification of Creation | 🚫 | ✅ |
| Receive Notification of Request Approval | ✅ | 🚫 |

#### Decision Log

| **Date** | **Decision** | **Why** | **Who** |
| ---| ---| ---| --- |
| 30/05/2025 | ~~A request approval email will be sent to all admins of a company.~~ |  | [@Diego Jeptha](#user_mention#93615988)[@Olivia de Kok](#user_mention#87874670) |
| All admins of a company have access to approve or decline project creation. |  |
|  | On dataset share creation:<br><br><br><br> |  | [@Diego Jeptha](#user_mention#93615988)[@Olivia de Kok](#user_mention#87874670) |
|  | Notifications describe in-app and email notifications |  | [@Diego Jeptha](#user_mention#93615988)[@Olivia de Kok](#user_mention#87874670) |

# Dataset Share Notifications: Toggle Logic

| Role | Is Admin (Primary)<br>Contact | Notification<br>Toggle | Email Template | Approval Page | Enhancement |
| ---| ---| ---| ---| ---| --- |
| Admin | Yes | Yes<br><br><br>Toggle should be turned on by default. | Approver | Yes<br><br>Due to admin role. | ✅ Disable the notification panel + provide tooltip informing the user they are an admin contact. |
| Admin | Yes | No | Approver | Yes<br><br>Due to admin role. |
| Admin | No | Yes | Approver | Yes<br><br>Due to admin role. |  |
| Admin | No | No | No email | Yes<br><br>Due to admin role. |  |
| User | Yes | Yes<br><br>Toggle should be turned on by default. | User | No | ✅ Disable the notification panel + provide tooltip informing the user they are an admin contact.<br><br>Should users be able to be set as “Admin Contacts”? |
| User | Yes | No | User | No |
| User | No | Yes | User | No |  |
| User | No | No | User | No |  |

# Create a connection when a subscription is enabled



# Selection for own use

## Epic Description
When selecting your own customer base and export as a CSV you will now get dedupe options
1. Deduplicate by Customer ID
2. Return All Distinct Records
These options allow you to return a single row per user or multiple records per user if they have purchased multiple items

# Send to Partner Capability for Selections - CSV Only

## Epic Description
Private ([https://app.clickup.com/t/8699pcjk5](https://app.clickup.com/t/8699pcjk5))
Enable marketers to distribute audiences directly to a configured Partners via a “Send to Partner” option in the Audience Builder, closing the loop between selection and activation. This new audience activation destination allows users to send audience outputs to the configured partner directly from the platform. The delivery will generate a **CSV file** and make it available to the partner via an **Incoming Audiences** section of the Audience Manager (or Shared Files module).
### Decision Log

| Date | Decision | Decision made by |
| ---| ---| --- |
|  |  |  |

### Product Requirements Document
Private ([https://app.clickup.com/9012824942/docs/8ck9jve-47512](https://app.clickup.com/9012824942/docs/8ck9jve-47512))
### **Capability Shaping**

# Architecture

### Configuration Structure

# Standardized Data Seller formats

## Epic Description
Step 1:
Private ([https://app.clickup.com/t/8699j8xt4](https://app.clickup.com/t/8699j8xt4))
The **Mapper** feature enables users to align their datasets with Omnisient’s standard schema through a mapping and validation tool. It supports creating and editing mappings from a Dataset or Data Prep level, validates required fields and data types, and stores this as **metadata** for versioning and automation for future downstream optimizations. The Mapper will support only Transactional dataset types and includes Intercom documentation to guide users through mapping and troubleshooting.

### Decision Log

| Date | User Story | Decision | Decision made by |
| ---| ---| ---| --- |
| 12/01/2026 | SSF01 | Functionality will be accessed by Admins by default only.<br><br>The functionality can be added to Users via the permission page. | Made in Platform Squad Story Review (13/01/2026) |
| 13/01/2026 | SSF01 | Out of scope: since the data type and the associated fields will be stored in config we can easily edit / remove columns and change columns from required to not required.<br><br>If we change these fields the mapping for existing datasets will break especially if they do not have a field that is now required. We need to deal with the downstream effects of changing the config.<br><br>[](https://app.clickup.com/t/869brh62k) | [@Rudolph K](#user_mention#87829005) [@Paul de Beer](#user_mention#87829001) [@Tegan Carton-Barber](#user_mention#87829007) |
| 29/01/2026 | SSF01 | Show the mapping on the following statuses:<br>Unregistered:<br>All statuses except failed<br><br>Available<br>All of them except failed<br>When an available dataset has failed there is the option to retry with a new customer identifier so this would be the primary workflow to sort out first. | [@Diego Jeptha](#user_mention#93615988) [@Olivia de Kok](#user_mention#87874670) |
| 02/02/2026 | SSF01 | AC: The mapping creation action should be visible as an entry in dataset history and activity log views.<br><br>Dataset history acts as a history view for uploaded datasets and does not show all the history associated with the dataset.<br><br>Audit logs will surface in the activity log only. | [@Olivia de Kok](#user_mention#87874670) [@Bianca](#user_mention#93602158) |

# Architecture



# Design



# Infrastructure



# Testing



# Supporting Documentation

[Dataset Type Mappings.xlsx](https://t9012824942.p.clickup-attachments.com/t9012824942/33f12772-c684-4317-9817-c939bcada81b/Dataset%20Type%20Mappings.xlsx)

# HubSpot Inspiration
![](https://t9012824942.p.clickup-attachments.com/t9012824942/45006112-b687-4be8-90d0-6b0d97bc6ae7/image.png)

# Transunion Cleanroom Analytics

## Epic Description
Private ([https://app.clickup.com/t/9012824942/OMNI-2396](https://app.clickup.com/t/9012824942/OMNI-2396))
### Decision Log

| **Date** | **Decision** | **Decision made by** |
| ---| ---| --- |
| Nov 2025 | TransUnion agreed to logo position in report v1. | Eulicia (TU) |
| 05 Dec 2025 | TransUnion agreed to changes of graph types in AC positioning meeting | Eulicia and team |
| 14 Jan 2026 | New PowerBI report will use TU colours for the charts and branding | Chess |
| 04 Feb 2026 | Blank changed to 0 on report | Ronny |
| 02 Feb 2026 | Sub-headings added to all reports | Eulicia |
| 19 Feb 2026 | Own dataset matching - will use ID - TBC based on capacity required for this sprint | Eulicia |
| 19 Feb 2026 | Partner dataset matching - will use any PII | Eulicia |
| 19 Feb 2026 | TOC In data dictionary can't be included | Jaco / Chess |

## High-level flow

[

www.figma.com

https://www.figma.com/board/p6ZdQHjzqLSnfuFUY9RsYg/Transunion-Cleanroom-Analytics?node-id=0-1&t=suYb5Vi6s8zlKdMY-1

](https://www.figma.com/board/p6ZdQHjzqLSnfuFUY9RsYg/Transunion-Cleanroom-Analytics?node-id=0-1&t=suYb5Vi6s8zlKdMY-1)

### Documentation
#### PowerBI Report Template
This needs to be edited to include TU brand elements

[X2 Report Template.pptx](https://t9012824942.p.clickup-attachments.com/t9012824942/29cea5d2-eaae-4de3-9ce8-8ea9514ba203/X2%20Report%20Template.pptx)

[X2 Report Template Transunion.pptx](https://t9012824942.p.clickup-attachments.com/t9012824942/59c65f65-0a0d-4a1b-b28b-4a38646c9bd5/X2%20Report%20Template%20Transunion.pptx)

[X2 Report Template Transunion with report details.pptx](https://t9012824942.p.clickup-attachments.com/t9012824942/ce88dec3-b15d-490a-a270-aa8ecc438d6a/X2%20Report%20Template%20Transunion%20with%20report%20details.pptx)

#### TU Branding Guidelines
This is the document we can use for all TU brand elements, such as logos, fonts and colours

[TU Brand Refrence Guide 06-08-2023\_Revised.pdf](https://t9012824942.p.clickup-attachments.com/t9012824942/e9e51cb5-f52b-4fe3-a7f8-1e289ca6491d/TU%20Brand%20Refrence%20Guide%2006-08-2023_Revised.pdf)

[BRD-2574202-LogoMiniGuide-GDE-US\_EN-US.pdf](https://t9012824942.p.clickup-attachments.com/t9012824942/1be001bf-9a6f-4712-89ae-5d0b9e6293b0/BRD-2574202-LogoMiniGuide-GDE-US_EN-US.pdf)

[LOGOS.zip](https://t9012824942.p.clickup-attachments.com/t9012824942/4504cf86-f849-4852-85f5-e1e0f22a5d5d/LOGOS.zip)

#### TU Report Requirements
This contains all Transunion's requirements for the PowerBI report

[BI Visualisation - Business Requirement Specification v 1.0.docx](https://t9012824942.p.clickup-attachments.com/t9012824942/9bf567db-7733-41f6-8973-47ab1bc88292/BI%20Visualisation%20-%20Business%20Requirement%20Specification%20v%201.0.docx)

#### TU Data Bins and Required Fields

[TU Standardised Data Set V1.pdf](https://t9012824942.p.clickup-attachments.com/t9012824942/04ca866d-46bf-4593-8a36-c778b6a34cb7/TU%20Standardised%20Data%20Set%20V1.pdf)

# Architecture

## Pipeline Design

# Reports

Here is a powerpoint version of the first page of an Overlap Report that is editable (Jaco uses PPT Templates for the reports)

[X2 Report Template Transunion with report details.pptx](https://t9012824942.p.clickup-attachments.com/t9012824942/0bf677bf-6aae-42e3-b4b6-6c30ab3456a6/X2%20Report%20Template%20Transunion%20with%20report%20details.pptx)

# Acceptance Criteria CA US 03

**Dashboard Metrics: Overlap, Thick vs Thin. Credit Risk Distribution** 

**NOTE**
This does not replace our current BI Report - this will be a 2nd report added to the project

**Visual: Sunburst Chart** 
![](https://t9012824942.p.clickup-attachments.com/t9012824942/66478d27-903e-4c5a-9eba-98fe42672c23/Screenshot%202026-01-07%20at%2006.12.49.png)

1. **Hierarchical Data Representation**
*   The sunburst chart must display three levels as detailed in the specifications in the BRS:
    *   Level 1: Overlap categories
    *   Level 2: Thick vs Thin segmentation within each overlap category
    *   Level 3: Credit Risk Distribution within each thick vs thin segment
*   Suggested naming Conventions for Level 1 overlap categories

**Phase 1** 
- [x] Overlap/ Shared Base (client + bureau)
- [x] Open Market Base (bureau only)
- [x] Client Base (client base without bureau match)
*   _NOTE: If you need to be able to filter, then will need to re-design our link table and / or data model. In this case, maybe a relatively simple overlay to create an additional dimension on top of the std link table._

**Phase 2** 
*   Overlap/ Shared Base (client + 3rd party data)
*   Open Market Base (3rd party data)
*   Client Base (client base without match to 3rd party data)
*   TU data will be a preset

**2\. Filtering Behavior**
Selecting/deselecting any segment does not redraw the sunburst. 
Instead, it filters the data feeding into the latter charts: 
*   Consumer Age Distribution
\- Estimated Income Distribution 
\- Arrears Distribution 
\- Segmentation waterfall _(This is a new chart suggestion that will visualize the drop down of the consumers)_ 
Multiple selections across levels must be supported (e.g., "On both client base and bureau" + "Thin credit" + "Prime risk" + "Super prime risk"). 
**Note: The built-in visuals library in Power BI doesn’t include a native sunburst, but you can import a certified/interaction-capable Sunburst (Sunburst by Microsoft or Powerviz) from AppSource. These support interactions (i.e. clicking a segment, and it will filter or highlight other visuals on the page)** 
_Sunburst by Microsoft is certified by Microsoft so it should be reliable and well maintained._

**3\. Data Integrity** 
\- Filtered charts (Consumer Age Distribution, Estimated Income Distribution, Arrears distribution and the Segmentation Waterfall) must be updated accurately based on the applied selections 
\- Counts and percentages in the filtered charts must reflect _the subset_ of consumers selected 

**4\. Interactivity** 
*   Hovering over a segment shows: Segment name 
*   Consumer count 
*   Percentage of total 
*   Clicking a segment applies or removes the filter dynamically 
*   A clear filter/reset option must restore all charts to the full population 
    *   _Note: Reset button is possible. Need to confirm with TU where / how (but can do that after we confirm functionality)_

**5\. Visual Specifications** 
*       *   Colours differentiate levels clearly: Overlap categories have distinct base colors 
    *   Thick vs Thin uses shades of the parent base color 
    *   Credit Risk Distribution uses further variations of the parent base colour 

**6\. Why is this helpful for the client?** 
**Data Storytelling & Clear Insights** The visual hierarchy helps clients understand how consumer segments are structured, starting from overlap as the base population, then narrowing into credit file thickness, and finally into risk tiers. This layered view makes the various segmentations easy to consume and understand. 
**Improved Usability** A single interactive chart reduces complexity. When clients select segments, other charts (Age, Income, 
Arrears) dynamically update to reflect the filtered population. Clicking segments to filter the latter charts turns the sunburst into a narrative driver, not just a static graphic. 
This creates a cohesive, interactive experience without overwhelming the user with multiple drop-downs or filters.
* * *

**Dashboard Metrics: Consumer Age Distribution, Estimated Income Distribution, Arrears distribution** 
**Visual: Doughnut Pie Charts** 
![](https://t9012824942.p.clickup-attachments.com/t9012824942/23eaa126-efd5-4e77-8e3d-7642fc90c71a/Screenshot%202026-01-07%20at%2007.26.19.png)
**1\. Data Representation** 
*   Each chart must display percentage distribution of consumers across predefined bands as per the BRS 

**2\. Dynamic Filtering** 
*   Charts must be updated in real time based on selections made in the sunburst chart 
*   When no filter is applied, charts show the full population 
*   When filters are applied, charts reflect only the filtered subset 

**3\. Visual Specifications** 
*   Each chart must: Be a doughnut chart with a clear center label showing total consumers in the filtered set 
*   Use distinct colors for each band with a consistent palette across charts 
*   Display percentages and counts on hover or in a legend 

**4\. Interactivity** 
*       *   Hovering over a segment shows: Band name/ category 
    *   Percentage of filtered population 

**5\. Filtering options for the pie charts:** 
**Interactive Filtering (Select/Deselect on Pie Charts)** 
*   Similar to the Sunburst users click on segments of the doughnut charts (Age, Income, Arrears) to include/exclude those bands 
*   Multiple selections across charts are supported 
*   Charts update visually to reflect active selections 

**Dedicated Filter Controls** 
*   Filters for Age, Income, and Arrears appear in a sidebar 
*   Users select bands via checkboxes or drop-downs 
*   Charts update dynamically to reflect filter changes 

Either approach must allow multi-level filtering, so the waterfall chart reflects the final subset. Selecting/deselecting any segment does not redraw the pie charts. 

**6\. Why is this helpful for the client?** 
**Clear Proportions at a Glance.** Instead of scanning tables or reading percentages, the client sees the shape of the segment immediately – which age group dominates, which income band is most common, and how arrears status is distributed. 
**Progressive Refinement** After narrowing the population with the sunburst, the client can further refine by age, income, and arrears directly from the charts or via dedicated filter controls. This makes the dashboard feel logical and layered, not overwhelming. 
* * *

**Visual: Waterfall Chart** 
![](https://t9012824942.p.clickup-attachments.com/t9012824942/8af3cf29-89ca-4a5c-873a-8e5b899aa45c/Screenshot%202026-01-07%20at%2008.51.51.png)
**1\. Purpose** 
*   The waterfall chart shows progressive consumer counts across key stages (e.g., Total Population → Overlap → Thick v Thin → Risk → Age → Income → Arrears) 
    *   _Note: May not be possible in standard PBI waterfall visual. Suggest Funnel chart as alternative_
*   It must adapt dynamically based on: Sunburst selections 
*   Pie chart filters 

**2\. Data Representation** 
*       *   **Start:** Total Number of Consumers (full population) 
    *   **Then:** Overlap metrics 
    *   **Next:** Thick vs Thin metrics 
    *   **Next:** Credit Risk Distribution metrics 
    *   **Finally:** Additional filters (Age, Income, Arrears) applied after these will further reduce the population shown in the waterfall 
    *   Bars must be labeled with: Metric 
    *   Count 
    *   Percentage of previous stage 

**3\. Dynamic Filtering** 
*   Waterfall must be updated in real time based on selections made in the sunburst chart & doughnut pie charts 
*   When no filter is applied, chart shows the full population 
*   When filters are applied, chart reflects only the filtered subset 

**4\. Interactivity** 
*   Hovering over a bar shows: Count 
*   Percentage drop from previous stage 
*   Clicking a bar does not apply additional filters (waterfall is for visualization only) 

**5\. Visual Specifications** 
*   Bars arranged left-to-right showing progressive reduction from Overlap…. → …Arrears 
*   Colors consistent with dashboard theme 

**6\. Why is this helpful for the client?** 
*   Shows the cumulative effect of all filters 

This provides a clear, visual story of segmentation impact. The client can see how each filtering step reduces the population. Instead of guessing how filters interact, the client sees the exact impact at each step, reducing uncertainty and putting them in control of and putting them in control of building the optimal target segment for their strategy. 
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ 
**PRODUCT OVERVIEW ACCEPTANCE CRITERIA** 
*   All metrics in the Product Overview section will always be calculated based on the current segment shown in the waterfall chart 
*   If no filters are applied, the metrics represent the entire population 

**Dashboard Metric: Product Holding – secured vs unsecured** 
**Visual: Basic Pie Chart** 
![](https://t9012824942.p.clickup-attachments.com/t9012824942/e7a062f1-52aa-442a-b74e-4614a45f02d4/Screenshot%202026-01-07%20at%2008.55.02.png)
**Dashboard Metric: Product Holding – product level** 

**Visual: Nightengale/ Rose Chart (ordering largest to smallest) OR Basic Bar Graph** 
_Note: Prefer Bar Graph if it tells the same story_
![](https://t9012824942.p.clickup-attachments.com/t9012824942/61e7e2d6-7c33-467f-a583-69f74c526703/Screenshot%202026-01-07%20at%2008.56.01.png)

Note: The built-in visuals library in Power BI doesn’t include a native Nightengale/ Rose Chart, but you can import a one from AppSource. “Rose/Donut/Oie Chart by Powerviz”. Configure it in Rose mode and sort data so that largest value appears first and the smallest appears last. 
* * *
**Dashboard Metric: Credit Activity in the last 6 months** 
**Visual: Basic Pie Chart** 
![](https://t9012824942.p.clickup-attachments.com/t9012824942/b4060ee1-dc74-4957-aeb2-3dbec15cd02c/Screenshot%202026-01-07%20at%2008.57.45.png)
_Note: Need to check our calc on this, as it seems it should add to 100%_

**Dashboard Metric: Credit Utilisation** 
**Visual: Semi-Circular Gauge Chart** 
![](https://t9012824942.p.clickup-attachments.com/t9012824942/462c72e9-edb3-44aa-86d4-7448b3d1754d/Screenshot%202026-01-07%20at%2009.49.56.png)
**Acceptance Criteria for data represented in the product overview:** 
**1\. Visual Consistency** 
*   Each chart must: Display **counts and percentages** clearly (on the chart and via hover tooltips) 
*   Use a consistent color palette aligned with dashboard theme 

**2\. Interactivity** 
*       *   Hovering over any segment or element shows: Metric name 
    *   Consumer count 
    *   Percentage of the filtered population 
    *   Charts themselves do not apply additional filters 

**3\. Why is this helpful for the clients?** 
*   **Consistency & Accuracy:** The client sees product insights for the exact segment they’ve defined, not for the full population. This ensures relevance and avoids misleading conclusions. 
*   **Logical Flow:** The dashboard feels cohesive: segmentation → demographics → waterfall → product insights. Each step builds on the previous one, reinforcing the data story they may be trying to create. 

## Future Stage:
Report will be added automatically.

# Internal Socialisation Article on CA Report 2 (Consumer Marketing)

**Feature Overview: Credit Consumer Marketing Intelligence Hub (Power BI Template)**
A production-ready Power BI data model and interactive dashboard template for the _Cleanroom Analytics_ project type, designed for TransUnion clients to privacy-safely explore, size, and create consumer audiences using combined bureau and client data.
This dashboard becomes the primary analytical interface for segmentation and decisioning within Cleanroom Analytics.
* * *

## Why this matters (Business Value)
*   Enables privacy-preserving consumer segmentation using cleanroom collaboration—no raw data movement, no exposure of PII
*   Unlocks marketing, risk, and product opportunity insights without compromising consumer or client trust
*   Scales a proven prototype into a repeatable, enterprise-grade offering across multiple client projects
*   Supports financial inclusion outcomes by allowing institutions to confidently identify and serve previously under-represented consumers using behavioral signals, not invasive data sharing
*   Moves TransUnion from _static reporting_ toward _interactive audience intelligence_ in cleanrooms
* * *

## Current State
*   Power BI template report deployable across Cleanroom Analytics projects
*   Standardised data model aligned to TU UACs
*   Branded, performant, and production-ready
* * *

## What’s included
*   New Power BI data model supporting all filtering dimensions
*   Full dashboard build including all prototype visualisations
*   Interactive segmentation for:
    *   Audience sizing
    *   Campaign targeting
    *   Risk assessment
    *   Product opportunity identification
*   Template-based deployment to multiple client cleanrooms
* * *

## Acceptance Criteria
*   Report adheres to TransUnion brand guidelines
    *   Approved colour palette
    *   Visualization standards applied consistently
*   All prototype visuals are faithfully reproduced in Power BI
*   Data model supports all agreed segmentation dimensions and filters
*   Report can be deployed as a reusable template across client projects
*   Performance SLA:
    *   Initial load and refresh < 10 seconds using OLAP
* * *

## Strategic Alignment
*   Reinforces Omnisient’s position as the privacy-first cleanroom partner
*   Demonstrates how data collaboration can unlock growth without eroding trust
*   Lays foundation for scalable, repeatable cleanroom analytics products with TransUnion

# SHAVAPI

Table of Contents
You don't have access to this Doc

## Epic Description

## Decision Log

| Date | Decision | Decision made by |
| ---| ---| --- |
| 29/01/2026 | ShavAPI 4 has been deferred to sprint 2, as Rafi has advised they will only be using it in April | Ronny |

#

# Migrate DEV/UAT to UK

# Project Details

| **Project Name** | Migrate DEV/UAT to UK |
| ---| --- |
| **Project Description** | Migrate Azure DEV + UAT environments from ZA to UK |
| **ClickUp Link** | Private ([https://app.clickup.com/t/869b3ap2z](https://app.clickup.com/t/869b3ap2z))[](https://app.clickup.com/t/869b3ap2z) |

## 1\. Executive Summary
This document proposes migrating **Development (DEV)** and **User Acceptance Testing (UAT)** environments from **Azure South Africa North** to **Azure UK South**.
The migration is driven by:
*   Development of IP that needs to be done in UK.

**Production is explicitly out of scope** for this change.
* * *
## 2\. Current State Architecture
### 2.1 Regions
*   **Primary Region:** South Africa North
*   **Secondary / DR:** Not applicable (non-production)
### 2.2 Key Azure Services
*   App Services / Functions
*   Azure SQL / Synapse / Storage Accounts
*   Key Vault
*   Application Insights / Log Analytics
*   Azure DevOps Pipelines
*   Private Endpoints
*   Embedded Power BI
*   Virtual Machines
*   Service Bus
*   AKS
*   Postgres
*   Fabric
### 2.3 Current Challenges
* * *
## 3\. Target State Architecture
### 3.1 Target Region
*   **Azure UK South**
### 3.2 Architecture Overview
*   Like-for-like service deployment where possible
*   Environment isolation maintained (DEV ≠ UAT)
*   Infrastructure as Code (Bicep / Terraform / ARM) as source of truth
*   CI/CD pipelines updated for region parameterisation
### 3.3 Non-Goals
*   No cross-region active-active
*   No production data residency changes
*   No customer-facing cutover
* * *
## 4\. Scope Definition
### In Scope
*   DEV environment
*   UAT environment
*   CI/CD configuration updates
*   Environment test data migrations
*   Shoprite environment?
    *   Keep where it is
*   New Developments? Data Authentication
### Out of Scope
*   Production
*   DR strategy changes
*   Customer data migration
*   Regulatory re-certification (ISO, SOC, etc.)
* * *
## 5\. Data & Compliance Considerations
### 5.1 Data Classification
*   DEV/UAT data classified as:
    *   Synthetic
### 5.2 Data Residency
*   No contractual or regulatory restriction preventing DEV/UAT data being hosted in the UK
*   Production data residency remains unchanged
### 5.3 Compliance Impact
*   No impact to existing compliance posture
*   Environments remain non-production and access-restricted
* * *
## 6\. Security Architecture
### 6.1 Identity & Access
*   Azure AD tenant unchanged
*   RBAC roles remain environment-scoped
*   Least-privilege access maintained
### 6.2 Secrets Management
*   New regional Key Vaults
*   No cross-region secret sharing
### 6.3 Network Security
*   Private Endpoints recreated where applicable
*   NSGs and firewall rules region-specific
*   No public exposure increase
* * *
## 7\. Networking & Connectivity
### 7.1 Ingress / Egress
*   Public endpoints updated with UK South DNS
*   IP allowlists updated where required
### 7.2 Internal Connectivity
*   No dependency on South Africa North post-migration
*   Any third-party integrations validated from UK South
* * *
## 8\. CI/CD & DevOps Impact
### 8.1 Pipelines
*   Region parameter introduced (`uksouth`)
*   Environment-specific variables isolated
*   Secrets re-bound to new Key Vaults
### 8.2 Deployment Strategy
*   Parallel deployment (old + new)
*   Smoke testing before decommission
*   No in-place migration
* * *
## 9\. Migration Approach
### Phase 1 – Prepare
*   Provision infrastructure in UK South
    *   Setup Subscriptions
    *   Provision Firewall
    *   Virtual Machines
## DEV Deployment
*   Deploy baseline services
### Phase 2 – Deploy
*   Deploy DEV workloads
    *   Omnisient platform
    *   Synapse
    *   Fabric
    *   AKS
*   Validate functionality
### Phase 3 – Validate
*   Set auto-pausing on some resources:
    *   Fabric
    *   Synapse SQL pool
*   Application testing
*   Performance sanity checks
### Phase 4 - Observability
*   Configure monitoring and alerts
### Phase 5 – Decommission
*   Disable South Africa North DEV
*   Retain backups for defined retention period
*   Remove unused resources
## UAT Deployment
*   Deploy baseline services
### Phase 2 – Deploy
*   Deploy UAT workloads
    *   Omnisient platform
    *   Synapse
    *   Fabric
    *   AKS
*   Validate functionality
### Phase 3 – Validate
*   Set auto-pausing on some resources:
    *   Fabric
    *   Synapse SQL pool
*   Application testing
*   Performance sanity checks
### Phase 4 - Observability
*   Configure monitoring and alerts
### Phase 5 – Decommission
*   Disable South Africa North UAT
*   Retain backups for defined retention period
*   Remove unused resources

* * *
## 10\. Risks & Mitigations

| Risk | Impact | Mitigation |
| ---| ---| --- |
| Misconfigured regional resources | Medium | IaC + peer review |
| Latency to SA-based services | Low | DEV/UAT only |
| Cost variance | Low | Azure Cost Management alerts |
| Hidden regional dependency | Medium | Pre-migration dependency audit |

* * *
## 11\. Cost Impact
### Expected Changes
*   Slight increase in some service SKUs
*   Reduced need for workarounds / unsupported services
### Controls
*   Budget alerts
*   Environment-level cost tracking
*   Post-migration cost review after 30 days
* * *
## 12\. Operational Impact
*   No downtime impact to customers
*   Minimal developer disruption
*   Cleaner parity with production-grade regions
* * *
## 13\. Rollback Strategy
*   South Africa North environments remain intact until sign-off
*   DNS and pipelines can be reverted within hours
*   No destructive migration steps until approval
* * *
## 14\. Decision Required from ARB
Approval to:
*   Provision DEV and UAT environments in **Azure UK South**
*   Migrate non-production workloads from **South Africa North**
*   Decommission legacy DEV/UAT post-validation
#

# Census Implementation

# Project Details

| **Project Name** | Census Implementation |
| ---| --- |
| **Project Description** | Omnisient platform will integrate with Census to easily push audiences to different ad platforms. |
| **ClickUp Link** | Private ([https://app.clickup.com/t/869azpfv8](https://app.clickup.com/t/869azpfv8)) |

# Desired ARB Outcome
**Tech Stack**:
*   Azure App Service
*   Azure Function App
    *   Scheduled job to sync audience
    *   Queue function to do initial sync
    *   Webhook to report failures
*   SQL Server / Postgres / Blob Storage?
**Security:**
*   Database access will be restricted by Census IP
**Monitoring:**
*   Census webhooks
*   Application Insights
# Technology Stack
**Existing:**
*   Azure App Service
*   Azure Function App
*   SQL Server / Postgres
# Security Considerations
*   Hashed data will be stored unencrypted in the database. Data will still be stored as encrypted at rest.
*   Database access will be public facing but access will be restricted by Census IP
*   Database will be isolated from the rest of databases
*   Webhook will be restricted by IP and auth token
# Cost Considerations
*   The extra database will add to the costs
# Open Questions
1. How long should we keep the data for, for a specific upload? What will trigger a clean up?
# To-Be Diagram
![](https://t9012824942.p.clickup-attachments.com/t9012824942/6dec0c07-5b13-45f0-a5b7-ef9826936a44/Census%20Implementation.drawio%20(1).png)

# Omnisient Look-Alike



# FNB Batch Enablement



# Predictive Modelling (Dollar General)

| **Reviewer** | **Reviewed/Verified** | **Last Reviewed** |
| ---| ---| --- |
| ??? | ✅ / ❌ | \- |

# Table of Contents
* * *
# Overview
*   **Description of project:** The Predictive Modelling on Retail Data project is a U.S.-exclusive initiative designed to support financial inclusion through privacy-preserving data collaboration.
*   **Purpose of project:**  It enables financial institutions, insurers, and retail analytics teams to gain deeper insight into underserved communities by combining anonymized retail purchase data with financial transaction data.
*   **Regions Affected:** USA
## Supported Features \[WIP\]

| **Feature** | **Enabled** | **Notes** |
| ---| ---| --- |
| **Project Creation Wizard** |
| Project Details | ✅ | Name, Description, Additional Users |
| Add Own Table | ✅ | One/Multiple |
| Add Shared Table | ❌ | One/Multiple |
| Back Office Approvals | ❌ | Private ([https://app.clickup.com/9012824942/docs/8ck9jve-21812/8ck9jve-15932](https://app.clickup.com/9012824942/docs/8ck9jve-21812/8ck9jve-15932)) |
| **Project Detail View** |
| Roles + Permissions | ✅ | Governs Access to Project |
| View Users and Permissions | ✅ | All project users |
| Manage Users | ✅ | Only if Owner |
| View Table Relationships | ❌ | Globally and per Table. Not available on Metadata Tables |
| Add Own Table After Creation | ❌ |  |
| Add Partner Table After Creation | ❌ |  |
| Data Processing Reports | ❌ | Only available on Client and Partner tables |
| Open with Analytical Tools | ✅ | Jupyter is Subscription dependent. Available data is dependent on dataset share agreement for shared/partner datasets:<br><br><br> |
| Reports | ❌ |  |
| Custom Reports | ❌ | Feature not developed yet |
|  | ❌ | Dependent if selections were enabled and what columns were defined in the dataset share agreement for shared/partner datasets:<br><br><br> |
| Back Office Selection Approvals | ❌ | Private ([https://app.clickup.com/9012824942/docs/8ck9jve-21812/8ck9jve-16072](https://app.clickup.com/9012824942/docs/8ck9jve-21812/8ck9jve-16072)) |
| Activations on Selections | ❌ | Dependent on Selection Type |
| Back Office Audience Approvals | ❌ | Private ([https://app.clickup.com/9012824942/docs/8ck9jve-21812/8ck9jve-15672](https://app.clickup.com/9012824942/docs/8ck9jve-21812/8ck9jve-15672)) |

* * *
# Flow Diagram
![](https://t9012824942.p.clickup-attachments.com/t9012824942/8f50f2c4-ce2e-49cb-8863-ccde4c7cecae/image.png) 
* * *
# Business Rules
*   **Supported Match Fields:** 
*   **Supported Datasets:** 
*   **Backoffice Approval Required:**
*   **Expected Project Outputs:** 
*   **Stability (Unstable / Stable):** 
* * *
# Pipeline Details
*   **Name:** Retail Predictive Modelling
*   **Parameters:** 
    *   Primary\_Client\_Name
    *   ProjectID
    *   Environment

* * *
# PowerBI Base Template Details
1. **Template Name:**
2. **Report ID:**
3. **Workspace ID:**
4. **Regions Affected:**

1. **Template Name:**
2. **Report ID:**
3. **Workspace ID:**
4. **Regions Affected:**
* * *
# User Guidance
## Help Centre Articles
*   [Link](https://help.omnisient.com/en/articles/11414340-predictive-modelling-on-retail-data-usa-only)

* * *
# Additional Notes

The Predictive Modelling on Retail Data project is a U.S.-exclusive initiative designed to support financial inclusion through privacy-preserving data collaboration. It enables financial institutions, insurers, and retail analytics teams to gain deeper insight into underserved communities by combining anonymized retail purchase data with financial transaction data.

The platform matches datasets with a **Retro Date**, ensuring that no Personally Identifiable Information (PII) is exposed. This secure matching process allows organizations to analyze consumer spending patterns, financial behavior, creditworthiness indicators, and community segmentation without compromising privacy.

# Supporting Documentation

#

# Predictive Modelling on Retail Data for USA (fin incl.) Dollar General (Full ticket)

## 📝 Notes
*   This is a subscription template for Dollar General Subscribers
*   It is only allowed in the USA environment
*   You can add your own table
*   You can add additional own tables once the project has been compiled
*   You don't add a shared table
*   Best match is not featured on the UI, we will use Profile\_ID Column
*   No selections
*   No reports
*   Back office needs to approve the project

It will be called "Predictive Modelling on Retail data"

### Possible names:
*   Retail Predictive Modelling
*   Dollar General Financial Inclusion
*   Predictive Modelling on Retail data (chosen)

![](https://t9012824942.p.clickup-attachments.com/t9012824942/4247d820-d269-4e2e-8ba0-bc217ef44718/image.png)

[Project Flow.xlsx](https://t9012824942.p.clickup-attachments.com/t9012824942/7971060d-c359-49ee-9aed-3bde8369e167/Project%20Flow.xlsx)

# 📝 Requirements
## → Context/Why
We need to create a Financial Inclusion Project for use in the USA. For the majority of this piece, we will reuse the financial inclusion template. However, it will need a new matching field (the Profile\_ID column).

The project is designed to help organizations better understand underserved communities, identify financial behavior patterns, and improve access to financial services.
## → High Level Flow
🔗 [Link to high-level Figjam flow here](https://www.figma.com/board/kKNH7PUbixjBtEHHzNoDsk/Predictive-modelling-on-Retail-data?node-id=1-226&t=pRElzkPN3d8qrSLO-1)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/dcff9fb8-0c1a-4f8c-aa45-e28bab9a9a06/image.png)
## → High-Level Requirements
*   This project will follow the existing Financial Inclusion template, but using Profile\_ID for the matching column.
*   It will be for USA only - and specifically for Dollar General subscribers.
*   Need to create a subscription for Dollar General subscribers.
*   Uses anonymized customer data from Dollar General and a financial institution.
*   Matches customer records based on a Profile\_ID column and a Retro Date.
*   Helps businesses assess financial behaviours, spending patterns, and creditworthiness.
## → Process
1. Stored Proc (SP) and pipeline for pre-aggregations (Jaco - Feb) (features ticket)
2. Updated Non-ID matching SP - to cater for selecting only accurate matches (Neels - Mar) (new ticket with specific requirements)
3. SP to prepare Non-ID results for Features SP (Jaco - Mar) (new ticket with specific requirements)
4. SP to build the Features (Jaco - Feb) (features ticket)
5. Pipeline to run the usual bits (create project, kanon etc.) as well as new and updated SPs above (Neels - Apr)
6. UI edits and calling the pipeline (Motla - May)
## → Technical Requirements
🔗 [Tech Spec](https://omnisientworkspace.slack.com/docs/T018NR32PGV/F08DLFZ069Y)
## → Acceptance Criteria
![](https://t9012824942.p.clickup-attachments.com/t9012824942/c21e73ba-4521-47f3-aca8-e4e090f1efe1/image.png)

# ⚠️ Dependencies

# 💭 Open Questions
How will the non\_ID part work?
Will we be able to match on "buckets" of data with high scores?

# 🎨 High-Fidelity Designs
🔗 [Link](https://www.figma.com/design/le2kOHy6xkS57nfALYM811/Project-Templates?node-id=1290-13783&t=gTcvylu7wXlhUiUH-1) to high-fidelity Figma designs here
## Project Template and Icon
![](https://t9012824942.p.clickup-attachments.com/t9012824942/eb591c00-66b9-4c3e-98c9-8bb90415471a/image.png)![](https://t9012824942.p.clickup-attachments.com/t9012824942/a0b74fc3-f288-4aff-9d56-f470b9833188/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/2fef68f9-a56f-4962-beca-1a9db0093415/image.png)
## Project Steps
## 1.1 Empty state
![](https://t9012824942.p.clickup-attachments.com/t9012824942/0c2e6114-f569-4eff-88f6-b72614a749d8/image.png)
## 1.2 User Complete details
![](https://t9012824942.p.clickup-attachments.com/t9012824942/0888dc50-04d1-4dab-9be2-bfdb77b95782/image.png)
## 2\. Add Dataset
![](https://t9012824942.p.clickup-attachments.com/t9012824942/958452df-f536-4cc3-9987-f1810d16b915/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/cab0de8d-bca0-42af-9db0-53f1c1769e1c/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/a6accb02-dcea-4e0f-8aad-1e593e08e70b/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/d5f0bb1c-a8b0-4c7a-8872-846b6ffe14d7/image.png)
## Chosen Datataset
![](https://t9012824942.p.clickup-attachments.com/t9012824942/cae251e6-1b09-4f6b-9780-203a998447e6/image.png)
## Projects Dashboard
![](https://t9012824942.p.clickup-attachments.com/t9012824942/ae09a5cf-ea43-4483-a251-7699f3c8da1b/image.png)
# 🛠️ Engineering Task Breakdown

...

# Meetings
[Slack Canvas here](https://omnisientworkspace.slack.com/docs/T018NR32PGV/F08FC0N5P28) for meeting notes
## Kickoff meeting 25/02/25
### 1\. Develop Stored Procedure for Feature Calculations
*   Jaco is responsible for creating the stored procedure to calculate financial inclusion features using retail data.
*   Adjust the procedure to default the retro date to the current date.
### 2\. Review and Refine the Project Template & Subscription Model
*   Conduct a structured review of the user experience (UX).
*   Define and implement a subscription model restricting access to financial inclusion features for subscribed clients.
### 3\. Improve Data Matching Methods
*   Adapt non-ID matching processes for Dollar General, as it relies on general PII rather than ID-based matching like ShopRite.
*   Enhance credit risk scoring by refining non-ID matching techniques.
*   Ensure the system allows clients to select specific fields for matching.
*   Update validation checks to align with the new matching criteria.
### 4\. Implement Engineering and Structural Changes
*   Assess the impact of region-specific data management on financial inclusion strategies.
*   Identify necessary structural modifications before development begins.
*   Integrate new PII handling methods and ensure compliance with data security requirements.
### 5\. Project Timeline and Development Phases
*   Target completion of key tasks by April to align with the financial year-end.
*   Evaluate feasibility within the March sprint and adjust resource allocation if needed.
*   Collaborate to prevent delays and streamline execution.
### 6\. Documentation & Coordination
*   Chess Ashley-Cooper to compile a list of required changes and distribute notes to the team for alignment.
*   Maintain ongoing collaboration to ensure smooth project execution.

[https://t9012824942.p.clickup-attachments.com/t9012824942/ff6fec6c-d42e-458f-81ae-3e266c3ebbde/Go%20over%20financial%20inclusion%20for%20Dollar%20General-20250225\_111604-Meeting%20Recording.mp4?view=open](https://t9012824942.p.clickup-attachments.com/t9012824942/ff6fec6c-d42e-458f-81ae-3e266c3ebbde/Go%20over%20financial%20inclusion%20for%20Dollar%20General-20250225_111604-Meeting%20Recording.mp4?view=open)

## Meetings 26/03/25
### Project Overview: Dollar General – Non-ID and Feature Development Alignment
#### Roles & Responsibilities
*   Neels Oosthuizen: Responsible for non-ID component development.
*   Jaco: Responsible for feature development.
*   Ronny Tack: Oversight and integration coordination.
#### Core Requirements
*   Link non-ID matching results to customer identifiers (e.g., loyalty account ID).
*   Ensure Neels and Jaco's outputs are aligned and interoperable.
*   Coordinate integration tasks with Jaco to avoid timeline conflicts.
* * *
#### Integration Tasks
*   Add Crest IDE key to the partner table.
*   Use Dollar General data fields (email, phone, first name, surname).
*   Exclude loyalty account ID from dummy data for realistic testing simulation.
* * *
#### Pipeline & Matching Logic
*   Create stored procedures to streamline the non-ID pipeline.
*   Define user-adjustable match confidence cutoff levels (vital for financial inclusion and credit scoring).
*   Example: first name + surname + DOB = 99% match accuracy.
* * *
#### Financial Inclusion Pipeline
*   Define and apply filtering rules (pre- vs. post-deduplication).
*   Clarify final partner table creation criteria (may require partner consultation, e.g., call with Paul).
*   Consider enhancing filtering capabilities in future updates.
* * *
#### Timeline & Dependencies
*   March schedule is tight due to overlapping tasks.
*   Neels to complete point 2 by week’s end to unblock Jaco.
*   Neels to support Jaco’s queries during feature implementation (point 3).

[https://t9012824942.p.clickup-attachments.com/t9012824942/efc25dba-25b9-4c1c-adfc-0ab545a82461/US%20DG%20Fin%20Incl.%20Features%20%26%20Non-ID%20-%20Align%20on%20tasks-20250326\_123437-Meeting%20Recording.mp4?view=open](https://t9012824942.p.clickup-attachments.com/t9012824942/efc25dba-25b9-4c1c-adfc-0ab545a82461/US%20DG%20Fin%20Incl.%20Features%20%26%20Non-ID%20-%20Align%20on%20tasks-20250326_123437-Meeting%20Recording.mp4?view=open)

![](https://t9012824942.p.clickup-attachments.com/t9012824942/77451e7e-6a3f-45cc-a309-5e14f16b45a8/image.png)
[https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53712](https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53712)

## Meeting 31 March 2025
*   Non-ID Testing
    *   Non-ID process is complete; a few test cases done.
    *   Ready for UAT testing by afternoon/tomorrow.
    *   Non-ID covers all projects and must be tested across them.
    *   Must run Non-ID first (with SKey in partner table).
    *   Output from Non-ID must be correct and sufficient for subsequent stored procedure.
*   Stored Procedure (StoreProc) Testing
    *   StoreProc prepares data for feature StoreProc.
    *   Must run on approved tables after Non-ID.
    *   Needs a dedicated ticket based on the tech spec.
    *   Certain ranks must be excluded.
    *   Must cut off data below the phone number.
    *   StoreProc must be tested post-Non-ID for correctness.
*   UAT Testing
    *   Manual testing for now.
    *   Test sequence: Non-ID → StoreProc → Feature StoreProc.
    *   Must test with proper dataset through full pipeline.
    *   Paul and Jaco involved in UAT testing.
    *   Define test case to avoid full end-to-end run each time.
*   Test Data & Table Structure
    *   Jaco to confirm a suitable test table and structure.
    *   Jaco to update loyalty account to SKey (to be tested this week).
    *   DG data resides in USA DW; components still available in SA.
*   Tickets & Documentation
    *   Create 3 separate tickets for tracking.
    *   Non-ID needs ticket for tracking and release.
    *   Feature testing to follow after sprint.
    *   Paul to update and populate tech spec details.
*   Quality Assurance
    *   Overlaps and custom cases to be checked by QA.

![](https://t9012824942.p.clickup-attachments.com/t9012824942/34614210-0cdd-4383-a43f-90e7ddad085b/image.png)
[https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53672](https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53672)

# Comments
![](https://t9012824942.p.clickup-attachments.com/t9012824942/31ab8bdd-7509-48fc-b9e5-b34b0327eba5/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/acd8ada0-b783-48ef-bc21-396402e65183/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/fae8839d-f084-40e3-939f-b06e9b708aeb/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/26752cd5-c13c-4625-b306-bd7a8739bed3/image.png)

# Predictive Modelling on Retail Data for USA (fin incl.) Dollar General  (Main Ticket)

# 📝 Notes
*   This is a subscription template for Dollar General Subscribers
*   It is only allowed in the USA environment
*   You can add your own table
*   You can add additional own tables once the project has been compiled
*   You don't add a shared table
*   Best match is not featured on the UI, we will use Profile\_ID Column
*   No selections
*   No reports
*   Back office needs to approve the project

It will be called "Predictive Modelling on Retail data"

## Possible names:
*   Retail Predictive Modelling
*   Dollar General Financial Inclusion
*   Predictive Modelling on Retail data (chosen)

![](https://t9012824942.p.clickup-attachments.com/t9012824942/9fc78823-f93f-490d-aa7b-354a090807f2/image.png)

[Project Flow.xlsx](https://t9012824942.p.clickup-attachments.com/t9012824942/4e3a513c-d44f-4d36-8302-7aa471562310/Project%20Flow.xlsx)

# 📝 Requirements
## → Context/Why
We need to create a Financial Inclusion Project for use in the USA. For the majority of this piece, we will reuse the financial inclusion template. However, it will need a new matching field (the Profile\_ID column).

The project is designed to help organizations better understand underserved communities, identify financial behavior patterns, and improve access to financial services.
## → High Level Flow
🔗 [Link to high-level Figjam flow here](https://www.figma.com/board/kKNH7PUbixjBtEHHzNoDsk/Predictive-modelling-on-Retail-data?node-id=1-226&t=pRElzkPN3d8qrSLO-1)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/35a47eb5-1d9a-4a84-888c-f0a817760841/image.png)
## → High-Level Requirements
*   This project will follow the existing Financial Inclusion template, but using Profile\_ID for the matching column.
*   It will be for USA only - and specifically for Dollar General subscribers.
*   Need to create a subscription for Dollar General subscribers.
*   Uses anonymized customer data from Dollar General and a financial institution.
*   Matches customer records based on a Profile\_ID column and a Retro Date.
*   Helps businesses assess financial behaviours, spending patterns, and creditworthiness.
## → Process
1. Stored Proc (SP) and pipeline for pre-aggregations (Jaco - Feb) (features ticket)
2. Updated Non-ID matching SP - to cater for selecting only accurate matches (Neels - Mar) (new ticket with specific requirements)
3. SP to prepare Non-ID results for Features SP (Jaco - Mar) (new ticket with specific requirements)
4. SP to build the Features (Jaco - Feb) (features ticket)
5. Pipeline to run the usual bits (create project, kanon etc.) as well as new and updated SPs above (Neels - Apr)
6. UI edits and calling the pipeline (Motla - May)
## → Technical Requirements
🔗 [Tech Spec](https://omnisientworkspace.slack.com/docs/T018NR32PGV/F08DLFZ069Y)

## → Acceptance Criteria
*   ✅ User able to use a registered dataset with email/phone/firstname/surname, retrodate and cust\_id
*   ✅ FI project created for Dollar General and subscribers the predictive modelling template
*   ✅ USA only
*   ❌ Where the project will automatically run, without failing:
*   ✅ Customer records matched on a Profile\_ID column and a Retro Date
*   ✅ All without any manual intervention (except for necessary approvals etc.)
*   ✅ Subscription created for Dollar General and subscribers
*   ✅ Only visible for Dollar General and subscribers
*   ✅ User can add multiple datasets
*   ✅ User can add another dataset once the project has compiled

# ⚠️ Dependencies
![](https://t9012824942.p.clickup-attachments.com/t9012824942/95a297ed-a014-458b-840a-7eef12d05796/image.png)
[https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53672](https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53672)

# 💭 Open Questions
How will the non\_ID part work?
Will we be able to match on "buckets" of data with high scores?
* * *
# 🎨 High-Fidelity Designs
🔗 [Link](https://www.figma.com/design/le2kOHy6xkS57nfALYM811/Project-Templates?node-id=1290-13783&t=gTcvylu7wXlhUiUH-1) to high-fidelity Figma designs here

# 💡 CX

| Item | Link |
| ---| --- |
| Article | [Article](about:blank) to be released in June sprint |
| News | [USA Only](https://app.intercom.com/a/apps/ns0zsqth/outbound/tour/49198658?mode=edit) |
| Banner | N/A |
| Figma Slides | [Link](https://www.figma.com/slides/iQ7NJ6mbcXoKtrwDVkURx1/June-2025-Sprint-Demo--Copy-?node-id=20004-63&t=p8Ss9EM8jRf0HhIa-1) |
| Training/Internal Article | [Article](about:blank) to be released in June sprint |
| Newsletter | N/A as it is company specific and region specific |

# Testing Evidence
_Tests:_
QA coverage
Includes functional, edge case, and UI tests.
[Predictive Modelling – Test Scenarios.loop](https://omnisient.sharepoint.com/:fl:/g/contentstorage/CSP_9a54cbb8-60a3-4ba4-8782-cae1cb13e73b/EQL4AdUal9hNgSN28NuXmp8BJnWvpvb--KIPaliCeGPpRw?e=NkPTXf&nav=cz0lMkZjb250ZW50c3RvcmFnZSUyRkNTUF85YTU0Y2JiOC02MGEzLTRiYTQtODc4Mi1jYWUxY2IxM2U3M2ImZD1iJTIxdU10VW1xTmdwRXVIZ3NyaHl4UG5PMlZqV25RbVJQdEpqakViNFd6VmdBZ1JISU8wODF2WlJiM09xTkxQbU1qRCZmPTAxTFZNWlhVQUM3QUE1S0dVWDNCR1lDSTNXNkROWlBHVTcmYz0lMkYmYT1Mb29wQXBwJnA9JTQwZmx1aWR4JTJGbG9vcC1wYWdlLWNvbnRhaW5lciZ4PSU3QiUyMnclMjIlM0ElMjJUMFJUVUh4dmJXNXBjMmxsYm5RdWMyaGhjbVZ3YjJsdWRDNWpiMjE4WWlGMVRYUlZiWEZPWjNCRmRVaG5jM0pvZVhoUWJrOHlWbXBYYmxGdFVsQjBTbXBxUldJMFYzcFdaMEZuVWtoSlR6QTRNWFphVW1JelQzRk9URkJ0VFdwRWZEQXhURlpOV2xoVlJGZ3pRbGd5U1ZGUk1qTk9SVnBVUVVKUFQxWkZXa3N5VkU4JTNEJTIyJTJDJTIyaSUyMiUzQSUyMjljZTczZjllLTY1ZGYtNGQyNi1iZjVkLTI5ZDI2ODA1YjIzYyUyMiU3RA%3D%3D)
## Acceptance Criteria UAT
![](https://t9012824942.p.clickup-attachments.com/t9012824942/5e18950d-3577-44fb-9ce2-c930a533d247/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/1bd13aca-b1d6-4076-b957-64087f172be5/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/af6a3433-a438-4463-8ed4-d71de823b3b7/image.png)
Feedback from Paul (Slack group):

```sql
Paul  4:30 AM
In summary:
The customers are correctly matched
The relevant tables contain the SKEYS
The customers are correctly matched to sales
These specific special characters are assigned correctly
Our testing data sucks and we can't test calculations etc
4:32 Paul
Since we were in any case planning on testing the calculations in the US I think this looks good and can continue into prod when ready.  Someone just needs to check Bianca's issue with adding a table to the project after the fact.
```

* * *
# Meetings
[Slack Canvas here](https://omnisientworkspace.slack.com/docs/T018NR32PGV/F08FC0N5P28) for meeting notes
## 1\. Develop Stored Procedure for Feature Calculations
*   Jaco is responsible for creating the stored procedure to calculate financial inclusion features using retail data.
*   Adjust the procedure to default the retro date to the current date.
## 2\. Review and Refine the Project Template & Subscription Model
*   Conduct a structured review of the user experience (UX).
*   Define and implement a subscription model restricting access to financial inclusion features for subscribed clients.
## 3\. Improve Data Matching Methods
*   Adapt non-ID matching processes for Dollar General, as it relies on general PII rather than ID-based matching like ShopRite.
*   Enhance credit risk scoring by refining non-ID matching techniques.
*   Ensure the system allows clients to select specific fields for matching.
*   Update validation checks to align with the new matching criteria.
## 4\. Implement Engineering and Structural Changes
*   Assess the impact of region-specific data management on financial inclusion strategies.
*   Identify necessary structural modifications before development begins.
*   Integrate new PII handling methods and ensure compliance with data security requirements.
## 5\. Project Timeline and Development Phases
*   Target completion of key tasks by April to align with the financial year-end.
*   Evaluate feasibility within the March sprint and adjust resource allocation if needed.
*   Collaborate to prevent delays and streamline execution.
## 6\. Documentation & Coordination
*   Chess Ashley-Cooper to compile a list of required changes and distribute notes to the team for alignment.
*   Maintain ongoing collaboration to ensure smooth project execution.

# Meeting 26/03/25
## Project Overview: Dollar General – Non-ID and Feature Development Alignment
## Roles & Responsibilities
*   Neels Oosthuizen: Responsible for non-ID component development.
*   Jaco: Responsible for feature development.
*   Ronny Tack: Oversight and integration coordination.
* * *
## Core Requirements
*   Link non-ID matching results to customer identifiers (e.g., loyalty account ID).
*   Ensure Neels and Jaco's outputs are aligned and interoperable.
*   Coordinate integration tasks with Jaco to avoid timeline conflicts.
* * *
## Integration Tasks
*   Add Crest IDE key to the partner table.
*   Use Dollar General data fields (email, phone, first name, surname).
*   Exclude loyalty account ID from dummy data for realistic testing simulation.
* * *
## Pipeline & Matching Logic
*   Create stored procedures to streamline the non-ID pipeline.
*   Define user-adjustable match confidence cutoff levels (vital for financial inclusion and credit scoring).
*   Example: first name + surname + DOB = 99% match accuracy.
* * *
## Financial Inclusion Pipeline
*   Define and apply filtering rules (pre- vs. post-deduplication).
*   Clarify final partner table creation criteria (may require partner consultation, e.g., call with Paul).
*   Consider enhancing filtering capabilities in future updates.
* * *
## Timeline & Dependencies
*   March schedule is tight due to overlapping tasks.
*   Neels to complete point 2 by week’s end to unblock Jaco.
*   Neels to support Jaco’s queries during feature implementation (point 3).
![](https://t9012824942.p.clickup-attachments.com/t9012824942/9f64eeab-7659-4147-b3b9-46a77d7bec08/image.png)
[https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53592](https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53592)[https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53712](https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53712)[https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53692](https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53692)

# Comments
![](https://t9012824942.p.clickup-attachments.com/t9012824942/e0361660-e830-4b0e-8604-fbec5700f250/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/b700eb0e-f2d4-4066-991d-ad8f35ee1aa5/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/70f074c7-213a-445f-a68a-334b465133a4/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/8cd89a33-355c-4186-aef9-03db91d93c37/image.png)

[20210825 - Match accuracy estimates.xlsx](https://t9012824942.p.clickup-attachments.com/t9012824942/ca59e906-d531-4ffa-8892-f48900b5f7b1/20210825%20-%20Match%20accuracy%20estimates.xlsx)

![](https://t9012824942.p.clickup-attachments.com/t9012824942/6d1fbe19-14b0-4711-8e61-5ea2a72e8e38/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/57e315d3-9af1-4c09-a4b6-35c1e7841b3d/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/84644ce2-57bf-4dcf-82ca-65f16bbc0fb0/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/58dbc0cd-c141-4304-95fd-5aac91698cbc/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/da8d6cc9-2d4b-4180-97f9-8bf8c05bbcd7/image.png)

# Predictive Modelling on Retail Data (USA) Non_ID

![](https://t9012824942.p.clickup-attachments.com/t9012824942/942caca0-03f0-4be6-92bf-4657dd1bd741/image.png)

# Meetings
## MEETING 1:
Subject: Go Over Financial Inclusion for Dollar General
Date: 25 Feb 2025

*   Match Only field not yet a necessity, could be revisited later.
*   Updated NonID to get a new parameter to only allow rules within a certain rank number (25m)
    *   Either at the beginning or the end of the processing the rules should be applied (ignored vs deleted out of the linking table)

# Item 1: Add the custidskey SKEY key into the partner table
## Description:
I have added detail into component 4 for the adjustment SP that needs to run after non-id.  I mention the tables I think are the correct ones to use to get the final selected matches back to the custidskey for both parties, but I can't find anything that links the partner id back to the partner custidskey.  Please have a look at the data flow section and just update how we get from the matched Own ID and Partner ID to the two custidskeys (or the raw custid is also fine for the partner). (edited) 

## DEVELOPMENT:
When the partner table gets created, ensure that the old customer identifier is added into the table. This is done on the final stored procedure when the final table is created.

# Comments
![](https://t9012824942.p.clickup-attachments.com/t9012824942/2fffef79-569c-456a-a8df-9d2e9e055571/image.png)

# Pre-aggregation of tables into it's own pipeline - Predictive Modelling USA

# Context / Why
We need the pre-aggregation of tables into it's own pipeline - for Predictive Modelling USA
‼️ This is a technical ticket

* * *
# Requirements for DE

- [x] Pushing through different steps of devops
- [x] Add a trigger to the pipeline
- [x] Schedule to be weekly ( Jaco will confirm with Paul) if it should be weekend or weekly. Confirmed this will run after hours in US region on a Monday (11PM ZA time)
- [x] Features are dependant of this process, it aggregates the sales before we run the features.

# 🔗 Please refer to linked tickets for previous requirements
[https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53652](https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53652)[https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53712](https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53712)

# DE point 5 - Predictive Modelling on Retail Data for USA (fin incl.) Dollar General  (April Sprint)

# 📝 Notes
*   This is a subscription template for Dollar General Subscribers
*   It is only allowed in the USA environment
*   You can add your own table
*   You can add additional own tables once the project has been compiled
*   You don't add a shared table
*   Best match is not featured on the UI, we will use Profile\_ID Column
*   No selections
*   No reports
*   Back office needs to approve the project

It will be called "Predictive Modelling on Retail data

[Project Flow.xlsx](https://t9012824942.p.clickup-attachments.com/t9012824942/b29a86e3-80dd-43ef-8ec3-d761c61ffae4/Project%20Flow.xlsx)

# 📝 Requirements
## → Context/Why
We need to create a Financial Inclusion Project for use in the USA. For the majority of this piece, we will reuse the financial inclusion template. However, it will need a new matching field (the Profile\_ID column).

The project is designed to help organizations better understand underserved communities, identify financial behavior patterns, and improve access to financial services.
## → High Level Flow
🔗 [Link to high-level Figjam flow here](https://www.figma.com/board/kKNH7PUbixjBtEHHzNoDsk/Predictive-modelling-on-Retail-data?node-id=1-226&t=pRElzkPN3d8qrSLO-1)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/b2b28857-fc8f-4c91-aeb1-a8aed0971b3d/image.png)

## → High-Level Requirements
*   This project will follow the existing Financial Inclusion template, but using Profile\_ID for the matching column.
*   It will be for USA only - and specifically for Dollar General subscribers.
*   Need to create a subscription for Dollar General subscribers.
*   Uses anonymized customer data from Dollar General and a financial institution.
*   Matches customer records based on a Profile\_ID column and a Retro Date.
*   Helps businesses assess financial behaviours, spending patterns, and creditworthiness.
## → Jaco requirements
1. Pipeline to run the usual bits (create project, kanon etc.) as well as new and updated SPs above
## → Technical Requirements
🔗 [Tech Spec](https://omnisientworkspace.slack.com/docs/T018NR32PGV/F08DLFZ069Y)
## → Acceptance Criteria
*   ✅ User able to use a registered dataset with email/phone/firstname/surname, retrodate and cust\_id
*   ✅ FI project created for Dollar General and subscribers the predictive modelling template
*   ✅ USA only
*   ✅ Where the project will automatically run, without failing:
*   ✅ Customer records matched on a Profile\_ID column and a Retro Date
*   ✅ All without any manual intervention (except for necessary approvals etc.)
*   ✅ Subscription created for Dollar General and subscribers
*   ✅ Only visible for Dollar General and subscribers

# ⚠️ Dependencies
[https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53592](https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53592)[https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53652](https://app.clickup.com/9012824942/docs/8ck9jve-35012/8ck9jve-53652)

# 💭 Open Questions
How will the non\_ID part work?
Will we be able to match on "buckets" of data with high scores?

# 🎨 High-Fidelity Designs
🔗 [Link](https://www.figma.com/design/le2kOHy6xkS57nfALYM811/Project-Templates?node-id=1290-13783&t=gTcvylu7wXlhUiUH-1) to high-fidelity Figma designs here

# Meetings
[Slack Canvas here](https://omnisientworkspace.slack.com/docs/T018NR32PGV/F08FC0N5P28) for meeting notes
## Kickoff meeting 25/02/25
### 1\. Develop Stored Procedure for Feature Calculations
*   Jaco is responsible for creating the stored procedure to calculate financial inclusion features using retail data.
*   Adjust the procedure to default the retro date to the current date.
### 2\. Review and Refine the Project Template & Subscription Model
*   Conduct a structured review of the user experience (UX).
*   Define and implement a subscription model restricting access to financial inclusion features for subscribed clients.
### 3\. Improve Data Matching Methods
*   Adapt non-ID matching processes for Dollar General, as it relies on general PII rather than ID-based matching like ShopRite.
*   Enhance credit risk scoring by refining non-ID matching techniques.
*   Ensure the system allows clients to select specific fields for matching.
*   Update validation checks to align with the new matching criteria.
### 4\. Implement Engineering and Structural Changes
*   Assess the impact of region-specific data management on financial inclusion strategies.
*   Identify necessary structural modifications before development begins.
*   Integrate new PII handling methods and ensure compliance with data security requirements.
### 5\. Project Timeline and Development Phases
*   Target completion of key tasks by April to align with the financial year-end.
*   Evaluate feasibility within the March sprint and adjust resource allocation if needed.
*   Collaborate to prevent delays and streamline execution.
### 6\. Documentation & Coordination
*   Chess Ashley-Cooper to compile a list of required changes and distribute notes to the team for alignment.
*   Maintain ongoing collaboration to ensure smooth project execution.

# Meeting 26/03/25
## Project Overview: Dollar General – Non-ID and Feature Development Alignment
### Roles & Responsibilities
*   Neels Oosthuizen: Responsible for non-ID component development.
*   Jaco: Responsible for feature development.
*   Ronny Tack: Oversight and integration coordination.
* * *
### Core Requirements
*   Link non-ID matching results to customer identifiers (e.g., loyalty account ID).
*   Ensure Neels and Jaco's outputs are aligned and interoperable.
*   Coordinate integration tasks with Jaco to avoid timeline conflicts.
* * *
### Integration Tasks
*   Add Crest IDE key to the partner table.
*   Use Dollar General data fields (email, phone, first name, surname).
*   Exclude loyalty account ID from dummy data for realistic testing simulation.
* * *
### Pipeline & Matching Logic
*   Create stored procedures to streamline the non-ID pipeline.
*   Define user-adjustable match confidence cutoff levels (vital for financial inclusion and credit scoring).
*   Example: first name + surname + DOB = 99% match accuracy.
* * *
### Financial Inclusion Pipeline
*   Define and apply filtering rules (pre- vs. post-deduplication).
*   Clarify final partner table creation criteria (may require partner consultation, e.g., call with Paul).
*   Consider enhancing filtering capabilities in future updates.
* * *
### Timeline & Dependencies
*   March schedule is tight due to overlapping tasks.
*   Neels to complete point 2 by week’s end to unblock Jaco.
*   Neels to support Jaco’s queries during feature implementation (point 3).

# Comments
![](https://t9012824942.p.clickup-attachments.com/t9012824942/1a539ba4-59d8-4ddb-8e76-1361ae196528/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/deed5d2c-e7bd-4eec-b1be-9d47bf65230f/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/7a92b03f-a529-4350-a8a5-819f2e87cc0a/image.png)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/213baefb-0aef-4620-a0b2-d909ad9d5bf5/image.png)

[20210825 - Match accuracy estimates.xlsx](https://t9012824942.p.clickup-attachments.com/t9012824942/58a6fd1e-40fa-4448-8489-b853ea0f224d/20210825%20-%20Match%20accuracy%20estimates.xlsx)

# Change wording of error message regarding: 10m distinct ID and retro date combinations for the FI projects

# ClickUp Migrated Ticket
[https://app.clickup.com/t/8699ttgf3](https://app.clickup.com/t/8699ttgf3)

# 📝 Requirements
## → Context/Why
The current wording is confusing and doesn't help users know what to do next to proceed with their financial inclusion / predictive modelling projects
* * *
## → High Level Flow
🔗 Link to high-level Figjam flow here
N/A
* * *
## → High-Level Requirements
Update error message wording
This dataset exceeds the maximum records being built (10m). Please get in touch with Omnisient support to run this for you separately.

Current Error Message
![](https://t9012824942.p.clickup-attachments.com/t9012824942/782cc7b4-4f46-4388-afee-dca7ac9fcffa/image.png)
## → Technical Requirements
_Please find the Tech Spec Slack canvas template_ [_here_](https://omnisientworkspace.slack.com/docs/T018NR32PGV/F08ADMPKHJ4) _and choose "Use Template"_

🔗 Link to Slack canvas here
N/A
* * *
## → Acceptance Criteria

| ✅ Criteria | QA Comment / Verification | QA Ticket (If Applicable) |
| ---| ---| --- |
| New wording is displayed when there is an excess of 10m distinct id and date combinations in FI / DG Retail Modelling project setup | ✅ / ❌ |  |
| Omnisient support receives an email instructing them of the issue for Financial Inclusion | ✅ / ❌ |  |
| Omnisient support receives an email instructing them of the issue for Dollar General Retail Modelling | ✅ / ❌ |  |

* * *
# ⚠️ Dependencies
_These are listed as dependencies at the top of this card as well._
N/A
* * *
# 💭 Open Questions
N/A
* * *
# 🎨 High-Fidelity Designs
🔗 Link to high-fidelity Figma designs [here](https://www.figma.com/design/4ETD6s90wVlC0Jw4PVz5Uo/FI-error-message-for-high-distinct-id-and-retro-dates?node-id=1-2054&t=CjGL7NRlfjQ2u2fS-1)
## Error message
![](https://t9012824942.p.clickup-attachments.com/t9012824942/f6ab13d6-312c-4871-92ec-39fec8600dc5/image.png)

## Email for Financial Inclusion to [support@omnisient.com](mailto:support@omnisient.com)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/b5db1f7f-9266-42e4-8615-0987a455c876/image.png)
## Email for Dollar General Predictive Modelling to [support@omnisient.com](mailto:support@omnisient.com)
![](https://t9012824942.p.clickup-attachments.com/t9012824942/e5b9ac7b-2f13-4e3f-aa38-6b0eeb2fd9ff/image.png)
# 🔮 Future Work
_If applicable - this section contains new work items that have been spun out from this ticket_
N/A
* * *
# 🔎 Research/Analysis
N/A
* * *
# 💡 CX
N/A
* * *
# 🛠️ Engineering Task Breakdown

...

* * *

# Comments
![](https://t9012824942.p.clickup-attachments.com/t9012824942/c1a3ec9b-de57-4a0a-86a2-1d6f5ceb4818/image.png)