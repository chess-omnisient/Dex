---
title: Virtual Environments and OmniHub
status: draft
author: chess@omnisient.com
created: 2026-09-03
collection: Analytics and Modelling
article_shape: child
parent_article: Jupyter Notebook (https://help.omnisient.com/en/articles/8057225-jupyter-notebook)
---

<!-- Merge note 2026-09-03: combined article-virtual-environments-jupyter-notebook-2026-08-25.md
and article-omni-hub-2026-08-26.md at the author's request. Both were independent children of the
Jupyter Notebook hub; content itself is unchanged from the two source drafts (headings renumbered
to sit under two major sections instead of two separate articles). Once this combined draft is
confirmed, article-virtual-environments-jupyter-notebook-2026-08-25.md and
article-omni-hub-2026-08-26.md are superseded - author chose to leave them in place for now
(2026-09-03) rather than delete.

Open items:
1. (from the OmniHub draft, still unresolved) The parent article links a runnable example notebook
   from a signed, expiring Intercom CDN URL (downloads.intercomcdn.com/.../Omni+Resource+Help.ipynb
   ?expires=...). Don't publish that URL as-is - it will break once it expires. Re-upload the
   notebook as this article's own attachment (or confirm a stable link) before this goes to
   status: ready.
2. (2026-09-03, single-sourcing check against the live parent) Fetched the live parent article
   (Intercom id 8057225) via the Intercom API - the public URL still 401s (help-center
   access-gated). Confirmed this child article's OmniHub and venv-creation content is a strict
   superset of the parent's "Working with your data in Jupyter" section and the "Virtual
   environments" subsection under the parent's "Libraries" heading (h_working_with_data, h_venv) -
   no facts in the parent are missing here. Per the single-sourcing guardrail, the parent's two
   sections should be trimmed to a short lead-in + 👉 pointer to this article rather than continuing
   to duplicate the steps in full - proposed trim drafted separately, not yet applied to the live
   article (editing a published, customer-facing article needs the author's sign-off first).
3. (2026-09-03, resolved) Venv creation time discrepancy - author confirmed "up to 30 minutes"
   (matching the live parent) is accurate; this article's text updated accordingly.
4. (2026-09-03, unrelated, FYI only) The live parent's own "Load data into Jupyter" code sample
   has a stray bare `%omni_hub` line before the real query line - looks like a copy-paste artifact,
   not something to replicate here. Worth a separate bug report against the live article; not a
   grounding source to follow. -->

Jupyter Notebook supports two independent tools for working with data: virtual environments
(venvs), which keep installed packages isolated and persistent across sessions, and OmniHub, which
queries the data warehouse and loads the result into a notebook as a DataFrame. A venv is useful
whenever a specific analysis or model needs a particular library version, or when reproducibility
matters — recreating the same venv gives the same package versions every time. OmniHub is useful
whenever a notebook needs to read from a project's shared tables or your own Data Preparation area,
using SQL to select the exact data needed.

## What You'll Need

- Jupyter Notebook open within a project.

👉 See [Jupyter Notebook](https://help.omnisient.com/en/articles/8057225-jupyter-notebook) for how to open Jupyter Notebook within a project.

## Working with Virtual Environments

Jupyter Notebook creates and activates project-specific venvs through the `omni_helper` extension.

### Creating and Activating a Venv

Run these two cells at the top of the notebook, every session:

1. Load the `omni_helper` extension:

   ```
   %load_ext omni_helper
   ```

2. Create and activate the venv:

   ```
   %omni_helper venv-activate <env_name>
   ```

   Replace `<env_name>` with any name you choose. The first time, this creates the venv and activates it; every time after, it just activates it.

> 🖼️ **Image suggestion (Confirm):** the notebook cell output immediately after running `%omni_helper venv-activate` for the first time, showing the environment-creation progress — without this image, the reader has no way to confirm that a long-running cell is working as expected rather than stuck.
> - **Type:** Screenshot
> - **Alt text:** "Jupyter notebook output after running the venv-activate command for the first time, showing the environment being created."
> - **Filename:** `Omni-Helper-Venv-Activate-First-Run-Output.png`
>
> Capture from a sandboxed project with a placeholder environment name — never a real project or customer data.

<div style="background-color:#e8e8e880; border:1px solid #73737633; padding: 8px;">
<b>Note:</b> Initial creation takes up to 30 minutes. The venv itself persists in the project's storage, but a new session still needs to run both cells above to reactivate it — reactivating an existing venv takes seconds.
</div>

<div style="background-color:#e3e7fa80; border:1px solid #334bfa33; padding: 8px;">
💡 Use the same venv name across every notebook in the project, so each one activates the same persisted venv and the packages already installed in it.
</div>

### Installing Packages Inside a Venv

Once a venv is active, install a package the same way as outside one:

```
!pip install <package_name>
```

Packages install from Omnisient's vetted package library. A package installed inside an active venv persists across sessions in the project's storage — install it once, and it's available every time that venv is reactivated, without installing it again.

👉 See [Using Jupyter Notebook for Packages/Libraries Management](https://help.omnisient.com/en/articles/9866691-using-jupyter-notebook-for-packages-libraries-management) for how package installs behave outside a venv.

<div style="background-color:#feedaf80; border:1px solid #fbc91633; padding: 8px;">
⚠️ If a package isn't part of the vetted library, it isn't available to install this way. Contact <a href="mailto:support@omnisient.com">support@omnisient.com</a> to request it be added or updated.
</div>

## Querying Data with OmniHub

**OmniHub** reads data from the data warehouse into a Jupyter notebook, either from your own Data Preparation area or a project's shared tables. Queries are written as SQL strings and submitted through the `omni_hub` magic command; the result is a `ResultSet` object you convert to a pandas DataFrame with `.DataFrame()`.

<div style="background-color:#e3e7fa80; border:1px solid #334bfa33; padding: 8px;">
💡 See the OmniHub Resource Help Notebook<sup>1</sup> for a runnable, end-to-end example of the workflow below.
</div>

<!-- 1: the parent article links this from a signed, expiring Intercom CDN URL
(downloads.intercomcdn.com/.../Omni+Resource+Help.ipynb?expires=...). Don't publish that URL as-is
- it will break once it expires. Re-upload the notebook as this article's own attachment (or
confirm a stable link) before this goes to status: ready. -->

### Viewing Available Tables

Before querying, load the extension and list the tables available to you:

1. Load the extension:

   ```
   %load_ext omni_hub
   ```

2. Return every table in a project:

   ```
   %omni_hub {"select * from information_schema.tables where table_schema = '<PROJECT_NAME>'"}
   ```

   Replace `<PROJECT_NAME>` with the working project name, for example `OMNISIENT_PRJ_00114`. This returns the names, schemas, and types of tables available.

> 🖼️ **Image suggestion (Confirm):** the notebook cell output immediately after running the table-listing query, showing the returned names/schemas/types table – without this image, the reader has no reference for what a correct result looks like versus an empty or malformed one.
> - **Type:** Screenshot
> - **Alt text:** "Jupyter notebook output listing table names, schemas, and types after querying information_schema.tables."
> - **Filename:** `Omni-Hub-Table-List-Output.png`
>
> Capture from a sandboxed project with placeholder table names – never real project or customer data.

### Querying Data

Define the query as a SQL string, submit it through `omni_hub`, then convert the result to a DataFrame:

```
%load_ext omni_hub
data = %omni_hub {'select top 100 * from [project_code].[table_name]'}
df = data.DataFrame()
```

- Replace `[project_code]` with the project code, for example `ClientName_Prj_00001`. For Own Data Preparation, use `ClientName_a`.
- Replace `[table_name]` with the table to query.
- `top 100` limits the extract to the first 100 rows. Remove it to pull the full table.

Queries use Microsoft SQL Server syntax, and can join a table against a partner's table within the same query – join on `DW_ID_KEY` or `BestMatchID`.

To identify a username for support queries or table-creation permission requests:

```
%omni_hub {'select current_user'}
```

The username is the long alphanumeric string ending in the project name.

> 🖼️ **Image suggestion (Confirm):** the notebook cell output immediately after running `select current_user`, showing the returned username string – without this image, the reader has to infer the expected format from the description alone rather than recognizing it against a real example.
> - **Type:** Screenshot
> - **Alt text:** "Jupyter notebook output showing the current_user query result as a long alphanumeric string ending in the project name."
> - **Filename:** `Omni-Hub-Current-User-Output.png`
>
> Capture from a sandboxed project with a placeholder username – never a real one. (Considered a screenshot for the join-on-`DW_ID_KEY`/`BestMatchID` example too, but that's code, not a UI state – a code block covers it, per the "code belongs in a code block, never a screenshot" rule.)

<div style="background-color:#e3e7fa80; border:1px solid #334bfa33; padding: 8px;">
💡 <b>Tips for managing memory:</b>
<ul>
<li>For large datasets, do as much data preparation, cleaning, joining, and sampling in SQL as possible before loading into the notebook – Python compute may run out of memory on very large datasets.</li>
<li>Load only the data needed – a filtered query over a full table pull.</li>
<li>Clear unused variables with Python's <code>del</code>, or restart the kernel to free memory between tasks.</li>
</ul>
</div>

### Choosing a Workspace Size for a Query

Query performance and processing time depend on the shape of the table being pulled, and the notebook's workspace size needs to match it.

- A wide table (many columns, e.g. 500 columns across 3 million rows) is compute- and memory-intensive to process column-by-column, and typically needs the Extra Large workspace size.
- A long table (few columns, e.g. 10 columns across 50 million rows) processes differently – the Large workspace size is typically sufficient.

👉 See [Jupyter Notebook: Workspace size options](https://help.omnisient.com/en/articles/8057225-jupyter-notebook#h_workspace_size) for the full CPU/memory breakdown of each workspace size.

<div style="background-color:#feedaf80; border:1px solid #fbc91633; padding: 8px;">
⚠️ Pulling more data than a query actually needs increases the risk of the query timing out, independent of workspace size. Scope a query to the columns and rows actually needed rather than sizing up to compensate.
</div>

### Optimizing Memory for Large Tables

`omni_hub` returns a `ResultSet` object. Converting it directly to a DataFrame holds the data twice in memory – once as the `ResultSet`, once as the DataFrame – which can cause out-of-memory errors on large tables.

Export the `ResultSet` to CSV, delete it, then load the CSV into pandas instead. This holds only one copy at a time:

1. Run the query with `omni_hub`.
2. Save the result to CSV with `.csv("path")`.
3. Delete the original object with `del`.
4. Load the CSV into pandas with `pd.read_csv`.

```
# 1) Run query via omni_hub
sql_query = "select top 10 * from [project_code].[table_name]"
rs = %omni_hub {sql_query}

# 2) Save to CSV
rs.csv("my_table.csv")

# 3) Delete the ResultSet to free memory
del rs

# 4) Read the CSV into pandas
import pandas as pd
df = pd.read_csv("my_table.csv", low_memory=False)
```

### Writing a DataFrame Back to a Project

To write the results of an analysis back to the project tables, use `omni_lab`.

1. Import the package:

   ```
   import omni_lab
   ```

2. Copy the DataFrame back to the project:

   ```
   omni_lab.copy_to_project_tables(df, "PROJECT_CODE", "table_name")
   ```

   Replace `PROJECT_CODE` with your project code, for example `QACOMPANYA_PRJ_00023`, and `table_name` with a name of your choosing. Table names can't contain spaces.

The write runs asynchronously.

> 🖼️ **Image suggestion (Confirm):** the notebook cell output immediately after running `copy_to_project_tables()`, showing the write request was submitted successfully – without this image, the reader has no way to tell a successful async submission from a silent failure.
> - **Type:** Screenshot
> - **Alt text:** "Jupyter notebook output confirming a DataFrame write request was submitted via omni_lab."
> - **Filename:** `Omni-Lab-Copy-To-Project-Tables-Output.png`
>
> Capture from a sandboxed project with placeholder project/table names – never real project or customer data.
</content>
