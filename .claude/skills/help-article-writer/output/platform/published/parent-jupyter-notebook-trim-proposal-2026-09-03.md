---
title: "Proposed trim: Jupyter Notebook (parent article, Intercom id 8057225)"
status: proposal
author: chess@omnisient.com
created: 2026-09-03
target_article: Jupyter Notebook (https://help.omnisient.com/en/articles/8057225-jupyter-notebook)
target_article_id: "8057225"
---

<!-- Not applied to the live article. This is a proposal to review before anything is pushed via
the Intercom API - editing a published, customer-facing article needs sign-off first. Two blocks
below are now single-sourced in article-virtual-environments-and-omnihub-2026-09-03.md; per the
single-sourcing guardrail (article-information-architecture.md) the parent should orient + link
rather than duplicate the full steps. Placeholder URL below needs the real published URL for the
child article once it ships - it's currently still status: draft with no live URL. -->

## Block 1 — replaces the "Working with your data in Jupyter" H1 section

**Current (live):** the full "Working with your data in Jupyter" section — `h_working_with_data`,
`h_step1_tables` (View the tables available in your project), `h_step2_load` (Load data into
Jupyter), `h_cd9b7dd847` (Writing data back to the project). Duplicates this article's "Querying
Data with OmniHub" section in full, including the memory-management tips callout and both
screenshots.

**Proposed replacement:**

> ## Working with Your Data in Jupyter
>
> **OmniHub** reads data from the data warehouse into a Jupyter notebook, either from your own
> Data Preparation area or a project's shared tables. Queries are written as SQL strings and
> submitted through the `omni_hub` magic command; the result is a `ResultSet` object you convert
> to a pandas DataFrame with `.DataFrame()`.
>
> 👉 See [Virtual Environments and OmniHub](PLACEHOLDER — insert live URL once child article is published) for the full workflow: viewing available tables, querying data, choosing a workspace size, optimizing memory for large tables, and writing a DataFrame back to a project.

## Block 2 — replaces the "Virtual environments" H2 subsection (under "Libraries")

**Current (live):** `h_venv` — "If you need project-specific dependencies without affecting the
shared Jupyter environment, use the `omni_helper` venv feature," plus the two-step
create/activate instructions and the creation-time note. Duplicates this article's "Working with
Virtual Environments" section, minus the package-installation content (which the parent doesn't
cover at all).

**Proposed replacement:**

> ### Virtual Environments
>
> If you need project-specific dependencies without affecting the shared Jupyter environment, use
> the `omni_helper` venv feature.
>
> 👉 See [Virtual Environments and OmniHub](PLACEHOLDER — insert live URL once child article is published) for how to create, activate, and reuse a venv, and how to install packages inside one.

## Before this goes anywhere

- [x] Resolve the venv creation-time discrepancy — author confirmed "up to 30 minutes" (matching
      the live parent); the child article's text is updated.
- [ ] Publish the child article first so Block 1 and Block 2 have a real URL to link to.
- [ ] Confirm you want this pushed to the live Intercom article (id 8057225) via the Intercom API
      — that's a published, customer-facing edit, so it needs your go-ahead, not a silent apply.
- [ ] Separately, flag the live parent's own "Load data into Jupyter" code sample — it has a
      stray bare `%omni_hub` line before the real query line — as a bug report; unrelated to this
      trim.
</content>
