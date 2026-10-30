# Sitting 2: edited brushes and brushes made from nothing

This folder was made by `python -I brushes/pipeline/device_tests.py build sitting-2 --confirm`.
Git keeps three things of it: `manifest.json`, this checklist, and whatever is put in
`returned/`. The brush files built here are scratch and are not committed.

## Before you start: sitting 1 comes first

Do sitting 1 (`../sitting-1/CHECKLIST.md`) before this one, in the same session: first its
known-bad file, then the control set, ROSW 1 Control. **If ROSW 1 Control does not open,
stop there** and bring back what sitting 1 asks for; do not go on with this checklist.
Every set here is packed the way ROSW 1 Control is. Until the control set has opened, a set
here that fails cannot tell us whether the brushes we wrote are at fault or the packing.

## What this is for

Sitting 1 asks whether Procreate opens a set we packed around brushes it made itself.
This sitting asks the next two questions. Nothing in these two sets has been opened in
Procreate yet.

1. **ROSW 2 Edits** (45 brushes). Does Procreate open a brush whose settings file
   we wrote ourselves after changing one setting? Each brush is a copy of one of two
   brushes from the library, with one setting changed, and is named after that change:
   `L02 plotSpacing=0.1` is the older brush with its spacing set to 0.1. Its shape and grain
   pictures are the original's, byte for byte. A few settings are two or three numbers that
   go together, so a name may show two or three of them.
2. **ROSW 3 Scratch & Ünï 💧** (6 brushes). Does Procreate open a brush made from
   nothing? Every file in these brushes is ours.

Your screenshots of Brush Studio also tell us what each number in a settings file means,
which today is only a guess.

It takes about an hour, most of it the screenshots. You need the iPad, Procreate, and a
way to move files to the iPad and back.

## What is in this folder

| File | What it is |
|---|---|
| `ROSW-2-edits.brushset` | the edited brushes, named "ROSW 2 Edits", 45 brushes |
| `ROSW-3-scratch.brushset` | the brushes made from nothing, named "ROSW 3 Scratch & Ünï 💧", 6 brushes |
| `singles/` | every brush of both sets as a `.brush` file of its own, named by its code. Needed if a set fails; one of them is worth a tap anyway (Step 5b) |
| `returned/` | empty. What comes back from the iPad goes here |
| `manifest.json` | what was built and from where, with checksums. For the comparison afterwards |
| `CHECKLIST.md` | this file |

## What to bring back

1. The Procreate version, the iPadOS version and the iPad model.
2. Your answers in the two tables below.
3. One Brush Studio screenshot for each brush of ROSW 2 Edits (45 screenshots),
   taken in the order of the list, so that each can be matched to its brush.
4. Three files: both sets shared back out of Procreate, and one brand-new untouched brush.

Photos of the screen are welcome wherever words are slow.

## Step 1. Get the files onto the iPad

Any route works, as long as the files arrive unchanged:

- **iCloud Drive.** On this computer, sign in at icloud.com, open iCloud Drive, and upload
  `ROSW-2-edits.brushset`, `ROSW-3-scratch.brushset` and the files in `singles/`.
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

## Step 3. Import ROSW 2 Edits

Tap `ROSW-2-edits.brushset`. Open any canvas, then tap the brush icon at the top right. A brush set
named **ROSW 2 Edits** should be in the Brush Library, holding 45 brushes whose names
start with L00, L01 and so on, then M00, M01 and so on.

If Procreate shows a message instead, write down its words, then go to "If a set does not
import" below.

## Step 4. Each edited brush: three questions and one screenshot

- The 24 **L** brushes are copies of **AN Botanicaliser**, an older brush (the 101-key format), the same brush as member 2 of sitting 1.
- The 21 **M** brushes are copies of **Hard**, a current brush (the 220-key format).
- A brush called "name only" changes nothing but its name. L00 and M00 keep the original's
  preview picture. **Every other brush has no preview picture in its file**, so if its row
  in the list shows a stroke, Procreate drew it.

Pick black. For each brush, in list order:

1. **Listed?** Is it there, under its name?
2. **Preview?** What does its row in the list show: a stroke, or nothing?
3. **Draws?** Select it and draw one stroke across the canvas. Does a mark appear?
4. **Screenshot.** Tap the selected brush again to open Brush Studio. Open the tab the table
   names (our guess at where the changed setting is) and take a screenshot (top button and
   volume up together). For a "name only" brush, the "About this brush" tab. Then
   leave with Cancel, so that nothing is changed before you share the set back.

Anything else you notice goes beside the row: a message, Procreate closing, a stroke that
looks wrong, a setting that is not where the table says.

