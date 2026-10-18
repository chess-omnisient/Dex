---
status: draft (Intercom 17278304)
type: how-to
audience: technical
collection: Server Connect (19711513)
source: ".NET 10 Runtime Install Runbook (Windows & Linux Servers)"
drafted: 2026-10-01
---

# How to install the .NET 10 runtime for Server Connect


This guide covers adding the .NET 10 runtime to a Windows or Linux server that runs Server Connect, alongside the runtimes already installed. Do this before you upgrade to the Server Connect build that runs on .NET 10. Everything currently running on the server keeps working unchanged, so you can install the runtime well ahead of the upgrade itself.

💡 The Server Connect build that runs on .NET 10 is available from 11 October 2026. Installing the runtime now is a side-by-side change: it sits alongside your existing runtimes, your current Server Connect build keeps using the runtime it already uses, and no application code or configuration changes. It normally needs no reboot or downtime. On Windows servers running IIS, the Hosting Bundle restarts IIS during the install.

## Before you start

- **Permissions required:** root or sudo on Linux, local administrator on Windows.
- **Access:** VPN, plus SSH (Linux) or RDP (Windows).
- **Change approval:** an approved change for each target server, per your own change management process.
- **The package:** downloaded with its published SHA-512 checksum, or confirmed repository access from the server.
- **The service account:** the name of the account that runs Server Connect on each server. You need it to verify the install.
- **Order:** failover and non-production servers first, then production in its own change window.
- **Time:** roughly 15 to 30 minutes per server for the install, plus OS update and reboot time.

**In scope:** installing ASP.NET Core Runtime 10 on Linux and Windows servers, and proving it is visible to the account that runs Server Connect.

**Out of scope:** deploying the new Server Connect build, changing scripts or schedules, removing older .NET versions, and servers where .NET was installed manually from a tarball. Those need a separate procedure.

