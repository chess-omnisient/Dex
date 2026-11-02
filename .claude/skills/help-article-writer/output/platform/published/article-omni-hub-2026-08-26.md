---
title: OmniHub
status: draft
author: chess@omnisient.com
created: 2026-08-26
collection: Analytics and Modelling
article_shape: child
parent_article: Jupyter Notebook (https://help.omnisient.com/en/articles/8057225-jupyter-notebook)
---

<!-- Revision 2026-08-27: merged in grounding from the live parent article (Jupyter Notebook,
id 8057225) via the Intercom API - the public URL 401s (help-center access-gated). Per the
single-sourcing guardrail, this content overlaps with the parent's "Working with your data in
Jupyter" section; the author chose to keep both for now rather than trim the parent in this pass,
so that section is flagged as a follow-up, not resolved here. Also fixed a correctness bug in
"Writing a DataFrame Back to a Project" - step 2's code block was a copy-paste of the query
template instead of the actual omni_lab call; corrected against the parent article. Status reset
to draft pending the open items below. -->

**OmniHub** reads data from the data warehouse into a Jupyter notebook, either from your own Data Preparation area or a project's shared tables. Queries are written as SQL strings and submitted through the `omni_hub` magic command; the result is a `ResultSet` object you convert to a pandas DataFrame with `.DataFrame()`.

## What You'll Need
- Jupyter Notebook open within a project.

<div style="background-color:#e3e7fa80; border:1px solid #334bfa33; padding: 8px;">
💡 See the OmniHub Resource Help Notebook<sup>1</sup> for a runnable, end-to-end example of the workflow below.
</div>

<!-- 1: the parent article links this from a signed, expiring Intercom CDN URL
(downloads.intercomcdn.com/.../Omni+Resource+Help.ipynb?expires=...). Don't publish that URL as-is
- it will break once it expires. Re-upload the notebook as this article's own attachment (or
confirm a stable link) before this goes to status: ready. -->

## Viewing Available Tables
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

## Querying Data

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

## Choosing a Workspace Size for a Query

Query performance and processing time depend on the shape of the table being pulled, and the notebook's workspace size needs to match it.

- A wide table (many columns, e.g. 500 columns across 3 million rows) is compute- and memory-intensive to process column-by-column, and typically needs the Extra Large workspace size.
- A long table (few columns, e.g. 10 columns across 50 million rows) processes differently – the Large workspace size is typically sufficient.

👉 See [Jupyter Notebook: Workspace size options](https://help.omnisient.com/en/articles/8057225-jupyter-notebook#h_workspace_size) for the full CPU/memory breakdown of each workspace size.

<div style="background-color:#feedaf80; border:1px solid #fbc91633; padding: 8px;">
⚠️ Pulling more data than a query actually needs increases the risk of the query timing out, independent of workspace size. Scope a query to the columns and rows actually needed rather than sizing up to compensate.
</div>

## Optimizing Memory for Large Tables

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

## Writing a DataFrame Back to a Project

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
