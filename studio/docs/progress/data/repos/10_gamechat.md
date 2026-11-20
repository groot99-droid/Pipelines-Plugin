# gamechat

**Private voice, video and screen-share rooms for gaming (Electron).** Source: https://github.com/groot99-droid/gamechat

Generated 20 November 2026 from the repository clone (`git log`, `git ls-files`, and the files at HEAD). Counts are as cloned. Commit dates are git author dates in UTC and can differ from when the work was done (merged PRs, integration passes).

## 1. Numbers

| Measure | Value |
|---|---|
| Commits (all branches) | 5 (4 non-merge, 1 merge) |
| First commit | 2026-11-15 |
| Last commit | 2026-11-19 |
| Days with commits | 2 |
| Tracked files | 24 |
| Checked-out branch | HEAD |
| Commit authors (non-merge, by name) | groot99-droid: 3; Claude: 1 |

Author names are git author names: "Claude" marks commits made by a Claude session, and the owner's GitHub handle marks commits made by the owner. Email addresses are left out.

**Tracked files by type (top 15):** .js 13; .html 2; .json 2; (none) 1; .md 1; .txt 1; .ico 1; .png 1; .ps1 1; .css 1

**Tracked files by top-level folder:** (root) 12; renderer 6; build 3; overlay 3

## 2. Activity by month and by day

| Month | Non-merge commits |
|---|---|
| 2026-11 | 4 |

**Per day (non-merge commits):** 2026-11-15 3; 2026-11-19 1

## 3. Layout (folders and file counts)

- **(repository root)** 12 files
- **renderer/** 6 files
- **build/** 3 files
- **overlay/** 3 files

## 4. package.json (root)

- name: gamechat; version: 2.2.0
- scripts: `start`; `icon`; `test`; `dist`; `dist:mac`; `dist:linux`
- dependencies: @achingbrain/nat-port-mapper, selfsigned, uiohook-napi, ws
- devDependencies: electron, electron-builder, rcedit

## 6. Documents inventory (1 Markdown files)

Markdown files by folder (top 25): (root) 1

- `README.md` (255 words): GameChat. Sections: Install (Windows); Phone (iPhone / Android, nothing to install); Use

## 10. Pull requests merged (1)

- 2026-11-19 #1 from `groot99-droid/claude/inspiring-cori-juqfrm`

## 11. Source documents (verbatim)

Each file below is quoted from the repository at HEAD. Lines start with ">" so its headings do not mix with this document's.

### Source file: README.md

> # GameChat
>
> Private, serverless voice / video / screen-share rooms for gaming with friends. No accounts, no cloud.
>
> ## Install (Windows)
>
> **One line** (PowerShell):
>
> ```powershell
> irm https://raw.githubusercontent.com/groot99-droid/gamechat/main/install.ps1 | iex
> ```
>
> **Or download** from the [latest release](https://github.com/groot99-droid/gamechat/releases/latest):
> `GameChat-Setup-*.exe` (installer + shortcut) or `GameChat-Portable-*.exe` (no install).
>
> The app is unsigned: SmartScreen > *More info* > *Run anyway*; allow the firewall prompt (Private and Public).
>
> ## Phone (iPhone / Android, nothing to install)
>
> 1. On the PC that hosts the room, start the room. The header shows **Phone: https://<pc-ip>:7778**.
> 2. Open that link in the phone's browser (same Wi-Fi, or Tailscale on the phone).
> 3. The page uses a self-signed certificate, so accept the warning once (Advanced > Proceed). HTTPS is what lets the browser use the mic.
> 4. Enter name + room password > Join. Voice, camera, chat, channels and soundboard work; hosting, screen share, clips, overlay and hotkeys are PC-only.
>
> Tip: use "Add to Home Screen" for an app-like icon. Keep the screen on while talking; browsers pause audio when the tab is in the background.
>
> ## Use
>
> Host: name + room + password > Start room > copy the invite code to friends. Join: paste the code.
> Friends outside your network: use Tailscale. See the in-app Settings for hotkeys, soundboard, clips and overlay.
>
> El Fuego quick-room: the password is not bundled; enter it once and it is remembered.
>
> The full user guide (hosting, channels, hotkeys, voice, soundboard and clips, overlay, Internet mode, troubleshooting, privacy, building from source) is in [README.txt](README.txt), which ships with the app.
>

## 12. Full commit log (date, hash, subject)

Every commit, oldest first. Merge commits are shown with their subjects.


### 2026-11

- 2026-11-15 92ddc054 GameChat 2.1.0
- 2026-11-15 1a466332 Fix slow download in installer script
- 2026-11-15 fd0eb3f7 Phone web client: host serves the UI over HTTPS (v2.2.0)
- 2026-11-19 0c5dce17 docs: bring README.txt up to v2.2.0 (phone client, version-free file names, unversioned tests)
- 2026-11-19 c4ef4589 Merge pull request #1 from groot99-droid/claude/inspiring-cori-juqfrm [merge]
