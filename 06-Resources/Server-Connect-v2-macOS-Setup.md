# Omnisient Server Connect v2 — macOS Setup Guide

Tested with **Server Connect 2.0.0.408** and **.NET 10** on an **Apple Silicon (M-series) Mac**.

## Why the Mac setup needs extra steps

Server Connect is a .NET app, so it runs on macOS through the `dotnet` command instead of the Windows `.exe` files. The build doesn't include SQLite's native library for macOS, though, and the official SQLite package for .NET only provides one for **Intel** Macs. So on Apple Silicon:

- The **config tool** runs normally, with the standard .NET.
- The **server** runs with the **Intel (x64) version of .NET through Rosetta**, using an Intel SQLite library that you add yourself.

## What to install

| Package | Why it's needed | Where to get it |
|---|---|---|
| Homebrew (optional) | Easiest way to install .NET | https://brew.sh |
| .NET 10 SDK (Arm64) | Runs the config tool | `brew install --cask dotnet-sdk`, or the macOS **Arm64** installer from https://dotnet.microsoft.com/download/dotnet/10.0 |
| Rosetta 2 | Runs Intel apps on Apple Silicon | `softwareupdate --install-rosetta --agree-to-license` |
| .NET 10 SDK (x64) | Runs the server under Rosetta | macOS **x64** installer from https://dotnet.microsoft.com/download/dotnet/10.0. It installs alongside the Arm64 version, in `/usr/local/share/dotnet/x64` |
| SQLite native library 1.0.119 (osx-x64) | Required by the server | NuGet package `Stub.System.Data.SQLite.Core.NetStandard` (download commands in step 5) |
| Server Connect zip | The application | Your region's download endpoint, e.g. `Intersect.Enterprise.Server.2.0.0.408.zip` |

## Key locations

| What | Path |
|---|---|
| Install folder | `~/enterprisev2` |
| Config tool (always start it from here) | `~/enterprisev2/Config` |
| Saved configurations | `~/enterprisev2/Configs` |
| Source CSV files | `~/enterprisev2/uploadedfiles` |
| Rejected files and their error logs | `~/enterprisev2/uploadedfiles/Failed` |
| Saved iURNs | `~/enterprisev2/savedata` |
| Logs | `~/enterprisev2/Logs` |
| Config tool in the browser | http://localhost:5050 |

In the config tool, use full paths, which start with `/Users/<your-username>/`. Run `echo $HOME` to see yours.

---

## Step 1: Install .NET 10 (Arm64)

```bash
brew install --cask dotnet-sdk
dotnet --list-runtimes
```

Check that `Microsoft.NETCore.App 10.x` and `Microsoft.AspNetCore.App 10.x` are listed.

## Step 2: Install Rosetta and .NET 10 (x64)

```bash
softwareupdate --install-rosetta --agree-to-license
```

Download the **macOS x64** .NET 10 SDK installer from https://dotnet.microsoft.com/download/dotnet/10.0 and run it. Then check that it installed:

```bash
/usr/local/share/dotnet/x64/dotnet --list-runtimes
```

## Step 3: Extract Server Connect

```bash
mkdir -p ~/enterprisev2
unzip -q ~/Downloads/Intersect.Enterprise.Server.2.0.0.408.zip -d ~/enterprisev2
ls ~/enterprisev2
```

You should see the `.dll` files and a `Config` folder. If you only see a single folder, move its contents up into `~/enterprisev2`.

```bash
cd ~/enterprisev2
mkdir -p savedata uploadedfiles
```

## Step 4: Remove the macOS download block

```bash
xattr -dr com.apple.quarantine ~/enterprisev2
```

## Step 5: Add the Intel SQLite library

First confirm the SQLite version in the build. It should print `1.0.119.0`:

```bash
strings ~/enterprisev2/System.Data.SQLite.dll | grep -E "^1\.0\.[0-9]{3}" | sort -u
```

If it prints a different version, use that number, without the final `.0`, in the download address below.

```bash
cd ~/Downloads
curl -L -o sqlite-stub.zip https://www.nuget.org/api/v2/package/Stub.System.Data.SQLite.Core.NetStandard/1.0.119
ls -lh sqlite-stub.zip
```

The file should be several MB. A file of about 100 bytes is an error page, which usually means the version number is wrong.

