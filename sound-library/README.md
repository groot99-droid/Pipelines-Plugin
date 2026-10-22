# Sound library

The author's own sound effects, catalogued in one place so a project (a game,
a video, a studio run) can find a sound by what it is and have the file put on
disk.

| What | Versioned | |
|---|---|---|
| `catalog.json` | yes | one entry per sound: id, name, category, duration, sample rate, channels, bit depth, size, sha256, tags, and where its original is kept |
| `files/<category>/<slug>.<ext>` | **no** | the originals. A batch of ten zips is 230 MB; the library will be several GB |
| `library.py` | yes | `ingest`, `search`, `show`, `fetch`, `verify`, `status`. Stdlib only |
| `tests/` | yes | run on temporary folders with generated WAVs |

The originals live as zips attached to **GitHub Releases of this repo**, not in
git. A release holds any number of files up to 2 GB each, costs nothing, and is
uploaded from a browser; `fetch` reads the release through the public API and
needs no token. Git LFS was not chosen: a public repo's LFS bandwidth is spent by
every clone, and when it runs out the files are gone for the author too.

## Find a sound

```
python sound-library/library.py search "boat horn"
python sound-library/library.py search "" --category bus --max-seconds 3
python sound-library/library.py search "" --loopable
python sound-library/library.py show boats/deep-boat-horn
python sound-library/library.py status
```

`search` ranks by the words of the query against name, tags and category, and
marks each result `here` when the file is on disk. `--json` gives the same for a
script.

## Put a sound on disk

```
python sound-library/library.py fetch --dry-run --category boats
python sound-library/library.py fetch --id boats/deep-boat-horn --id bus/bus-hydraulic
python sound-library/library.py fetch --query "harley" --release sfx-2026-10
python sound-library/library.py fetch --category bicycle --from ~/Downloads/Bicycle_Pt1.zip --from ~/Downloads/Bicycle_Pt2.zip
```

Without `--from`, `fetch` downloads the zip each entry records from its release
(the recorded tag, or `--release`), takes the member out and checks its sha256
before placing it. One download serves every sound in that zip. With `--from`,
it takes the files from a local zip or folder by content hash, so the author's
own copies, or a zip uploaded to a session, work without the network and whatever
they are named. A sound already on disk is never downloaded again.

The file lands at `sound-library/files/<category>/<slug>.wav`. Copy it into the
project that needs it; this folder is not versioned and is never added to git.

## Add a batch

1. Recordings are WAV, or M4A where that is what exists; both are read for
   duration, sample rate and channels. The author zips a batch per category (`Boats_Pt1.zip`, `Boats_Pt2.zip`...).
   The zip's name gives the category: `Motor_Bikes_Pt3.zip` → `motor-bikes`;
   `--category` overrides it. Folders inside the zip and macOS `__MACOSX`
   entries are fine.
2. Attach the zips to a release of this repo (GitHub → Releases → *Draft a new
   release*, tag for instance `sfx-2026-10`, drag the zips in, publish). The
   same zips, byte for byte, that are ingested; if a zip is rebuilt, `fetch`
   still finds each file by its hash.
3. Ingest, with that tag:

   ```
   python sound-library/library.py ingest Boats_Pt1.zip Boats_Pt2.zip --release sfx-2026-10
   python sound-library/library.py verify
   python -m unittest discover -s sound-library/tests
   ```

   Or, once the release is published, from anywhere with no copy of the zips:

   ```
   python sound-library/library.py ingest --from-release sfx-2026-10
   ```

   `ingest` prints `N new, N already there, N replaced, N refused`. A file whose
   name gives an id the catalog already holds with different content is refused
   unless `--replace`. Two files with the same content under different names are
   both kept; `ingest` and `verify` note the pair and neither fails on it.
4. Commit `catalog.json`. Nothing else here changes.

In a Claude Code session on this repo, the `sound-library` skill does steps 3
and 4 from uploaded zips and tells the author which release to attach them to.

## What it keeps, and what it does not

- Names are the author's, verbatim; the id is derived from them
  (`Riding Bike Wet Ground (loopable)` → `bicycle/riding-bike-wet-ground-loopable`).
  A name with `loop` in it marks the sound loopable.
- The catalog is versioned and the repo is public: a sound's name, duration and
  hash become public when pushed, and so does a zip attached to a release of a
  public repo. The catalog holds no link and no path.
- It is not a studio run. It writes nothing into `studio/vault/` or `studio/assets/`.
- Never edit `catalog.json` by hand; `ingest` and `--replace` are the ways in.

## Checking it

```
python -m unittest discover -s sound-library/tests
python sound-library/library.py verify
```

Exit codes: 0 done, 1 some items failed or refused, 2 usage error.
