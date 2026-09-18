#!/usr/bin/env python3
"""Build a formatted PDF of the Omnisient Help Center articles."""

import re
from fpdf import FPDF

def sanitize(text):
    """Replace Unicode characters that latin-1 can't encode."""
    replacements = {
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2014": " - ", "\u2013": " - ", "\u2022": "-", "\u2026": "...",
        "\u2032": "'", "\u2033": '"', "\u00a0": " ", "\u200b": "",
        "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2015": " - ",
        "\u2212": "-", "\u2192": "->", "\u2190": "<-", "\u2713": "[x]",
        "\u2714": "[x]", "\u2717": "[ ]", "\u2718": "[ ]", "\u2605": "*",
        "\u2606": "*", "\u00b7": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Fallback: replace any remaining non-latin1 chars
    return text.encode("latin-1", errors="replace").decode("latin-1")


class HelpCenterPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(130, 130, 130)
            self.cell(0, 8, "Omnisient Help Center", align="L")
            self.ln(4)
            self.set_draw_color(200, 200, 200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(130, 130, 130)
            self.cell(0, 10, f"Page {self.page_no() - 1}", align="C")

    def chapter_header(self, collection_name):
        """Add a collection/chapter header."""
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(0, 90, 156)
        self.cell(0, 14, sanitize(collection_name), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 90, 156)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def article_title(self, title):
        """Add an article title."""
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, sanitize(title), new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def section_heading(self, text):
        """Add a section heading (##)."""
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(60, 60, 60)
        self.cell(0, 8, sanitize(text), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def sub_heading(self, text):
        """Add a sub-heading (###)."""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 7, sanitize(text), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        """Add body text with basic formatting."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, sanitize(text))
        self.ln(2)

    def bullet_item(self, text, indent=10):
        """Add a bullet point."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.set_x(self.l_margin + indent)
        w = self.w - self.l_margin - self.r_margin - indent
        self.multi_cell(w, 5.5, "-  " + sanitize(text))
        self.ln(1)

    def code_block(self, text):
        """Add a code block with background."""
        self.set_fill_color(245, 245, 245)
        self.set_font("Courier", "", 9)
        self.set_text_color(40, 40, 40)
        x = self.get_x()
        self.set_x(x + 5)
        self.multi_cell(180, 5, sanitize(text), fill=True)
        self.ln(3)

    def table_row(self, cells, header=False):
        """Add a table row."""
        if header:
            self.set_font("Helvetica", "B", 9)
            self.set_fill_color(230, 240, 250)
        else:
            self.set_font("Helvetica", "", 9)
            self.set_fill_color(255, 255, 255)
        self.set_text_color(50, 50, 50)

        n = len(cells)
        if n == 0:
            return
        col_width = 190 / n
        # Limit column width for readability
        if n == 2:
            widths = [60, 130]
        elif n == 3:
            widths = [45, 100, 45]
        else:
            widths = [col_width] * n

        # Calculate row height based on content
        max_lines = 1
        for i, cell in enumerate(cells):
            w = widths[i] if i < len(widths) else col_width
            lines = max(1, len(cell) * self.get_string_width("a") / (w - 2) + 1)
            max_lines = max(max_lines, int(lines))

        row_h = max(6, min(max_lines * 5, 30))
        self.set_draw_color(200, 200, 200)

        for i, cell in enumerate(cells):
            w = widths[i] if i < len(widths) else col_width
            cell_clean = sanitize(cell)
            x = self.get_x()
            y = self.get_y()
            self.rect(x, y, w, row_h)
            if header:
                self.set_fill_color(230, 240, 250)
                self.rect(x, y, w, row_h, "F")
            self.set_xy(x + 1, y + 1)
            self.multi_cell(w - 2, 4.5, cell_clean[:200])  # Truncate very long cells
            self.set_xy(x + w, y)

        self.ln(row_h)

    def render_markdown(self, md_text):
        """Parse simple markdown and render it."""
        lines = md_text.split("\n")
        in_code = False
        code_buf = []
        in_table = False
        table_header_done = False

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                if in_code:
                    code_buf.append("")
                elif in_table:
                    in_table = False
                    table_header_done = False
                    self.ln(2)
                continue

            # Code block toggle
            if stripped.startswith("```"):
                if in_code:
                    self.code_block("\n".join(code_buf))
                    code_buf = []
                    in_code = False
                else:
                    in_code = True
                continue

            if in_code:
                code_buf.append(stripped)
                continue

            # Table row
            if "|" in stripped and stripped.startswith("|"):
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                # Skip separator rows
                if all(re.match(r"^[-:]+$", c) for c in cells if c):
                    continue
                if not in_table:
                    in_table = True
                    table_header_done = False
                    self.table_row(cells, header=True)
                    table_header_done = True
                else:
                    self.table_row(cells, header=False)
                continue

            in_table = False

            # Headings
            if stripped.startswith("### "):
                self.sub_heading(re.sub(r"\*\*|__", "", stripped[4:]))
            elif stripped.startswith("## "):
                self.section_heading(re.sub(r"\*\*|__", "", stripped[3:]))
            elif stripped.startswith("# "):
                # Treat top-level headings as article subtitles
                self.section_heading(re.sub(r"\*\*|__", "", stripped[2:]))
            elif stripped.startswith("- ") or stripped.startswith("* "):
                text = re.sub(r"\*\*(.+?)\*\*", r"\1", stripped[2:])
                text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
                self.bullet_item(text)
            elif stripped.startswith("---"):
                self.set_draw_color(220, 220, 220)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(4)
            else:
                # Clean inline markdown
                text = re.sub(r"\*\*(.+?)\*\*", r"\1", stripped)
                text = re.sub(r"\*(.+?)\*", r"\1", text)
                text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
                text = re.sub(r"!\[.*?\]", "", text)  # Remove image refs
                if text.strip():
                    self.body_text(text)


def build_pdf():
    # Define collections and articles
    collections = [
        {
            "name": "General Information",
            "articles": [
                {
                    "title": "Firewall Access Required",
                    "content": """If your firewall blocks the app installation or usage, contact your IT administrator to whitelist these URLs:

### IP Ranges
https://www.cloudflare.com/ips/

### South Africa (app.omnisient.com)
- api.omnisient.com
- app.omnisient.com
- auth.omnisient.com
- static.omnisient.com
- intersect.blob.core.windows.net

### UAE (uae.omnisient.com)
- api-uae.omnisient.com
- uae.omnisient.com
- auth-uae.omnisient.com
- staticuae.omnisient.com
- stblobomniprduan.blob.core.windows.net

### US East (us-east.omnisient.com)
- api-eus.omnisient.com
- us-east.omnisient.com
- auth-eus.omnisient.com
- static-eus.omnisient.com
- stblobomniprdeus.blob.core.windows.net

### United Kingdom (uk.omnisient.com)
- api-uk.omnisient.com
- uk.omnisient.com
- auth-uk.omnisient.com
- static-uk.omnisient.com
- stblobomniprduks.blob.core.windows.net

### General Domains
- http://desktopv2.omnisient.com/
- columnprediction.blob.core.windows.net"""
                },
                {
                    "title": "Deprecation of the Contracting Feature",
                    "content": """## Overview
Omnisient has officially deprecated its Contracting Feature from the platform.

## Rationale
The decision stems from a strategic shift toward using in-house legal counsel for all contractual matters, enabling streamlined operations and improved efficiency.

## Impact on Users
Users can no longer manage or process contracts directly within the Omnisient platform.

## Transition Plan
The company committed to notifying all users of this change through direct communication and platform announcements.

## Moving Forward
For contract-related needs, users should contact their account managers directly. This approach aims to provide more personalized and legally robust support, ensuring that all contractual processes are handled with the highest level of professionalism and care.

## Support
Users requiring further assistance should reach out to the support team at support@omnisient.com or visit https://app.omnisient.com/contact."""
                },
            ],
        },
        {
            "name": "Omnisient Web Application",
            "articles": [
                {
                    "title": "Copyright",
                    "content": """Unless otherwise noted, the contents of this platform, including all text, graphics, icons, hyperlinks, designs, video and other visual material and the selection, arrangement and layout thereof are copyright of Omnisient (RF) (Pty) Ltd and all rights are reserved.

Reproduction, downloading or copying of any material from this site, unless specifically indicated to be authorised, in any form whatsoever is prohibited and will constitute a copyright infringement. Such unauthorised copying may result in civil and criminal law prosecution.

The Poppins font used on this platform is licensed under the SIL Open Font License, Version 1.1, with copyright held by Intercom, Inc."""
                },
            ],
        },
        {
            "name": "New Features",
            "articles": [
                {
                    "title": "Control How Your Audience Exports Are Deduplicated",
                    "content": """## What's Changed

Previously, audience exports always returned a single record per customer, even when selected fields existed at more granular levels (such as multiple affluence segments per customer). This meant some valid records could be excluded during export.

Users can now choose how their audience is deduplicated when creating an export.

## Deduplication Options

When exporting customer base data as CSV, you'll encounter a deduplication choice:

### Distinct by Selected Columns
- Produces one record per selected column combination
- Provides structured, column-level uniqueness
- Maintains behavior consistent with existing exports

### Return All Records
- Returns all records across the selected fields
- No implicit deduplication by customer ID
- Ideal for enrichments and extractions requiring full granularity

Example: If a customer has three affluence segments included in your export, the file will contain three records for that customer.

## What Stays the Same
- Exports default to one record per customer if no deduplication option is selected
- Record counts in previews always match the exported file

## Built-In Transparency and Safeguards
- Selected deduplication mode is visible, saved, and auditable
- Results are deterministic and repeatable
- Warnings appear if "Return all records" produces very large exports
- Data is never silently dropped or truncated
- Exported columns are visible for review

## Why This Matters

Different use cases require different detail levels. This update enables exporting one row per customer when needed or retaining full field-level detail for deeper analysis and enrichment, while maintaining Omnisient's privacy-first design approach."""
                },
            ],
        },
        {
            "name": "FAQs",
            "articles": [
                {
                    "title": "How are you different from other platforms?",
                    "content": """## No one ever takes possession of your data.

Unlike other platforms, Omnisient doesn't require parties to upload raw consumer data before anonymization. Other platforms require clients to upload their raw consumer data to their platform before anonymizing the data. This traditional approach exposes clients to data breach risks and allows service providers to gain intellectual property from aggregated client data.

Omnisient's approach differs significantly: their desktop anonymization and upload app enables clients to anonymize their datasets before uploading, meaning only behavioral and demographic information -- not personal data -- gets shared on the platform.

## You get access to embedded AI & ML tools to build data products

Omnisient provides integrated artificial intelligence and machine learning capabilities within a collaborative environment. This allows clients to analyze the data and build predictive models and data products within the secure, neutral environment without ever needing to download each other's data for analysis."""
                },
                {
                    "title": "How is my IP protected?",
                    "content": """Omnisient has implemented four key data protection measures for their collaboration platform:

### 1. Local Anonymization
Your data is anonymized locally -- not on the platform. The personally identifiable information never leaves your environment. Data is processed through a desktop application that replaces identifiable information with unique hash strings called Crypto-IDs, which enable record matching across partner datasets.

### 2. Irreversible Anonymization
The anonymization of your dataset cannot be reverse engineered to re-identify consumers by Omnisient or any 3rd party. Additional hashing occurs during upload to the secure environment. Even Omnisient cannot re-identify consumer records because local matching tokens differ from cloud-based tokens.

### 3. User Control
Your uploaded dataset is never out of your control. You retain authority over access permissions and determine which parties can view specific data at all times.

### 4. No Data Transfer
Data never exchanges hands in the environment. Authorized parties may analyze data but cannot download or remove it from the platform."""
                },
                {
                    "title": "Can another business identify my clients?",
                    "content": """Your dataset undergoes multiple instances of hashing and SALTing (adding more unique characters to the original string of hashed characters generated for additional anonymization) before it is accessible to your authorized collaboration partners.

Even Omnisient has no way of re-identifying your consumers, meaning the anonymization process prevents re-identification by all parties, including the platform operator itself."""
                },
                {
                    "title": "Can a competitor see my data?",
                    "content": """No, they cannot. Only parties you've authorized can view your anonymized data in the secure collaboration environment.

Omnisient's platform restricts visibility to authorized parties only and maintains anonymization within its collaborative framework."""
                },
                {
                    "title": "Can a business take an extract and run models against my data?",
                    "content": """No. The Omnisient platform allows authorized businesses to run models against your data within the platform, eliminating the transfer of your data asset to another party. Partners can evaluate your data's value without obtaining ownership of it."""
                },
                {
                    "title": "How much is my data worth?",
                    "content": """Data valuation depends on solving known market problems. The key principle is: If your data can solve a known problem better than existing data in the market, there is often a simple point of comparison to determine what your data is worth.

Data often has untapped potential beyond initial assumptions. By allowing data-hungry businesses to safely explore datasets, organizations can discover additional value and build credibility.

The final step involves assessing the problem's scope and setting competitive, reasonable pricing based on the value delivered."""
                },
                {
                    "title": "Where is my data uploaded to?",
                    "content": """Your anonymized data is uploaded into the secure collaboration environment which is hosted on the Microsoft Azure Cloud in the region of your choice.

Omnisient stores user information on Microsoft Azure Cloud infrastructure with regional selection options available. The data undergoes anonymization before upload to the collaborative environment."""
                },
                {
                    "title": "Is the Omnisient platform GDPR / CCPA / POPIA compliant?",
                    "content": """Omnisient's platform enables businesses to comply with global privacy regulations by eliminating personal information from the data collaboration process entirely. The platform uses matchable Crypto-Identities that cannot be reverse engineered so the customers' personal information cannot be re-identified.

Once parties determine data value and seek to transfer data between collaborators, consent considerations may apply. However, personal information is never exchanged with the other party in the collaboration process and thus eliminates breach risk."""
                },
                {
                    "title": "Am I at risk if there is a breach at one of my data partners?",
                    "content": """No, you are never at risk. Since you never transfer or provide personal information to either Omnisient or to a data partner, if the data partner experiences a breach in their environment, you are never at risk.

You never physically transfer personal information out of your environment. Your customers' personal information remains behind your firewall."""
                },
                {
                    "title": "Do I need consent from my customers to collaborate with other businesses on the Omnisient platform?",
                    "content": """You do not need your customers' consent to share anonymized data on the Omnisient platform, since personal information is never shared, and your consumers cannot be re-identified by a 3rd party.

Key points:
- Anonymized data sharing does not require customer consent
- Personal information is not disclosed
- Third parties cannot re-identify consumers through the platform"""
                },
                {
                    "title": "Using Virtual Environments (Venv) in Jupyter Notebooks",
                    "content": """## Overview

The Venv feature in Omnisient's Jupyter Notebook enables users to create and manage isolated Python environments directly inside your notebook. This approach allows project-specific library installations without affecting other notebooks or shared environments.

## Prerequisites
- Access to Jupyter Notebook within the Omnisient platform
- Permission to run notebooks in your project
- Basic familiarity with Jupyter cells and magic commands

## How It Works

The Venv feature requires only two notebook cells:

1. First cell: Loads the Omnisient helper extension
2. Second cell: Creates and activates your virtual environment

The same command works whether the environment is new or already exists.

## Setup Instructions

### Step 1: Load the Extension

In your first cell, run:

```
%load_ext omni_helper
```

This enables Omnisient-specific helper commands.

### Step 2: Activate the Virtual Environment

In your second cell, run:

```
%omni_helper venv-activate venv
```

You can replace "venv" with custom names like "analysis_env" or "project_a_env".

Example:

```
%omni_helper venv-activate analysis_env
```

## Behavior and Performance

Initial creation: The environment is created on first run, taking up to 30 minutes depending on setup and resources.

Subsequent activations: Activation is near-instant for existing environments.

## Best Practices
- Use clear, project-specific names for environments
- Place both commands at the notebook's top
- Reuse the same environment across notebooks in the same project when possible

## Troubleshooting
- Command doesn't run: Verify %load_ext omni_helper executes first
- Long initial wait: This is expected during first-time environment creation

For persistent issues, contact Omnisient Support via the Help Centre."""
                },
            ],
        },
        {
            "name": "Data Preparation",
            "articles": [
                {
                    "title": "How to Share a Notebook with Another Project User",
                    "content": """## Overview
Use omni_helper to transfer Jupyter notebook files to other active participants within the same project.

## Before You Start

Permissions required: Active participant in the project

Prerequisites: Jupyter Notebook open within your project

## Steps

### 1. Load the omni_helper Extension

Run the following in a Jupyter cell:

```
%load_ext omni_helper
```

Note: omni_helper is available in all Jupyter environments with no installation required.

### 2. Get the Recipient's User Address

Each project member has a unique user address per project. Run:

```
omni_helper project-members
```

This command returns a table displaying each member's user address and email. Copy the User Address of your intended recipient.

Important: User addresses are project-specific -- the same person will have different addresses across different projects.

### 3. Send the File

```
omni_helper send-files --paths [filename.ipynb] --receiver [user_address]
```

Example:

```
omni_helper send-files --paths test_file.ipynb --receiver 35e618dbe7bbda5acbb0166c25d0463789e99fd9
```

Note: Filenames cannot contain spaces. Rename your file before transferring if necessary.

### 4. Check Transfer Status

Transfers run asynchronously. When you submit the command, a REQUEST_ID is returned. To verify completion:

```
omni_helper transfer-history
```

Match the output against your REQUEST_ID.

## What to Expect

Sender: A confirmation message with a REQUEST_ID appears immediately. The actual transfer operates in the background.

Recipient: The file appears in a shared folder within their Jupyter workspace, organized in a dated subfolder. No automatic notification is sent -- the recipient must manually check the shared folder.

## Common Issues

| Issue | Likely Cause | Fix |
| Recipient not listed | User not active in project | Confirm recipient added to project |
| Transfer not completing | Filename contains spaces | Rename file to remove spaces |
| Wrong user address | Address from different project | Re-run project-members in current project |"""
                },
            ],
        },
        {
            "name": "Datasets",
            "articles": [
                {
                    "title": "Datasets",
                    "content": """## Overview

The Datasets section is where you view and manage all datasets available to your organization. This includes datasets you've uploaded and registered, datasets shared with you by connection partners, and tools that allow you to prepare, transform, and generate derived datasets for use in projects.

## My Datasets

The My Datasets tab displays all datasets uploaded by your organization. Datasets are grouped based on their current processing, registration, and sharing status.

### Dataset Status Categories

**Unregistered:** This table acts as the dataset lobby. Newly uploaded datasets appear here while they are being processed. You can review potential issues, such as high error rates or possible PII leaks, to ensure the dataset is in optimal condition before registration. At this stage, datasets can also be mapped. Mapping is a crucial step to ensure the dataset is fit for its intended purpose.

**Available:** These datasets have completed processing and registration and are ready to be used in projects. Available datasets can also be shared with connection partners. Deleting a dataset will trigger a confirmation modal if it is currently shared.

**Dataset Share:** This table lists registered datasets that have been shared with connection partners. You can manage or revoke partner access to a dataset at any time from here.

### Dataset Types

| Dataset Type | Description | Mapping Supported |
| Custom / Derived | Created on the platform using tools such as SQLPad | No |
| Customer | Contains customer information including PII that must be anonymized | No |
| Customer (Activation) | Contains single hash values for upload to activation channels | No |
| Dimension | Descriptive dataset information without PII | No |
| Transaction | Transactional data, each row represents a transaction | Yes |
| Other | Mixed information that may include PII | No |

## Partner Datasets

This tab shows datasets that have been shared with your organization by connection partners. From here, you can review incoming dataset shares and decide whether to accept or decline access.

### Partner Datasets Statuses

| Status | Description |
| New | Requires action. You can Accept or Decline the dataset share. |
| Accepted | Dataset can be used when creating a new project. |
| Declined | Dataset will not be available for use in projects. |
| Locked | Dataset share has expired. Projects using it become locked. |

## Own Data Preparation

This tab provides tools to explore, transform, and prepare your datasets for use in projects. You can also create and save new datasets, which will appear as Custom / Derived datasets under My Datasets.

### Supported Tools

| Tool | Description |
| SQLPad | Write and run SQL queries to explore and prepare data. |
| Jupyter Notebook | Create code and data visualizations for data preparation. |
| Dataset Mapper | Map dataset columns to required fields. |"""
                },
                {
                    "title": "Dataset Mapping",
                    "content": """## Overview

Dataset mapping is a crucial preparatory step for using datasets in downstream functionality like project creation. It creates transparency between your intended use of the dataset and Omnisient's structural expectations, including required and recommended columns.

## Access Locations

| Location | How to Access |
| My Datasets (Unregistered & Available) | Via dataset row context menu: "Map dataset" or "Edit mapping". Also from dataset detail view. |
| Own Data Preparation | Through the Dataset Mapper widget. Datasets with existing mappings display a mapper icon. |

Permission Note: Dataset mapping is enabled by default for Admin users. Non-admin users require explicit permission assignment.

## How It Works

The mapping process uses a two-step bottom sheet flow:

### Step 1: Select

Choose your dataset and assign its dataset type. The dropdown behavior varies:
- From My Datasets: Pre-populated with your selected dataset
- From Own Data Preparation: Displays all Unregistered and Available datasets with icons differentiating their states

Dataset types determine which fields are required versus recommended during mapping.

### Step 2: Map

After selection, the system automatically populates mapping fields organized into:
- Required fields: Must be mapped to save
- Additional fields: Strongly recommended but optional

## Data Type Icons Reference

| Icon | Type |
| Boolean | Boolean values |
| Datetime | Date and time values |
| Decimal | Decimal numbers |
| Number | Integer / Number values |
| String | Text strings |

Recommendation: While only required fields need mapping, Omnisient strongly encourages mapping additional fields to maximize dataset utility."""
                },
            ],
        },
        {
            "name": "Omnisient Help",
            "articles": [
                {
                    "title": "Need Help?",
                    "content": """Your first point of contact is a help bot located in the bottom right of your screen. Clicking it provides several options:

### Messaging Support
If you'd like to send a message and engage with the bot or someone in person, please click on messages.

### Knowledge Library
If you'd like to source the knowledge library simply click on help, and type in your query.

### News Updates
Want to know what's new at Omnisient? Click on News!

### Direct Contact
For direct email support, users can reach out via the support contact form.

## Support Channels
- Interactive chatbot (accessible via bottom-right widget)
- Direct messaging with support team members
- Self-service knowledge base search
- Product news and updates section
- Email support option

The help bot widget is the primary support entry point, with escalation options to human support available through the messaging feature."""
                },
            ],
        },
    ]

    pdf = HelpCenterPDF()

    # --- Title Page ---
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(0, 90, 156)
    pdf.cell(0, 16, "Omnisient", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 14, "Help Center", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_draw_color(0, 90, 156)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 10, "Complete Documentation", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, "Generated: 2026-03-23", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, "https://help.omnisient.com", align="C", new_x="LMARGIN", new_y="NEXT")

    # --- Table of Contents ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(0, 90, 156)
    pdf.cell(0, 14, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    article_num = 0
    for coll in collections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0, 90, 156)
        pdf.cell(0, 8, coll["name"], new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        for art in coll["articles"]:
            article_num += 1
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 6, f"    {article_num}. {art['title']}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # --- Content ---
    current_collection = None
    for coll in collections:
        for art in coll["articles"]:
            pdf.add_page()
            if coll["name"] != current_collection:
                pdf.chapter_header(coll["name"])
                current_collection = coll["name"]
            pdf.article_title(art["title"])
            pdf.render_markdown(art["content"])

    # Save
    output_path = "/Users/chess/dex/Omnisient_Help_Center.pdf"
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")
    print(f"Collections: {len(collections)}")
    print(f"Articles: {sum(len(c['articles']) for c in collections)}")


if __name__ == "__main__":
    build_pdf()