```bash
unzip -o -q sqlite-stub.zip -d sqlite-stub
find sqlite-stub -path "*osx-x64*" -name "SQLite.Interop.dll"
mkdir -p ~/enterprisev2/runtimes/osx-x64/native
cp sqlite-stub/runtimes/osx-x64/native/SQLite.Interop.dll ~/enterprisev2/runtimes/osx-x64/native/
xattr -dr com.apple.quarantine ~/enterprisev2/runtimes
```

If `find` prints a different path, use that path in the `cp` command.

## Step 6: Start the config tool (Terminal window 1)

The config tool must be started **from the `Config` folder** so it reads its own settings. Use port **5050**, because macOS AirPlay Receiver already uses port 5000.

```bash
cd ~/enterprisev2/Config
dotnet ../Intersect.Enterprise.Config.dll --urls http://localhost:5050
```

Leave this window running and don't type anything else into it.

## Step 7: Create a configuration in the browser

Type **http://localhost:5050** into the address bar, log in, and select the company. Create a new configuration with these settings:

- **Data source:** CSV
- **File path:** `/Users/<your-username>/enterprisev2/uploadedfiles`
- **Delimiter:** the character your CSV uses, such as `;` or `,`. It must be set.
- **Save path:** `/Users/<your-username>/enterprisev2/savedata`
- **Schema:** note its exact field names and their order
- **Dataset name:** any available name

Save it. A folder with the configuration's name appears in `~/enterprisev2/Configs`. To check what was saved:

```bash
cat ~/enterprisev2/Configs/<configuration-name>/customsettings.json
```

## Step 8: Prepare the data

- Put your CSV file(s) in `~/enterprisev2/uploadedfiles`.
- **Every CSV in that folder is processed and uploaded**, so include only the files you intend to upload.
- The header line must match the schema's field names **exactly**: the same names, the same order, and no stray spaces.
- Use the same delimiter as in the configuration.
- Every row must have a value for every column.

## Step 9: Run the server (Terminal window 2)

Open a new Terminal window with **Cmd+N**. Run the server from the install folder using the **x64** `dotnet`:

```bash
cd ~/enterprisev2
ls Configs
/usr/local/share/dotnet/x64/dotnet Intersect.Enterprise.Server.v2.dll <configuration-name>
```

The argument is the **configuration name**, not the dataset name.

---

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| A command seems to do nothing | It was typed into a window where an app is already running. Open a new window (**Cmd+N**) and run it there. |
| Config tool shows a 500 error at `HomeController.cs` line 23 | It was started from the wrong folder. Restart it from `~/enterprisev2/Config`. |
| `localhost` shows "HTTP ERROR 403" | That's AirPlay answering on port 5000. Use http://localhost:5050, or turn off AirPlay Receiver in System Settings → General → AirDrop & Handoff. |
| `Could not find a part of the path ...` | The file path in the configuration doesn't exist. Use the full path to `uploadedfiles`. |
| `Value cannot be null ... Convert.ToChar` | A single-character setting, such as the delimiter, is empty. Set it in the config tool and save. |
| `File headers doesn't match schema` | Fix the CSV header line to match the schema exactly. |
| `Access to the path .../Failed/<file>.csv is denied` | A leftover **folder** with the CSV's name is in `Failed`. Delete it with `rm -rf ~/enterprisev2/uploadedfiles/Failed/*`. |
| `Unable to load shared library 'SQLite.Interop.dll'` | Step 5 wasn't completed, or the server was started with the Arm64 `dotnet` instead of `/usr/local/share/dotnet/x64/dotnet`. |
| `free: command not found` | A harmless Linux-only memory check. Ignore it. |

To see error details:

```bash
ls -t ~/enterprisev2/Logs | head -3
cat ~/enterprisev2/uploadedfiles/Failed/*-errors.log
```

## Tips

- **To stop an app, press Control+C**, not Cmd+C.
- Keep one Terminal window per running app, plus one for commands.
- Clear `uploadedfiles/Failed` before re-running a file that failed.
- The config tool's `Config/appsettings.json` may point to **UAT** (`api-uat-v2.omnisient.com`). Check the URLs before using production.
- **Intel Macs:** skip Rosetta and the x64 .NET install, and run the server with the normal `dotnet` command. Step 5 is still required.
