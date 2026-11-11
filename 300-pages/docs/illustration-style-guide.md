# Illustration style guide

For illustrators and for AI image generation. One style for all six levels, twelve chapters per
level, about eight pictures per chapter. The briefs for every single picture are generated from
the content files:

```bash
python tools/image_briefs.py --level a2 --lang en > docs/image-briefs-a2.md
```

Until a picture exists, the book shows a calm placeholder in the chapter colours with the brief
printed on it. A placeholder is replaced by adding one line (`src:`) to the content file.

## 1 · What pictures are for

A picture in this book always has a job. It sets the scene of a dialogue, shows the words of a
vocabulary page, or gives learners something to talk about. If a picture could be removed
without a task getting harder, it should not be there.

- Show **one moment**, not a story in several steps.
- Show **the words of the page**. If the task teaches *der Teppich, das Regal, der Spiegel*, these
  three things are clearly visible and nothing else competes with them.
- Leave **room**. Learners write next to pictures; numbered pins sit on them.

## 2 · The look

Flat, warm, geometric. The pictures continue the language of the cover: large quiet shapes,
circles and arches, strong colour, no decoration.

| | Do | Don't |
| --- | --- | --- |
| Shapes | simple, rounded, built from circles, arches and rectangles | outlines, hatching, sketchy lines |
| Colour | flat fills, at most one darker tone for shadow | gradients, glow, glossy highlights |
| Surface | clean vector look | paper texture, grain, brush strokes |
| Space | 2–3 props that carry the vocabulary, one calm wall or floor area | full interiors, patterned wallpaper, clutter |
| Light | even, friendly, daytime unless the scene says otherwise | dramatic shadows, night scenes without reason |
| Depth | two layers: figures in front, shapes behind | perspective tricks, fisheye, tilted horizons |

Background shapes may be abstract: a circle can be the evening sun or a lamp, an arch a doorway
or a window. That keeps scenes light and ties every picture to the cover.

## 3 · Colour

Each chapter has its own palette, generated from the level colour (`series.yaml → colors.chapter`,
`levels/<level>.yaml → hue`). The image briefs list the exact values for every chapter:

| Token | Use in pictures |
| --- | --- |
| `mid` | the one strong colour of the picture: a sofa, a jacket, the sun |
| `hl` | second colour, large quiet areas |
| `soft`, `wash` | walls, floors, sky |
| `deep` | small dark details in the chapter hue |
| navy `#1B1E2F` | hair, shoes, the darkest details – instead of black |
| cream `#FBF4E6`, white | paper, light, windows |

Rules:

- A picture uses the chapter palette, navy, cream and white, plus the fixed colours of the
  characters (section 4). Nothing else.
- At most three strong colours per double page, pictures included.
- **Blue, pink and green are reserved.** In the text they mean *der*, *die* and *das*
  (`#005DCA`, `#BF1070`, `#007835`). Don't use these three as the main colour of an object whose
  word is taught on the same page. Mülltonnen are the exception: their real colours are the lesson.
- Meaning never depends on colour alone. Two bins are also different in shape or label position.

## 4 · The people

The same eight neighbours appear in every chapter and at every level. Their avatars in dialogues
are drawn by code (`engine/art.py`, colours in `series.yaml → cast`). Illustrations must match
them: same hair shape, same colours, same top.

| Character | Who | Always recognisable by | Top |
| --- | --- | --- | --- |
| **Elif Demir** | 27, nurse, new in Hanover | teal headscarf, small heart pin | teal scrubs |
| **Rahul** | 24, computer science student, Elif's best friend | black curls, round glasses | magenta hoodie |
| **David Berger** (Herr Berger) | 38, caretaker on the ground floor | tall and broad, moustache, key ring | orange work jacket |
| **Amina Diallo** (Frau Diallo) | 29, runs the property management | afro curls, colourful headband | ivory blazer |
| **Maria Lorenz** | 48, neighbour on the second floor | low bun with grey strands, apron | red |
| **Yusuf** | 33, craftsman, repair café | blue cap, dark beard, tool belt | denim blue |
| **Anna** | 25, student, friend from the German course | long wavy brown hair, hoop earrings, backpack | cream |
| **Herr Alvarez** | 52, landlord | grey swept-back hair, grey beard | slate blazer |

These eight come from the approved cast overview of 28 characters (`cast-overview.png`); the same
people appear in the videos. The character sheets made from that overview are the reference for
every picture. Avatars in dialogues are drawn by code from `series.yaml → cast` until portraits exist.

Faces are simple: dot eyes, eyebrows, a clear mouth shape, no eyelashes. Proportions are short and
friendly with slightly large heads, as in the cast overview. Hands are mittens with a thumb unless a hand holds something small.

People who are not part of the cast stay generic and in chapter colours.

## 5 · Formats