| # | Name | Where we think the setting is | Listed? | Preview? | Draws? | Screenshot? |
|---|---|---|---|---|---|---|
| 1 | L00 name only | About this brush |  |  |  |  |
| 2 | L01 name only, no thumbnail | About this brush |  |  |  |  |
| 3 | L02 plotSpacing=0.1 | Stroke path: Spacing |  |  |  |  |
| 4 | L03 plotSpacing=0.25 | Stroke path: Spacing |  |  |  |  |
| 5 | L04 plotSpacing=0.5 | Stroke path: Spacing |  |  |  |  |
| 6 | L05 plotSpacing=1 | Stroke path: Spacing |  |  |  |  |
| 7 | L06 dynamicsRenderType=0 | Rendering: Render type |  |  |  |  |
| 8 | L07 dynamicsRenderType=1 | Rendering: Render type |  |  |  |  |
| 9 | L08 dynamicsRenderType=2 (the original's own value) | Rendering: Render type |  |  |  |  |
| 10 | L09 dynamicsRenderType=3 | Rendering: Render type |  |  |  |  |
| 11 | L10 blendMode=1 extendedBlend=1 | Rendering: Blend mode, Extended blend mode |  |  |  |  |
| 12 | L11 blendMode=3 extendedBlend=3 | Rendering: Blend mode, Extended blend mode |  |  |  |  |
| 13 | L12 blendMode=8 extendedBlend=8 (the original's own value) | Rendering: Blend mode, Extended blend mode |  |  |  |  |
| 14 | L13 textureMovement=0 | Grain: Movement |  |  |  |  |
| 15 | L14 textureMovement=1 | Grain: Movement |  |  |  |  |
| 16 | L15 textureZoom=0 | Grain: Zoom |  |  |  |  |
| 17 | L16 textureZoom=1 (the original's own value) | Grain: Zoom |  |  |  |  |
| 18 | L17 shapeRotation=-1 | Shape: Rotation |  |  |  |  |
| 19 | L18 shapeRotation=0 | Shape: Rotation |  |  |  |  |
| 20 | L19 shapeRotation=1 (the original's own value) | Shape: Rotation |  |  |  |  |
| 21 | L20 stamp=true | Properties: Stamp preview |  |  |  |  |
| 22 | L21 previewSize=0.1 | Properties: Preview size |  |  |  |  |
| 23 | L22 previewSize=0.6 | Properties: Preview size |  |  |  |  |
| 24 | L23 dynamicsPressureSizeCurve=4 points | Apple Pencil: Size response |  |  |  |  |
| 25 | M00 name only | About this brush |  |  |  |  |
| 26 | M01 rendering max=0 mod=0 rec=1 (the original's own value) | Rendering: Max transfer, Modulated transfer, Recursive mixing |  |  |  |  |
| 27 | M02 rendering max=0 mod=0 rec=0 | Rendering: Max transfer, Modulated transfer, Recursive mixing |  |  |  |  |
| 28 | M03 rendering max=1 mod=0 rec=0 | Rendering: Max transfer, Modulated transfer, Recursive mixing |  |  |  |  |
| 29 | M04 rendering max=1 mod=1 rec=0 | Rendering: Max transfer, Modulated transfer, Recursive mixing |  |  |  |  |
| 30 | M05 rendering max=0 mod=1 rec=1 | Rendering: Max transfer, Modulated transfer, Recursive mixing |  |  |  |  |
| 31 | M06 rendering max=0 mod=1 rec=0 | Rendering: Max transfer, Modulated transfer, Recursive mixing |  |  |  |  |
| 32 | M07 plotSpacing=0.25 plotSpacingVersion=0 | Stroke path: Spacing, Spacing version |  |  |  |  |
| 33 | M08 plotSpacing=0.25 plotSpacingVersion=1 | Stroke path: Spacing, Spacing version |  |  |  |  |
| 34 | M09 plotSpacing=1 plotSpacingVersion=0 | Stroke path: Spacing, Spacing version |  |  |  |  |
| 35 | M10 plotSpacing=1 plotSpacingVersion=1 | Stroke path: Spacing, Spacing version |  |  |  |  |
| 36 | M11 textureApplication=0 (the original's own value) | Grain: Grain behavior |  |  |  |  |
| 37 | M12 textureApplication=1 | Grain: Grain behavior |  |  |  |  |
| 38 | M13 grainBlendMode=7 | Grain: Grain blend mode |  |  |  |  |
| 39 | M14 grainBlendMode=10 | Grain: Grain blend mode |  |  |  |  |
| 40 | M15 grainBlendMode=27 | Grain: Grain blend mode |  |  |  |  |
| 41 | M16 shapeCount=0.0625 | Shape: Count |  |  |  |  |
| 42 | M17 shapeCount=0.5 | Shape: Count |  |  |  |  |
| 43 | M18 shapeAngle=1.5708 | Shape: Angle |  |  |  |  |
| 44 | M19 wetEdgesAmount=1 | Rendering: Wet edges |  |  |  |  |
| 45 | M20 burntEdgesAmount=1 | Rendering: Burnt edges |  |  |  |  |

"The original's own value" means the copy holds the value the original already had: it
shows what that value is called in Brush Studio.

## Step 5. Import ROSW 3 Scratch & Ünï 💧

Tap `ROSW-3-scratch.brushset`. The new set's name should read exactly **ROSW 3 Scratch & Ünï 💧**: an
ampersand, two accented letters and a water drop. Write down what it shows if it differs.

For each brush, the same three questions, and its own question:

| # | Name | Listed? | Preview? | Draws? |
|---|---|---|---|---|
| 1 | S1 M220 scratch |  |  |  |
| 2 | S2 M220 no thumbnail |  |  |  |
| 3 | S3 E4 scratch |  |  |  |
| 4 | S4 Wäßrige Tönung 水彩 |  |  |  |
| 5 | S5 bundled shape |  |  |  |
| 6 | S6 dual |  |  |  |

- **S1 M220 scratch.** Made from nothing in the current format (220 keys), with our own shape (a soft round dot), our own grain (an even speckle) and a preview picture we drew (an S-shaped stroke). Does it draw a soft round line? Does its preview in the list show our S-shaped stroke?
- **S2 M220 no thumbnail.** The same as S1 without a preview picture. In the list, is its preview empty, or did Procreate draw one itself?
- **S3 E4 scratch.** The same as S1, made in the older format (101 keys) instead. It starts from another real brush than S1 does, so its size and spacing may differ; the question is whether it opens and draws. If only one of S1 and S3 works, that decides which format new brushes are made in.
- **S4 Wäßrige Tönung 水彩.** Its name is `S4 Wäßrige Tönung 水彩` and ends in a space, which you will not see. Is the name shown with every accent and both Chinese characters? Its shape is twice as wide as it is tall (600 x 300) and its grain is large (2048 x 2048). Does it draw?
- **S5 bundled shape.** It carries no picture at all. It names a shape that comes with Procreate, `Brush-Preset-Soft.png`, as a Procreate 5 brush does, and no grain. Does it draw with that shape, as a plain line, or not at all?
- **S6 dual.** A dual brush: two brushes working as one, both made here (the second has a hard square shape). Tap it a second time to open Brush Studio. Does it show two brushes? Does it draw?

Leave Brush Studio with Cancel each time.

## Step 5b (optional, one tap). A loose brush file of ours

Even if both sets imported, tap `singles/S1-M220_scratch.brush` once. It is the brush
S1 M220 scratch again, as a single `.brush` file, and a loose brush file we wrote
is otherwise never tested. It lands in the set named "Imported". Note whether it
arrives and whether it draws, then delete it from "Imported".

### If a set does not import, or a brush is missing or will not draw

Open the files in `singles/` of that set one at a time: their names start with the
brush's code (L00, M03, S2 and so on). A single brush lands in the set named "Imported".
Note for each file whether it arrives and whether it draws. Start with L00, M00 and S1,
the plainest of each kind.

## Step 6. The return leg: share three things back

**a. ROSW 2 Edits.** In the Brush Library, tap the set name so that it is selected, then
tap it once more. A small menu appears: choose Share. Save the file to Files. It is saved
as a `.brushset` file. It shows what Procreate kept of each brush, the preview it draws
for each value, and how it writes these settings itself.

**b. ROSW 3 Scratch & Ünï 💧.** The same.

**c. One brand-new, untouched brush.** In the Brush Library, tap the **+** at the top
right. Brush Studio opens with a new brush. Change nothing, and tap Done. The new brush
is now in the list (it is usually called "Untitled Brush"). Swipe left on it, tap Share,
and save it to Files. It is saved as a `.brush` file. This is what Procreate itself
writes today, and it becomes the starting point for brushes this tool makes.

Keep the file names Procreate gives them.

## Step 7. Put the returned files here

Back on this computer, put the three files and your screenshots in:

    brushes/device-tests/sitting-2/returned/

(that is the `returned` folder beside this file). Add your notes there too: a
`notes.txt` with the versions and your answers, or photos of this page filled in.

What is in `returned/` is kept in git, together with `manifest.json` and this page: it
is the only record of what the iPad did, and no build can make it again.

Do not build this sitting again once files are in that folder: a new build gives the
brushes new folder names, and the returned files are compared with this one.

Afterwards you can delete both sets and the new brush from Procreate (swipe left, Delete).
