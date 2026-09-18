# Omnisient Platform – Sprint 8 Release Summary

**Period:** 3 August – 30 August 2026 | **Prepared for:** Shoprite

---

## Shoprite Data Feed
- **Segments mart build automation:** We've automated the build process for Shoprite's segments data mart, making segment updates faster and more reliable.
- **Financial Inclusion project template moves to new data pipeline:** The Financial Inclusion project template now runs on our new barcode-level data pipeline instead of the previous weekly sales data pipeline.
- **Weekly features pipeline migrating to barcode-level data:** The weekly features pipeline feeding Rainmaker, FNB Batch, and Basketscore is moving onto our new barcode-level data pipeline. The previous pipeline continues to run in parallel as a fallback during the transition.

## Audience Activation
- **Send FMCG audiences straight to Rainmaker:** FMCG brands can now build audience selections that combine their own customer data, Shoprite's customer base, and third-party demographic data, then send the resulting audience directly to Shoprite Rainmaker for campaign activation. Only Shoprite can access the audience once it's sent; the brand can't download it directly.

## Platform Enhancements
- **See every reason a project is locked, in one place:** The locked project screen now shows every issue currently blocking your project at once (expired subscriptions, expired or deactivated dataset shares), instead of one at a time. A single "Contact support" link opens a pre-filled request listing everything that needs resolving.
- **Help right where re-identification risk reduction applies:** A help icon now appears in the project creation flow, on the Project Datasets widget, and on the Power BI report wherever re-identification risk reduction has been applied to your data, linking straight to an explainer article so you can see why data might be suppressed without needing to raise a support request.
- **Analytics Studio beta now live for a pilot group of Shoprite users:** Analytics Studio, our standalone desktop app for running SQL and Jupyter Notebook sessions outside the browser, is now in beta with a small group of Shoprite users. This sprint's work smoothed out the beta experience: sessions now log you in automatically instead of asking you to re-enter credentials, and we fixed a bug where the connection would time out if the app was minimized for a while.

## Platform Stability & Reliability
- **Project expiry emails no longer go to deleted users:** Fixed an issue where users marked as deleted in the system could still receive project expiry notification emails.
- **Dataset update dates now refresh correctly:** Fixed an issue where uploading more files to an existing data collection didn't update its "last updated" date, which made it hard to find recently updated data collections.

---
