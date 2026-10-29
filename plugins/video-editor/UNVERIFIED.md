# Not verified yet, and deferred work

Kept here so it can be surfaced later (the same list is tracked in the Video-Editor repository, issue 4). Nothing
here blocks use. Each item is something that was **not verified** or **deliberately deferred**.

## `ve publish`: first live run checklist
No platform was ever run against a real account. Request shapes were checked against the official docs, a fake
network, and a local HTTP server. Check these on first real use, one platform at a time, starting with Bluesky or
Mastodon. Run `ve publish plan` first; it sends nothing.

**Bluesky**
- [ ] Service-auth audience and method for video upload. The code uses `aud=did:web:<user's PDS host>` and
      `lxm=com.atproto.repo.uploadBlob` (taken from Bluesky's own client; the lexicons do not state it).
- [ ] `app.bsky.video.uploadVideo` is called with `did` and `name` query params; the lexicon lists none, so
      confirm they are accepted or ignored.
- [ ] Max video duration is unknown (lexicon: 300 MB, mp4). The 300-grapheme limit is a warning only.
- The app.bsky lexicons live in `bluesky-social/social-app/lexicons`, not in `atproto`.

**LinkedIn**
- [ ] Is `userinfo.sub` the id used in `urn:li:person:<id>`? Override with `VE_LINKEDIN_PERSON_ID` if not.
- [ ] Does the app accept `http://127.0.0.1` as a redirect? Otherwise use `ve publish init linkedin --manual`.
- [ ] `Linkedin-Version` is pinned to `202610`; versions are sunset on a schedule (override with
      `VE_LINKEDIN_VERSION`). Tokens last 60 days and self-serve apps get no refresh token.
- [ ] Whether a post must wait for the video status `AVAILABLE` (the code waits, then proceeds on timeout).
- No draft state exists for API posts; "draft" here means connections-only visibility.

**TikTok**
- [ ] Scope separator (the code uses a comma), authorize-URL parameters, and whether the redirect may be
      localhost (`--manual` fallback). PKCE is off (documented for mobile/desktop apps only).
- [ ] Inbox ("Upload") mode documents no caption field, so the caption is not sent; the CLI prints it.
- [ ] Public Direct Post needs `video.publish` and, for non-private posts, an audited app.

**Instagram Reels**
- [ ] Resumable upload is documented for "Facebook Login for Business" only; the alternative is hosting the file
      and setting `VE_INSTAGRAM_VIDEO_URL`.
- [ ] The docs advise polling the container once a minute for up to 5 minutes; large files may need longer (the
      error names the container id).
- [ ] The publishing cap is stated as 50 and as 100 per 24 h on different Meta pages.
- [ ] Token and user id are supplied by hand; the 60-day token refresh and the Meta login flow are not automated.

**X**
- [ ] Whether media-upload calls are billed (only post creation is priced: about $0.015, $0.20 with a URL).
- [ ] The OAuth token exchange for public vs confidential apps; the 280-character limit is a warning only; video
      duration and size caps depend on Premium status.

**YouTube**
- [ ] What counts as a Short (the developer docs do not say; the code uses vertical or square and 3 minutes or
      less as a hint).
- [ ] Refresh-token lifetime for apps in test mode (not confirmed on the pages read).
- Official docs say unverified API projects are **not** forced private; 1 quota unit per upload, 100 per day by default.

**Mastodon**
- [ ] Scopes needed (`write:media`, `write:statuses`); the settings menu path for creating a token varies by version.

## Optional backends: not tested
- [ ] whisperX **speaker diarization** (needs a Hugging Face token and accepting the pyannote terms). Only the
      plumbing is unit-tested.
- [ ] Real footage and real human speech (everything ran on synthetic fixtures). whisperX word starts were about
      41 ms from true onsets vs about 112 ms for faster-whisper on one synthetic clip: re-measure.
- [ ] GPU paths; the Manim and HyperFrames engines, and Remotion beyond this plugin's own small template.
- [ ] whisperX needs NLTK `punkt_tab` once (the build sandbox blocked the download).
- [ ] Remotion is not open source: free for individuals, for-profit organisations of up to 3 people and
      non-profits; others need a company licence.

## Known limits
- Local Whisper normalizes fillers ("um", "uh"), so filler removal is best-effort.
- Speaker-follow reframing needs a static camera and two hand-placed face regions, unless a diarized transcript is used.

## Deferred ideas
- [ ] More `ve publish` platforms: Pinterest, Reddit, Facebook Pages (APIs exist). Hacker News has no posting API.
- [ ] Automate Instagram/Meta token handling; remind before LinkedIn's 60-day expiry.
- [ ] Let `ve publish` read its credentials from the repo's key helper convention (`docs/setup_keys.py`) instead of
      only the OS keyring and `VE_*` variables. It was left separate on purpose: that helper writes a file.
- [ ] Decide whether to archive the standalone Video-Editor repository now that the code lives here.