Pictures are cropped to their slot (`object-fit: cover`). Slots in the running text grow to fill
their page, so the visible height varies – compose for the tallest case and keep the subject in
the middle.

| Format | Slot in the book | Deliver | Keep in mind |
| --- | --- | --- | --- |
| `banner` | 216 × 96 mm, top of the chapter opener, bleeds off three edges | 2560 × 1140 px | the chapter numeral covers the lower left corner; faces stay in the right two thirds |
| `wide` | 117 mm × 58–85 mm | 1400 × 1010 px | subject in the middle 69 % of the height |
| `strip` | 117 mm × 37–63 mm | 1400 × 760 px | subject in the middle 58 % of the height |
| `tall` | 117 mm × 85–111 mm | 1400 × 1330 px | subject in the middle 76 % of the height |
| `square` | 63 × 63 mm | 900 × 900 px | fixed |
| pinned picture | fixed shape, see brief | see brief | every numbered object sits exactly under its pin |

JPEG, sRGB, quality about 82. Each file should stay under 250 KB: with roughly a hundred pictures
the finished book remains well below 40 MB.

**Picture dictionaries** carry numbered pins. The pin positions are part of the content file
(`markers`, in per cent from the top left). Either draw to the pins, or move the pins to the
drawing – but then change them in the content file, not in the picture.

## 6 · No writing in pictures

Pictures contain **no letters and no numbers**. Signs, screens, notes and labels are empty shapes
or a few neutral lines. Where a scene needs readable German – a door sign, a departure board –
the words are added afterwards as real type (Source Sans 3 Bold), so that they are spelled
correctly, stay sharp and can be changed.

No logos, no brands, no real people, no flags as decoration.

## 7 · Germany, drawn correctly

Learners will look for these things in real life. Get them right.

- **Rubbish:** blue bin = paper, yellow bin or yellow bag = packaging, brown bin = organic waste,
  grey or black bin = everything else. Glass goes into street containers for white, brown and
  green glass.
- **Houses:** staircase with letterboxes and a notice board, doorbell panel with name plates,
  radiators under the windows, windows that tilt and turn, a cellar with bicycles.
- **Streets:** bus and tram stops with a timetable case, cycle lanes, bakeries on corners.
- **People:** everyday clothes for the season. No folklore, no clichés – the cast is the Germany
  of today.

## 8 · Prompt template for image models

Generate the eight character sheets first (front view, three-quarter view, three expressions) and
use them as references for every scene. Keep the style paragraph identical for all pictures.

```text
Flat vector editorial illustration for a language course book.
STYLE: bold simple geometric shapes, no outlines, no gradients, no texture, flat colour with at
most one darker tone for shadows, rounded forms, circles and arches in the background, generous
empty areas, calm and friendly. Simple faces with two dot eyes and a small smile, natural adult
proportions.
PALETTE (use only these): {mid}, {hl}, {soft}, {wash}, {deep}, navy #1B1E2F, cream #FBF4E6, white,
plus the character colours below.
SCENE: {scene from the image brief, translated or in German}
CHARACTERS: {one line per character from the table in section 4}
COMPOSITION: {format note from the image brief}, subject in the middle, {aspect ratio}.
No text, no letters, no numbers, no logos, no watermark.
```

Negative prompt:

```text
photorealistic, 3D render, gradient, outline, line art, hatching, texture, grain, watercolour,
text, letters, numbers, typography, signage with writing, watermark, logo, brand, clutter,
busy background, dramatic lighting, lens effects, deformed hands, extra fingers
```

Example for `k5-auftakt`:

```text
SCENE: A young woman stands in her new, still empty living room holding a moving box. Large
window, evening light, rooftops outside. In the doorway an older man holds a potted plant.
CHARACTERS: Elif – 27, long dark brown hair, warm light brown skin, vermilion top.
Wolfgang Becker – 68, short grey hair and grey beard, fair skin, green top.
COMPOSITION: very wide banner 2.25 : 1, both figures in the right two thirds, lower left
corner empty wall.
```

## 9 · From picture to page

1. Save the picture as `assets/images/<level>/<id>.jpg` (the id is in the brief).
2. Add the path to the image in the content file:

   ```yaml
   image:
     id: k5-auftakt
     format: banner
     src: assets/images/a2/k5-auftakt.jpg     # ← new
     description: "…"                          # stays: it is the alternative text of last resort
     alt: {en: "…", tr: "…"}
   ```

3. Build with `--preview` and look at the page. Check the crop, the pins, and that nothing
   important sits under the chapter numeral.
4. Run through this list before a picture is final:
   - Are all taught words of the task visible, and only these in focus?
   - Do the characters match their table row – hair, skin, top?
   - Only palette colours? No reserved article colour on a taught object?
   - No letters, numbers, logos?
   - Under 250 KB?
