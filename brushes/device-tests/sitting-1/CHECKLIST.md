# Sitting 1: the control set

This folder was made by `python brushes/pipeline/device_tests.py build sitting-1 --confirm`.
Git keeps three things of it: `manifest.json`, this checklist, and whatever is put in
`returned/`. The brush files built here are scratch and are not committed.

## What this is for

Nothing this tool has written has been opened in Procreate yet. This sitting asks the
narrowest question first: does Procreate open a brush set that we packed, when every
brush inside it is one that Procreate or a brush maker already made?

The set holds 8 brushes taken from the library. Every file inside every brush is,
byte for byte, the original. Only three things are ours: the zip container around them,
the folder name each brush sits in, and the small list (`brushset.plist`) that names the
set and puts the brushes in order. If Procreate opens this set, those three things are
right, and later sittings can test edited and newly made brushes.

It takes about fifteen minutes. You need the iPad, Procreate, and a way to move files
to the iPad and back.

## What is in this folder

| File | What it is |
|---|---|
| `ROSW-1-control.brushset` | the control set, named "ROSW 1 Control", 8 brushes |
| `singles/` | the same 8 brushes, one `.brush` file each. Only needed if the set fails |
| `known-bad/KNOWN-BAD_old-designer.brush` | a brush file the old Brush Designer wrote, which is malformed. Never a file to bring back |
| `returned/` | empty. What comes back from the iPad goes here |
| `manifest.json` | what was built and from where, with checksums. For the comparison afterwards |
| `CHECKLIST.md` | this file |

## What to bring back

1. The Procreate version, the iPadOS version and the iPad model.
2. What happened when you opened the known-bad file.
3. Your answers to the questions in the table below.
4. Two files: the control set shared back out of Procreate, and one brand-new
   untouched brush.

Photos of the screen are welcome wherever words are slow.

## Step 1. Get the files onto the iPad

Any route works, as long as the files arrive unchanged:

- **iCloud Drive.** On this computer, sign in at icloud.com, open iCloud Drive, and upload
  `ROSW-1-control.brushset`, the file in `known-bad/` and the files in `singles/`.
  They then appear in the Files app on the iPad, under iCloud Drive.
- **Another cloud drive** that shows up in the Files app (Google Drive, OneDrive,
  Dropbox): the same.
- **Email** the files to yourself and open the message on the iPad.
- **AirDrop**, if the files are on a Mac.

On the iPad, open the Files app, find the files, and wait until each has finished
downloading (no cloud symbol beside it).

To open a brush file: tap it in Files. Procreate should open and take it in. If
something else opens instead, press and hold the file, choose Share, then Procreate.

## Step 2. Write down the versions

- **Procreate version.** In the iPad's Settings app, find Procreate in the list of apps;
  the version is shown on that page. If you cannot find it there, the App Store page
  for Procreate shows it under Version History.
- **iPadOS version and iPad model.** Settings, General, About.

## Step 3. Open the known-bad file first

Tap `KNOWN-BAD_old-designer.brush`. The old Brush Designer wrote this file, and it is
malformed: its Brush.archive holds a single piece of text where a brush's settings should be, not the keyed archive a brush file carries.

We expect Procreate to refuse it, and we want to see what a refusal looks like on your
version, so that we recognise one if a file of ours gets the same treatment. Write down
exactly what happens:

- the words of any message (a photo of the screen is best), or
- "nothing happened", or
- "a brush appeared". If one did, say what it is called and whether it draws, then
  delete it straight away (swipe left on the brush, Delete). It may be called
  "Untitled Brush", which is also what the new brush of the last step is called, and
  the two must not be mixed up.

If Procreate closes by itself, open it again and carry on.

## Step 4. Import the control set

Tap `ROSW-1-control.brushset`.

What should happen: Procreate opens and takes the set in. To see it, open any canvas
(the brush icon is only there inside a canvas, not in the Gallery), then tap the brush
icon at the top right. A new brush set named **ROSW 1 Control** is in the Brush Library.
It holds 8 brushes, in this order:

1. Broken Conté
2. AN Botanicaliser
3. IGB 6B Pencil
4. Pandani
5. Studio Pen
6. Narinder Pencil
7. Cocoa
8. Volcanic Ash

If Procreate shows a message instead, write down its words, then go to "If the set does
not import" below.

## Step 5. Look at each brush

Stay in that canvas and pick black. For each brush in the set, answer three plain questions:

- **Listed?** Is it in the set, under the name given here?
- **Preview?** Does its row in the Brush Library show a picture of a stroke?
- **Draws?** Select it and draw one stroke. Does a mark appear?

