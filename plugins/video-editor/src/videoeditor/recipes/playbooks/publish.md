# Playbook: publish (optional closing step)

`ve publish` sends a finished video through official platform APIs. It never logs in with a password or a browser.

## What you may do without asking
- `ve publish prepare` and `ve publish plan` (no network, nothing leaves the machine).
- `ve publish handoff` (prints where to upload and the caption to paste).
- `ve publish status` (shows what is configured and the ledger).

## What needs the user's explicit instruction, every time
- `ve publish init <platform>` (they paste credentials; you never ask for or see a password).
- `ve publish send --platform NAME --yes`: one platform per command, after showing them the plan and the mode.
- `--public`: public posting. The default is private/draft wherever the platform has one. Bluesky and X have none, so
  they cannot be used without it. Say so before they choose.
- `--accept-cost` (X is pay-per-post) and `--force` (repeat an identical send).

## Declarations that belong to the user
- YouTube "made for kids": ask; never default it (`--made-for-kids` / `--not-made-for-kids`).
- `--ai-generated` if the video contains AI-generated or synthetic media; `--branded` for paid partnerships.

## Writing the post
Write a separate caption per platform (`--caption-for x="..."`), within each platform's limit. `ve publish plan` shows
length, aspect, duration and format problems before anything is sent. Hashtags go in `--tags` (no `#`).

## Platform behaviour to tell the user about
- TikTok draft mode puts the video in their TikTok inbox; the caption is NOT sent, they paste it (the command prints it).
- Instagram draft mode prepares the Reel but does not publish it; the container expires in 24 hours.
- LinkedIn has no draft: "draft" means connections-only visibility. Its token lasts 60 days.
- A platform that refuses `--yes` without `--public` is working as intended; do not work around it.

## When something fails
Read the error, fix the cause, and retry that one platform. A failed attempt is recorded but does not block a retry; a
successful one does (use `--force` only if the user wants a second post). If a platform's API behaves differently from
what the code expects, say so plainly rather than retrying blindly: these integrations were verified against official
docs and fake servers, not live accounts.
