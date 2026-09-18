> **Status:** Published — live

# Datasets

The **Datasets** section is where you view and manage all datasets
available to your organization.

This includes:

-   Datasets you've uploaded and registered\
-   Datasets shared with you by connection partners\
-   Tools to prepare, transform, and generate derived datasets for use
    in projects

------------------------------------------------------------------------

# My Datasets

The **My Datasets** tab displays all datasets uploaded by your
organization.

Datasets are grouped based on their processing, registration, and
sharing status.

------------------------------------------------------------------------

## Unregistered

This table acts as the dataset lobby.

Newly uploaded datasets appear here while they are being processed. At
this stage, you can:

-   Review potential issues (e.g., high error rates)
-   Identify possible PII leaks
-   Ensure the dataset is in optimal condition before registration

### Mapping

Datasets can also be mapped at this stage.

Mapping ensures: - The dataset is fit for its intended purpose - All
required columns and information are available - The dataset can be used
in future projects

------------------------------------------------------------------------

## Available

These datasets:

-   Have completed processing and registration\
-   Are ready to be used in projects\
-   Can be shared with connection partners

If you attempt to delete a dataset that is currently shared:

-   A confirmation modal will appear
-   This prevents accidental removal of datasets being used by partners

### Mapping

Available datasets can also be mapped to confirm:

-   Required columns exist
-   All necessary information is included for project use

------------------------------------------------------------------------

## Dataset Share

This table lists registered datasets that have been shared with
connection partners.

From here, you can:

-   Manage partner access\
-   Revoke access at any time

------------------------------------------------------------------------

# Dataset Types

Dataset types categorize datasets based on purpose and data structure.\
They guide platform processing and downstream usage.

------------------------------------------------------------------------

## Custom / Derived

-   Created on the platform (e.g., using SQLPad)
-   Registered for use in projects

------------------------------------------------------------------------

## Customer

-   Contains customer information\
-   Includes PII that must be anonymized

------------------------------------------------------------------------

## Customer (Activation)

-   Contains single hash values\
-   Intended for upload to activation channels (e.g., Meta, TikTok)

------------------------------------------------------------------------

## Dimension

-   Descriptive dataset\
-   Does not contain PII\
-   Does not require anonymization

------------------------------------------------------------------------

## Transaction

-   Transactional data\
-   Each row represents a single transaction at a point in time\
-   Does not contain PII\
-   Does not require anonymization\
-   ✅ Mapping supported

------------------------------------------------------------------------

## Other

-   Mixed dataset\
-   May include PII\
-   May require anonymization

------------------------------------------------------------------------

# Partner Datasets

This tab displays datasets shared with your organization by connection
partners.

From here, you can:

-   Review incoming dataset shares\
-   Accept or decline access

------------------------------------------------------------------------

## Partner Dataset Statuses

### New

-   Requires action\
-   You can Accept or Decline

### Accepted

-   Dataset share has been accepted\
-   Available when creating new projects\
-   Appears in partner referencing dropdowns

### Declined

-   Dataset share has been declined\
-   Not available for use in projects

### Locked

-   Dataset share has expired\
-   Any projects using this dataset will also become locked

------------------------------------------------------------------------

# Own Data Preparation

This tab provides tools to explore, transform, and prepare datasets for
project use.

You can:

-   Create new datasets\
-   Save derived datasets\
-   Register them as **Custom / Derived** under My Datasets

------------------------------------------------------------------------

# Supported Tools

## SQLPad

Use SQLPad to:

-   Write and run SQL queries\
-   Explore and prepare data\
-   Generate exports (in supported projects)\
-   Extract query results through the platform's export approval process

Related Guides: - 👉 How to Create a SQLPad Export\
- 👉 Approving SQLPad Exports Created On Your Data\
- 👉 How to Assess SQLPad Exports with Confidence

------------------------------------------------------------------------

## Jupyter Notebook

-   Write code\
-   Create data visualizations\
-   Enhance data preparation workflows

Related Guide: - 👉 Available Packages & Libraries for Jupyter Notebook

------------------------------------------------------------------------

## Dataset Mapper

-   Map dataset columns to required fields\
-   Ensure dataset readiness for project use
