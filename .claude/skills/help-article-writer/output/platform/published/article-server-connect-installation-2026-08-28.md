---
title: Server Connect: Installation
status: draft
author: chess@omnisient.com
created: 2026-08-28
source_article_id: 10102684
source_article_url: https://help.omnisient.com/en/articles/10102684-server-connect-installation
intercom_draft_id: 16729440
intercom_draft_note: pushed as a new draft article (not an update to the live 10102684) so the currently-published version stays online while this is reviewed
collection: Uploading Data
article_shape: standalone (child of the Uploading Data Collection; no hub article - parent_id 19711513 is the Collection itself)
---

<!-- Revision 2026-08-28: pulled the live article via the claude.ai Intercom connector
(mcp__claude_ai_Intercom__get_article) after the local intercom-mcp server 401'd on every call -
that server has since been deleted from .mcp.json as redundant/broken. Diffed against the live
HTML, not the archived Server_Connect_Guide/config.json manual (compiled 2026-08-04, since
superseded by the live content - e.g. region-specific download endpoints and the Firewall Access
Required / API Key Generation / Minimum System Requirements articles don't exist in that manual at
all).

Changes made, each flagged inline where it appears:
1. CORRECTNESS BUG: the live "Linux setup" section promises "the example below is a bash script
   that sets up Server Connect on Ubuntu 22.04" but no script follows - it jumps straight to the
   Configurator-only snippet. Reconstructed the missing install script from the archived manual's
   equivalent, adapted for region-specific downloads (placeholder, not hardcoded to one region) and
   trimmed to stop at the same point the Windows section stops (install + unzip + directory prep;
   not into running the server app, which "Next steps" already defers elsewhere). Flagged inline -
   NEEDS SME VERIFICATION before this goes to status: ready, per the confirmation gate below.
2. DUPLICATION/INCONSISTENCY: removed "Windows Server Specification and Requirements" and "Disk
   Space" subsections from Windows Setup - they duplicated Minimum System Requirements (id
   8684027), which Prerequisites already links to. Confirmed with the author: link out
   consistently rather than re-inlining full specs.
3. STRUCTURE: "Installation Steps Summary" mixed true sequential actions with explanatory asides
   ("The Configurator is a self-hosted web server...", the run-directly-vs-copy-to-server branch)
   as separate numbered items - violates one-action-per-step and numbered-steps-only-when-order-
   matters. Split the asides into a tip callout after the relevant step.
4. STRUCTURE: converted "Download endpoints by region" from a bulleted list to a table (3
   variants of the same kind of thing).
5. TONE: removed bold-wrapped heading text (headings carry their own weight per house style) and
   retitled "Prerequisites" to "What You'll Need" for consistency with the rest of the article set.
-->

Server Connect is a console application you run on your own infrastructure to anonymize and upload data to Omnisient on a schedule. This article covers installing and configuring the application on a Linux or Windows server.

## What You'll Need

- **System requirements** — see [Minimum System Requirements](https://help.omnisient.com/en/articles/8684027-minimum-system-requirements) for supported operating systems, RAM, and disk space.
- **.NET Core 8.0 SDK** — install it from [dotnet.microsoft.com](https://dotnet.microsoft.com/en-us/download/dotnet/8.0) before you begin.
- **Firewall access** — the required Omnisient domains and IP ranges must be allowlisted. See [Firewall Access Required](https://help.omnisient.com/en/articles/7019108-firewall-access-required).
- **API Key** — an API Key (ID and Secret) generated in the platform, used to authenticate the application. See [API Key Generation](https://help.omnisient.com/en/articles/8865523-api-key-generation).

## Installation Steps Summary

1. Provision the server you want to run the application on.
2. Install the .NET Core 8.0 SDK.
3. Download the application file from your region's download endpoint (see below).
4. Unzip the downloaded file to a directory on the server.
5. Set up an API Key in the Web App (see [API Key Generation](https://help.omnisient.com/en/articles/8865523-api-key-generation)).
6. Run the Configurator application to set up your configuration.
7. Make sure your data is available as per the configuration.
8. Run the application with the configuration name.
9. Optional: schedule the application to run automatically at set intervals.

<div style="background-color:#e3e7fa80; border:1px solid #334bfa33; padding: 8px;">
💡 The Configurator in step 6 is a self-hosted web server for setting up your server configuration. Run it directly on the server — on Linux without a user interface, open port 5000 to access the Configurator screen — or run it on your own machine and copy the resulting configuration to the server.
</div>

> 🖼️ **Image suggestion (Orient):** the Configurator's landing screen at `localhost:5000`, showing the initial configuration setup view — without this image, the reader has no reference for what a successful Configurator launch looks like before they start filling in fields.
> - **Type:** Screenshot
> - **Alt text:** "Server Connect Configurator landing screen showing the initial configuration setup options."
> - **Filename:** `Server-Connect-Configurator-Landing-Screen.png`
>
> Capture from a sandboxed/demo install with no real configuration data in frame.

## Download Endpoints by Region

| Region | Download Endpoint |
|---|---|
| South Africa | `https://api.omnisient.com/downloads/enterprisev2` |
| UAE | `https://api-uae.omnisient.com/downloads/enterprisev2` |
| US | `https://api-eus.omnisient.com/downloads/enterprisev2` |

## Linux Setup

The following bash script sets up Server Connect on Ubuntu 22.04:

<!-- FLAGGED - reconstructed from the archived Server_Connect_Guide manual (compiled 2026-08-04),
adapted for region-specific downloads and trimmed to match the Windows section's stopping point.
This is NOT confirmed against the current live application - verify before publishing. -->

```bash
# Update package lists and install prerequisites
sudo apt-get update
sudo apt-get install -y apt-transport-https wget

# Add the Microsoft package repository and install the .NET Core 8.0 SDK
wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y dotnet-sdk-8.0

# Move to the directory where you want to install the application
cd /opt

# Download the application from your region's download endpoint (see table above)
sudo wget <your-region-download-endpoint> -O enterprisev2.zip

# Install unzip and extract the application
sudo apt-get install -y unzip
sudo unzip enterprisev2.zip -d enterprisev2

# Create a directory to save iURNs (only needed if you choose to save them)
sudo mkdir savedata

# Create a directory for source files (only needed for CSV/Parquet uploads)
sudo mkdir uploadedfiles

# Give the current user permission to write to the installation directory
sudo chown -R $USER:$USER /opt/enterprisev2
```

### Run the Configurator on Linux

```bash
# Change to the directory where the Configurator is located
cd /opt/enterprisev2/Config

# Run the Configurator
sudo dotnet Intersect.Enterprise.Config.dll
```

The Configurator starts a local web server. Access it at `http://localhost:5000` or `https://localhost:5001`.

<div style="background-color:#e8e8e880; border:1px solid #c6c9c0; padding: 8px;">
Note: make sure the port is open. If you can't use that port, set up an instance on Nginx or Apache to proxy the site over port 80 or 443.
</div>

## Windows Setup

1. Download the application zip file from your region's download endpoint (see above).
2. Unzip the file to the location where you want to run the application.
3. Run the Configurator: open the **Config** folder and run `Intersect.Enterprise.Config.exe`. This starts a local web server.
4. Access the Configurator in your browser at `https://localhost:5001` or `http://localhost:5000`.

## Next Steps

Once installed, set up your data source configuration and authenticate the application. You can then run the application with your configuration name and, optionally, schedule it to run automatically at set intervals.