| # | Name | What it is | Listed? | Preview? | Draws? |
|---|---|---|---|---|---|
| 1 | Broken Conté | oldest format (E0, 52 keys) |  |  |  |
| 2 | AN Botanicaliser | plain legacy brush (E4, 101 keys) |  |  |  |
| 3 | IGB 6B Pencil | names built-in textures (E3, 88 keys) |  |  |  |
| 4 | Pandani | dual brush (M220, 221 keys) |  |  |  |
| 5 | Studio Pen | no preview in the file (M220, 220 keys) |  |  |  |
| 6 | Narinder Pencil | maker's picture and signature (M220, 220 keys) |  |  |  |
| 7 | Cocoa | dual brush with a reset point (M173, 173 keys) |  |  |  |
| 8 | Volcanic Ash | newest format (M242, 242 keys) |  |  |  |

Then one more question for each brush. To open Brush Studio, tap a brush that is
already selected.

1. **Broken Conté.** This is the oldest kind of brush file. Is its name written correctly, accent included? Its stored preview picture is an older, smaller size (440 x 276 pixels): does the preview in the list look right, stretched, or empty?
2. **AN Botanicaliser.** Nothing special: this is the plain case. If this one is missing or does not draw, say so first, because everything later builds on it.
3. **IGB 6B Pencil.** This brush carries no pictures of its own. It only names textures that came inside older versions of Procreate (`Brush-Pocket-Brick.png` and `Brush-Artery-Charcoal-Corse.jpg`). Does it draw with a texture, as a plain solid line, or not at all?
4. **Pandani.** This is a dual brush: two brushes working as one. Tap it a second time to open Brush Studio. Does Brush Studio show two brushes (a dual brush shows both of its brushes at the top left)? Does a stroke look like its preview?
5. **Studio Pen.** This brush file has no preview picture in it. In the Brush Library list, is its preview empty, or did Procreate draw one itself?
6. **Narinder Pencil.** In Brush Studio, open "About this brush". Is there a maker's name, a picture and a signature?
7. **Cocoa.** Another dual brush, and the one with the most inside it: it also carries a saved reset point. Does Brush Studio show two brushes? In "About this brush", is "Reset brush" offered? Look only; do not tap it.
8. **Volcanic Ash.** This is the newest kind of brush file in the library. It keeps its texture in the file under its own name (`GL-Volcanic-Grain.png`, `GL-Volcanic-Grain.png`). Does it draw with a texture?

Leave Brush Studio with Cancel each time, so that nothing in the set is changed before
you share it back.

### If the set does not import, or a brush is missing or will not draw

Open the files in `singles/` one at a time, in number order. Each holds one brush of the
set. A single brush lands in the set named "Imported". Note for each file whether it
arrives and whether it draws. That tells us which brush is at fault.

A single file for a dual brush or a brush with a reset point is laid out in a way we
have not yet seen Procreate write, so if one of those fails only as a single file, say
so and do not worry about it.

## Step 6. The return leg: share two things back

**a. The control set.** In the Brush Library, tap the set name **ROSW 1 Control** so that it
is selected, then tap it once more. A small menu appears: choose Share. Save the file to
Files (in the same cloud folder is fine). It is saved as a `.brushset` file. This shows
what Procreate kept of each brush and what it rewrote.

**b. One brand-new, untouched brush.** In the Brush Library, tap the **+** at the top
right. Brush Studio opens with a new brush. Change nothing, and tap Done. The new brush
is now in the list (it is usually called "Untitled Brush"). Swipe left on it, tap Share,
and save it to Files. It is saved as a `.brush` file. This is what Procreate itself
writes today, and it becomes the starting point for brushes this tool makes.

Keep the file names Procreate gives them.

## Step 7. Put the returned files here

Back on this computer, put both files in:

    brushes/device-tests/sitting-1/returned/

(that is the `returned` folder beside this file). Add your notes there too: a
`notes.txt` with the versions and your answers, or photos of this page filled in.

Do not put the known-bad file (`KNOWN-BAD_old-designer.brush`) in `returned/`, nor any brush that
came out of it: that folder is for the two files of the return leg and your notes.

What is in `returned/` is kept in git, together with `manifest.json` and this page: it
is the only record of what the iPad did, and no build can make it again.

Do not build this sitting again once files are in that folder: a new build gives the
brushes new folder names, and the returned files are compared with this one.

Afterwards you can delete the set and the new brush from Procreate (swipe left, Delete).
