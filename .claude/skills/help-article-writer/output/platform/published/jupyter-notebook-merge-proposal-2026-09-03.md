---
title: "Proposed merge: article-virtual-environments-and-omnihub content into Jupyter Notebook (Intercom id 8057225)"
status: proposal
author: chess@omnisient.com
created: 2026-09-03
target_article: Jupyter Notebook (https://help.omnisient.com/en/articles/8057225-jupyter-notebook)
target_article_id: "8057225"
---

<!-- Not applied to the live article yet. This replaces two blocks of the live "Jupyter Notebook"
article body with the fuller content from article-virtual-environments-and-omnihub-2026-09-03.md.
Everything else in the live article (Getting Started, Workspace size options, File browser,
general Libraries import/`!pip list`, Company Notebook Library, Sharing a notebook) is untouched -
only Block 1 and Block 2 below are new HTML to swap in via update_article. -->

## Block 1 — replaces the entire "Working with your data in Jupyter" H1 (`h_working_with_data`)

Covers: viewing available tables (`h_step1_tables`, unchanged scope), querying data
(`h_step2_load`, unchanged scope but the buggy stray `%omni_hub` line in the live code sample is
removed), two new subsections not currently in the live article (workspace sizing for a query,
optimizing memory for large tables), and writing data back (`h_cd9b7dd847`, unchanged scope).
Reuses the 3 existing screenshots at their equivalent points, now with alt text added.

```html
<h1 id="h_working_with_data">Working with Your Data in Jupyter</h1>
<p class="no-margin"><b>OmniHub</b> reads data from the data warehouse into a Jupyter notebook, either from your own Data Preparation area or a project's shared tables. Queries are written as SQL strings and submitted through the <code>omni_hub</code> magic command; the result is a <code>ResultSet</code> object you convert to a pandas DataFrame with <code>.DataFrame()</code>.</p>

<h2 id="h_step1_tables">Viewing Available Tables</h2>
<p class="no-margin">Before querying, load the extension and list the tables available to you:</p>
<ol>
<li><p class="no-margin">Load the extension:</p><p class="no-margin"></p><p class="no-margin"><code>%load_ext omni_hub</code></p></li>
<li><p class="no-margin">Return every table in a project:</p><p class="no-margin"></p><p class="no-margin"><code>%omni_hub {"select * from information_schema.tables where table_schema = '&lt;PROJECT_NAME&gt;'"}</code></p><p class="no-margin"></p><p class="no-margin">Replace <code>&lt;PROJECT_NAME&gt;</code> with the working project name, for example <code>OMNISIENT_PRJ_00114</code>. This returns the names, schemas, and types of tables available.</p></li>
</ol>

<h2 id="h_step2_load">Querying Data</h2>
<p class="no-margin">Define the query as a SQL string, submit it through <code>omni_hub</code>, then convert the result to a DataFrame:</p>
<pre><code>%load_ext omni_hub<br>data = %omni_hub {'select top 100 * from [project_code].[table_name]'}<br>df = data.DataFrame()</code></pre>
<ul>
<li><p class="no-margin">Replace <code>[project_code]</code> with the project code, for example <code>ClientName_Prj_00001</code>. For Own Data Preparation, use <code>ClientName_a</code>.</p></li>
<li><p class="no-margin">Replace <code>[table_name]</code> with the table to query.</p></li>
<li><p class="no-margin"><code>top 100</code> limits the extract to the first 100 rows. Remove it to pull the full table.</p></li>
</ul>
<p class="no-margin">Queries use Microsoft SQL Server syntax, and can join a table against a partner's table within the same query – join on <code>DW_ID_KEY</code> or <code>BestMatchID</code>.</p>
<div class="intercom-container"><img src="https://downloads.intercomcdn.com/i/o/ns0zsqth/2514985726/b0eef32cc78c81c44aaabd33ddd3/Frame+2.png?expires=1788544800&amp;signature=aebe6cccec291979e7a749518444560f5955f71714f2d078a25a82fecdc1958b&amp;req=diUmEsB2mIZdX%2FMW3nq%2BgVEQxUZqRPRQXKizTri1F0uVwxmm9AFeRNefKDQO%0AAlAMVMHiX3qtQ9xltDpibQQ9ZdA%3D%0A" width="3075" height="615" style="height: auto;" alt="Example SQL query joining a project table with a partner table on DW_ID_KEY, run through the omni_hub magic command."></div>
<p class="no-margin">To identify a username for support queries or table-creation permission requests:</p>
<p class="no-margin"><code>%omni_hub {'select current_user'}</code></p>
<div class="intercom-container"><img src="https://downloads.intercomcdn.com/i/o/ns0zsqth/2514982884/54ceb9e6b84c6601ec8389d26cb7/image+77.png?expires=1788544800&amp;signature=a4ab472b130768f83dbf05cfc89c176b64276ca52397a4099b41bd5be3273f0d&amp;req=diUmEsB2n4lXXfMW3nq%2BgV6rPDx%2FwZ01jqxZ8kpAL7FHhMH20S%2F0SiR7XJ8l%0A3ATbdv2Ki2LVC62ToOGyWbEiWXk%3D%0A" width="2085" height="672" style="height: auto;" alt="Jupyter notebook output showing the current_user query result as a long alphanumeric string ending in the project name."></div>
<p class="no-margin">The username is the long alphanumeric string ending in the project name.</p>
<div class="intercom-interblocks-callout" style="background-color: #e3e7fa80; border-color: #334bfa33;"><p class="no-margin">💡 <b>Tips for managing memory:</b></p><ul>
<li><p class="no-margin">For large datasets, do as much data preparation, cleaning, joining, and sampling in SQL as possible before loading into the notebook – Python compute may run out of memory on very large datasets.</p></li>
<li><p class="no-margin">Load only the data needed – a filtered query over a full table pull.</p></li>
<li><p class="no-margin">Clear unused variables with Python's <code>del</code>, or restart the kernel to free memory between tasks.</p></li>
</ul></div>

<h2 id="h_query_workspace_size">Choosing a Workspace Size for a Query</h2>
<p class="no-margin">Query performance and processing time depend on the shape of the table being pulled, and the notebook's workspace size needs to match it.</p>
<ul>
<li><p class="no-margin">A wide table (many columns, e.g. 500 columns across 3 million rows) is compute- and memory-intensive to process column-by-column, and typically needs the Extra Large workspace size.</p></li>
<li><p class="no-margin">A long table (few columns, e.g. 10 columns across 50 million rows) processes differently – the Large workspace size is typically sufficient.</p></li>
</ul>
<p class="no-margin">👉 See <a href="https://help.omnisient.com/en/articles/8057225-jupyter-notebook#h_workspace_size" target="_blank" class="intercom-content-link">Workspace size options</a> above for the full CPU/memory breakdown of each workspace size.</p>
<div class="intercom-interblocks-callout" style="background-color: #feedaf80; border-color: #fbc91633;"><p class="no-margin">⚠️ Pulling more data than a query actually needs increases the risk of the query timing out, independent of workspace size. Scope a query to the columns and rows actually needed rather than sizing up to compensate.</p></div>

<h2 id="h_query_memory_optimization">Optimizing Memory for Large Tables</h2>
<p class="no-margin"><code>omni_hub</code> returns a <code>ResultSet</code> object. Converting it directly to a DataFrame holds the data twice in memory – once as the <code>ResultSet</code>, once as the DataFrame – which can cause out-of-memory errors on large tables.</p>
<p class="no-margin">Export the <code>ResultSet</code> to CSV, delete it, then load the CSV into pandas instead. This holds only one copy at a time:</p>
<ol>
<li><p class="no-margin">Run the query with <code>omni_hub</code>.</p></li>
<li><p class="no-margin">Save the result to CSV with <code>.csv("path")</code>.</p></li>
<li><p class="no-margin">Delete the original object with <code>del</code>.</p></li>
<li><p class="no-margin">Load the CSV into pandas with <code>pd.read_csv</code>.</p></li>
</ol>
<pre><code># 1) Run query via omni_hub<br>sql_query = "select top 10 * from [project_code].[table_name]"<br>rs = %omni_hub {sql_query}<br><br># 2) Save to CSV<br>rs.csv("my_table.csv")<br><br># 3) Delete the ResultSet to free memory<br>del rs<br><br># 4) Read the CSV into pandas<br>import pandas as pd<br>df = pd.read_csv("my_table.csv", low_memory=False)</code></pre>

<h2 id="h_cd9b7dd847">Writing a DataFrame Back to a Project</h2>
<p class="no-margin">To write the results of an analysis back to the project tables, use <code>omni_lab</code>.</p>
<ol>
<li><p class="no-margin">Import the package:</p><p class="no-margin"></p><p class="no-margin"><code>import omni_lab</code></p></li>
<li><p class="no-margin">Copy the DataFrame back to the project:</p><p class="no-margin"></p><p class="no-margin"><code>omni_lab.copy_to_project_tables(df, "PROJECT_CODE", "table_name")</code></p><p class="no-margin"></p><p class="no-margin">Replace <code>PROJECT_CODE</code> with your project code, for example <code>QACOMPANYA_PRJ_00023</code>, and <code>table_name</code> with a name of your choosing. Table names can't contain spaces.</p></li>
</ol>
<p class="no-margin">The write runs asynchronously.</p>
<div class="intercom-container"><img src="https://downloads.intercomcdn.com/i/o/ns0zsqth/2514986158/bdb12e1b384bc04197457ae7ed0d/image+80.png?expires=1788544800&amp;signature=03bbb0682e0f2510dab4385725ccb71cd572e7345ef4686fbbe5d3f7f75f3bfa&amp;req=diUmEsB2m4BaUfMW3nq%2Bgd9OAq4wZWlLl7sfcdBb%2BjlaTOf7OEeznKmTLCff%0ALDtZrqb9sNPaOTuUUSfWqtes1FQ%3D%0A" width="2085" height="777" style="height: auto;" alt="Jupyter notebook output confirming a DataFrame write request was submitted via omni_lab."></div>
```

## Block 2 — replaces the "Virtual environments" H2 (`h_venv`) under the live "Libraries" H1

Everything above this in "Libraries" (the `import pandas`/`import numpy` example, `!pip list`, the
link to Available Packages & Libraries) is untouched. Only `h_venv` itself is replaced — it grows
two H3 subsections instead of staying flat, now that it covers both creating a venv and installing
packages inside one.

```html
<h2 id="h_venv">Virtual Environments</h2>
<p class="no-margin">Jupyter Notebook creates and activates project-specific venvs through the <code>omni_helper</code> extension. Use a venv when a specific analysis or model needs a particular library version, or when reproducibility matters.</p>

<h3 id="h_venv_create">Creating and Activating a Venv</h3>
<p class="no-margin">Run these two cells at the top of the notebook, every session:</p>
<ol>
<li><p class="no-margin">Load the <code>omni_helper</code> extension:</p><p class="no-margin"></p><p class="no-margin"><code>%load_ext omni_helper</code></p></li>
<li><p class="no-margin">Create and activate the venv:</p><p class="no-margin"></p><p class="no-margin"><code>%omni_helper venv-activate &lt;env_name&gt;</code></p><p class="no-margin"></p><p class="no-margin">Replace <code>&lt;env_name&gt;</code> with any name you choose. The first time, this creates the venv and activates it; every time after, it just activates it.</p></li>
</ol>
<div class="intercom-interblocks-callout" style="background-color: #e8e8e880; border-color: #73737633;"><p class="no-margin"><b>Note:</b> Initial creation takes up to 30 minutes. The venv itself persists in the project's storage, but a new session still needs to run both cells above to reactivate it – reactivating an existing venv takes seconds.</p></div>
<div class="intercom-interblocks-callout" style="background-color: #e3e7fa80; border-color: #334bfa33;"><p class="no-margin">💡 Use the same venv name across every notebook in the project, so each one activates the same persisted venv and the packages already installed in it.</p></div>

<h3 id="h_venv_packages">Installing Packages Inside a Venv</h3>
<p class="no-margin">Once a venv is active, install a package the same way as outside one:</p>
<p class="no-margin"><code>!pip install &lt;package_name&gt;</code></p>
<p class="no-margin">Packages install from Omnisient's vetted package library. A package installed inside an active venv persists across sessions in the project's storage – install it once, and it's available every time that venv is reactivated, without installing it again.</p>
<p class="no-margin">👉 See <a href="https://help.omnisient.com/en/articles/9866691-using-jupyter-notebook-for-packages-libraries-management" target="_blank" class="intercom-content-link">Using Jupyter Notebook for Packages/Libraries Management</a> for how package installs behave outside a venv.</p>
<div class="intercom-interblocks-callout" style="background-color: #feedaf80; border-color: #fbc91633;"><p class="no-margin">⚠️ If a package isn't part of the vetted library, it isn't available to install this way. Contact <a href="mailto:support@omnisient.com">support@omnisient.com</a> to request it be added or updated.</p></div>
```

## Still open

- [ ] No screenshot exists yet for the table-listing output (Block 1) or the venv-activate
      first-run output (Block 2) — both stay flagged as placement recommendations for someone to
      capture and add later; not a blocker for this merge.
- [ ] Anchor ids `h_query_workspace_size` and `h_query_memory_optimization` are my own slugs for
      the two genuinely new subsections — Intercom's editor may regenerate its own ids on save via
      the API; if so, any external deep link to these exact ids would need re-checking after publish.
- [ ] Confirm before I call `update_article` on live id `8057225` — this replaces real, published,
      customer-facing content immediately on save.
</content>
