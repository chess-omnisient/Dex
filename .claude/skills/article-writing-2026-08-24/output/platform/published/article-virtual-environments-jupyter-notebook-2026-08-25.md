---
title: Virtual Environments in Jupyter Notebook
status: draft
author: chess@omnisient.com
created: 2026-08-25
collection: Analytics and Modelling
article_shape: standalone
---

A virtual environment (venv) is a persistent, isolated Python environment within a Jupyter project, separate from the project's shared Python installation. Packages installed inside a venv persist across sessions in the project's storage, which avoids the session-only installs and version drift that come with installing packages directly into the shared environment.

A venv is useful whenever a specific analysis or model needs a particular library version — for example, testing a newer release of a package without changing the version every other notebook in the project relies on. It also makes an analysis reproducible: recreating the same venv gives the same package versions, rather than whatever happens to be installed in the shared environment at the time.

Jupyter Notebook creates and activates project-specific venvs through the `omni_helper` extension.

## What You'll Need

- Jupyter Notebook open within a project.

👉 See [Jupyter Notebook](https://help.omnisient.com/en/articles/8057225-jupyter-notebook) for how to open Jupyter Notebook within a project.

## Creating and Activating a Venv

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
<b>Note:</b> Initial creation takes 15 to 30 minutes. The venv itself persists in the project's storage, but a new session still needs to run both cells above to reactivate it — reactivating an existing venv takes seconds.
</div>

<div style="background-color:#e3e7fa80; border:1px solid #334bfa33; padding: 8px;">
💡 Use the same venv name across every notebook in the project, so each one activates the same persisted venv and the packages already installed in it.
</div>

## Installing Packages Inside a Venv

Once a venv is active, install a package the same way as outside one:

```
!pip install <package_name>
```

Packages install from Omnisient's vetted package library. A package installed inside an active venv persists across sessions in the project's storage — install it once, and it's available every time that venv is reactivated, without installing it again.

👉 See [Using Jupyter Notebook for Packages/Libraries Management](https://help.omnisient.com/en/articles/9866691-using-jupyter-notebook-for-packages-libraries-management) for how package installs behave outside a venv.

<div style="background-color:#feedaf80; border:1px solid #fbc91633; padding: 8px;">
⚠️ If a package isn't part of the vetted library, it isn't available to install this way. Contact <a href="mailto:support@omnisient.com">support@omnisient.com</a> to request it be added or updated.
</div>
