# How to share a notebook with another project user

Use `omni_helper` to transfer Jupyter notebook files to other active participants within the same project.

## Before you start

- **Permissions required:** Active participant in the project
- **Prerequisites:** Jupyter Notebook open within your project

## Steps

### 1. Load the omni_helper extension

Run the following in a Jupyter cell:

```python
%load_ext omni_helper
```

`omni_helper` is available in all Jupyter environments — no installation required.



### 2. Get the recipient's user address

Each project member has a unique user address per project. Run:

```
omni_helper project-members
```

This returns a table with each member's user address and email. Copy the **User Address** of the person you want to send the file to.

> **Note:** User addresses are project-specific. The same user will have a different address in each project they belong to.



### 3. Send the file

```
omni_helper send-files --paths [filename.ipynb] --receiver [user_address]
```

**Example:**
```
omni_helper send-files --paths test_file.ipynb --receiver 35e618dbe7bbda5acbb0166c25d0463789e99fd9
```

> **Note:** Filenames cannot contain spaces. Rename the file before transferring if needed.

### 4. Check transfer status

The transfer runs asynchronously. When the command is submitted, a `REQUEST_ID` is returned. To confirm completion:

```
omni_helper transfer-history
```



Match the output against your `REQUEST_ID`.

## What to expect

- **Sender:** A confirmation message with a `REQUEST_ID` is returned immediately. The transfer itself runs in the background.
- **Recipient:** The file appears in a shared folder within their Jupyter workspace, inside a dated subfolder. There is no automatic notification — the recipient needs to check the shared folder manually.

## Common issues

| Issue | Likely cause | Fix |
|-------|--------------|-----|
| Recipient not listed in `project-members` | User is not an active participant in this project | Confirm the recipient has been added to the project |
| Transfer not completing | Filename contains spaces | Rename the file to remove spaces, then retry |
| Wrong user address used | Address copied from a different project | Re-run `omni_helper project-members` in the current project |

## Related

- [Integrated Jupyter Notebook Solution](https://help.omnisient.com/en/articles/8057225-integrated-jupyter-notebook-solution)