⚠️ Before you install anything, save copies of your Server Connect scripts, schedule entries and configuration files. The checks in [Confirm your scripts and config still work](#h_0e8efb786a) compare against that baseline, and without it you cannot prove nothing changed.

## Which package to install

Install the **[ASP.NET Core Runtime 10](https://dotnet.microsoft.com/en-us/download/dotnet/10.0)**, latest 10.x.x release. Server Connect needs both `Microsoft.NETCore.App` and `Microsoft.AspNetCore.App`, and this single package provides both.

The runtime is all that is required. The SDK is not needed on servers.

| Server | Package | Where to get it |
|---|---|---|
| RHEL / Rocky / Alma | `aspnetcore-runtime-10.0` (dnf) | Distro AppStream repository |
| Ubuntu / Debian | `aspnetcore-runtime-10.0` (apt) | Ubuntu 24.04+: Ubuntu feed, or `ppa:dotnet/backports`. Ubuntu 22.04 and Debian: distro or Microsoft feed, depending on the release |
| Windows Server | `aspnetcore-runtime-10.<minor>.<patch>-win-x64.exe` | Microsoft download page, or winget / WSUS / SCCM |
| Windows with IIS hosting the app | ASP.NET Core Hosting Bundle 10.x.x | Same download page |

💡 **Version policy:** this guide covers every .NET 10 release. Always install the latest 10.x.x published at the time of your change. Package names like `aspnetcore-runtime-10.0` follow the version band your distribution publishes; if a later 10.x band appears, use its matching package name. .NET 10 is a long-term support release, supported until November 2028.

## Pre-install checks

Record these per server before installing. Check 3 decides your install method: use the same method and .NET root that Server Connect already uses.

1. **OS and CPU**
   - Linux: `cat /etc/os-release; uname -m`
   - Windows: `Get-ComputerInfo OsName,OsVersion,OsArchitecture`
2. **Installed runtimes:** `dotnet --list-runtimes`. Save the output; you compare against it later.
3. **How .NET is installed today**
   - Linux: `readlink -f $(which dotnet)`, plus `rpm -qa | grep -i dotnet` or `dpkg -l | grep -i dotnet`
   - Windows: `where.exe dotnet` (normally `C:\Program Files\dotnet`)
4. **Disk space:** at least 300 MB free on the volume holding the .NET root (`df -h`, or `Get-PSDrive C`)
5. **Repository or internet access:** `dnf repolist` or `apt-get update`, or confirm the package has been copied to the server

⚠️ If check 3 returns a path like `/opt/dotnet` with no matching package, .NET was installed manually from a tarball. Stop here and use the separate tarball procedure instead. If you end up with a second install method on the server, PATH, `DOTNET_ROOT` and the service configuration all have to be validated explicitly before sign-off.

## Linux install steps

Use the package manager already in use for .NET, as identified in pre-install check 3. Mixing sources (distro package, Microsoft feed, manual install) can make `dotnet` resolve a different host or runtime than you intended.

**RHEL / Rocky / Alma**, with the distribution's supported .NET 10 repository (AppStream) enabled:

```
sudo dnf install -y aspnetcore-runtime-10.0
```

**Ubuntu / Debian:**

```
sudo apt-get update && sudo apt-get install -y aspnetcore-runtime-10.0
```

**SUSE**, from Microsoft's feed:

```
sudo zypper install -y aspnetcore-runtime-10.0
```

## Windows install steps

Run these from an elevated PowerShell window. A reboot is rarely needed. If you use the Hosting Bundle, IIS restarts during the install.

1. **Check the installer** against the checksum published on the download page:

   ```
   Get-FileHash .\aspnetcore-runtime-10.<minor>.<patch>-win-x64.exe -Algorithm SHA512
   ```

2. **Install** using one of:
   - **Interactive:** run the .exe and accept the defaults.
   - **Silent:**

     ```
     .\aspnetcore-runtime-10.<minor>.<patch>-win-x64.exe /install /quiet /norestart /log C:\temp\dotnet10-install.log
     ```

   - **winget:** `winget install Microsoft.DotNet.AspNetCore.10`
   - **SCCM / Intune / WSUS:** deploy the same .exe with the silent switches above.
3. **Check the install log** for `Exit code: 0x0`. A code of `0xBC2` also means success, with a reboot required.
4. **Close and reopen PowerShell** before verifying, so the PATH is refreshed.

## Verify the install

The install passes when the account that runs Server Connect sees both 10.x.x runtimes, and the older runtimes are still listed.

1. **As the administrator:** `dotnet --list-runtimes` shows `Microsoft.NETCore.App 10.x.x` and `Microsoft.AspNetCore.App 10.x.x`.
2. **As the service account:**
   - Linux: `sudo -u <service-user> -i dotnet --list-runtimes`. If Server Connect runs as a systemd service, also check the unit's own environment with `systemctl show <unit> -p Environment -p ExecStart` and confirm its PATH and `DOTNET_ROOT` point to the same `dotnet`.
   - Windows: `runas /user:<domain\svc-account> "cmd /k dotnet --list-runtimes"`
3. **Every runtime from your pre-check list is still present.** Patch versions may be newer after OS updates.
4. **`dotnet --info` as the service account** resolves to the intended .NET root, normally unchanged from pre-install check 3, and lists the 10.x.x runtimes.
5. **Existing apps are unaffected:** the next scheduled Server Connect run on your current build completes with a clean log.

## Apply OS updates

Once the install is verified, apply outstanding OS updates in the same change window, following your patching policy. On servers that take .NET from the OS repository or Microsoft Update, this also brings .NET 10 to its latest patch.

1. **Apply updates:**
   - RHEL / Rocky / Alma: `sudo dnf upgrade -y`
   - Ubuntu / Debian: `sudo apt-get update && sudo apt-get upgrade -y`
   - SUSE: `sudo zypper patch -y`
   - Windows: install approved updates through WSUS, SCCM, Intune, or **Settings → Windows Update**. Turn on **Receive updates for other Microsoft products** so .NET patches are included.
2. **Check whether a reboot is needed:**
   - RHEL / Rocky / Alma: `sudo needs-restarting -r`
   - Ubuntu / Debian: `ls /var/run/reboot-required` (if the file exists, a reboot is needed)
   - Windows: Windows Update shows "Restart required", or the install log reports `0xBC2`
3. **Reboot if needed**, inside the change window.
4. **After the reboot,** confirm the Server Connect service, cron entries or Scheduled Tasks are active again.
5. **Repeat verify steps 1 to 4.** Runtime patch versions may now be newer, which is expected.

⚠️ Do not reboot while a scheduled Server Connect run is in progress.

## Confirm your scripts and config still work

All existing scripts and configuration must work exactly as they did before the install. Nothing in them is edited during this process. If any check below fails, stop and back out.

| # | Check | How | Pass when |
|---|---|---|---|
| 1 | Scripts unchanged | Compare each script and cron or Scheduled Task entry with the copy you saved before installing (diff, or `Get-FileHash`) | No differences |
| 2 | Config unchanged | Same comparison for `Configs`, `Config/appsettings.json` and any environment variables, for example `DOCKER` and `DOTNET_ROOT` | No differences |
| 3 | Script runs by hand | Run the script's exact command line as the service account | Exit code 0, new clean log in `Logs` |
| 4 | Scheduled run works | Let the next cron, timer or Scheduled Task run fire on its own | Run completes, nothing in `uploadedfiles/Failed` |
| 5 | No new errors | Compare the newest log with the last pre-install log | No new errors or warnings caused by the install |
| 6 | Upload lands | Check the Omnisient Platform for the dataset upload from check 4 | Upload shows as received |

## What to expect

When the install is done correctly:

- `dotnet --list-runtimes` shows the 10.x.x runtimes **in addition to** every runtime that was there before. Nothing is replaced.
- The service account sees the same list as the administrator, resolving to the same .NET root.
- Your existing Server Connect build keeps running on its current runtime. Scheduled uploads complete, logs are clean, and uploads land in the Omnisient Platform as before.
- No script, schedule entry or configuration file has changed.

## Common issues

| Issue | Likely cause | Fix |
|---|---|---|
| `aspnetcore-runtime-10.0` not found on Ubuntu or Debian | The .NET 10 packages aren't in the feeds configured on the server | Ubuntu 24.04+: add `ppa:dotnet/backports`. Ubuntu 22.04 and Debian: add Microsoft's feed, per your repository policy. Then retry the install |
| Pre-install check 3 shows a path like `/opt/dotnet` with no matching package | .NET was installed manually from a tarball, not through the package manager | Stop. This server needs the separate tarball procedure, not this one |
| Windows install log reports `Exit code: 0xBC2` | The install succeeded but needs a reboot | Reboot inside the change window, then repeat the verify steps |
| `dotnet --list-runtimes` doesn't show 10.x.x straight after a Windows install | The PowerShell session is still using the old PATH | Close and reopen PowerShell, then run the command again |
| The administrator sees 10.x.x but the service account doesn't | The service resolves a different `dotnet`, or the unit's PATH or `DOTNET_ROOT` points elsewhere | On Linux, check `systemctl show <unit> -p Environment -p ExecStart` and confirm it points at the same `dotnet`. Don't sign the server off until it does |
| A runtime from the pre-check list now shows a higher patch version | OS updates brought an existing runtime to its latest patch | Expected, not a failure. The runtime is still present, which is what the check requires |

## Back out (remove .NET 10)

Backing out is rarely needed, because .NET 10 does not change the runtime your existing apps use. Remove it only if the change is rejected or a check fails.

- **Linux:** `sudo dnf remove aspnetcore-runtime-10.0 dotnet-runtime-10.0`, or `sudo apt-get remove aspnetcore-runtime-10.0 dotnet-runtime-10.0`
- **Windows:** uninstall **Microsoft ASP.NET Core 10.x.x - Shared Framework** and **Microsoft .NET Runtime 10.x.x** from **Apps & features**, or run `winget uninstall Microsoft.DotNet.AspNetCore.10`

Then repeat verify steps 3 to 5 to confirm the server is back to its pre-install state.

## Related

- 👉 [Server Connect: Installation](https://help.omnisient.com/en/articles/10102684-server-connect-installation)
- 👉 [Minimum System Requirements](https://help.omnisient.com/en/articles/8684027-minimum-system-requirements)
- 👉 [What is Server Connect?](https://help.omnisient.com/en/articles/8861153-what-is-server-connect)
- 👉 [Server Connect Anonymization and Upload Process](https://help.omnisient.com/en/articles/10110433-server-connect-anonymization-and-upload-process)
- 👉 [Desktop Application Troubleshooting FAQ](https://help.omnisient.com/en/articles/7019202-desktop-application-troubleshooting-faq)
