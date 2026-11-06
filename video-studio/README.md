# LUMEN video studio

A small, fully local pipeline for 60-second vertical edutainment episodes (YouTube Shorts, TikTok, Instagram Reels, Facebook Reels): open-weights AI narration, original procedural motion graphics, synthesized score and sound design, word-synced captions, and a one-command swap to the creator's own voice.

Nothing here calls a paid API. The only downloads are the Kokoro TTS model files (Apache-2.0, fetched once from the kokoro-onnx GitHub release) and Python packages.

```
video-studio/
  engine/                 reusable library
    markup.py             script markup: {2010|twenty ten} = show "2010", say "twenty ten"
    tts.py                Kokoro-82M narration (offline once the model is cached)
    align.py              pocketsphinx forced alignment (offline, bundled model)
    timeline.py           narration -> timeline.json (AI or human), pause layout, lookups
    gfx.py                LUMEN look, easing, cairo canvas (base / glow / ui layers), shared props
    figure.py             hologram human figure
    props.py              dotted real-geography Earth, planet limb, satellite, phone, 3D grid, Earth cross-section
    anatomy.py            eye cross-section (retina, optic disc, nerve), blinking front-view eye, iris glyph
    ui.py                 instruction chips, editor timeline, film strip, analog clock, gaze reticle
    nature.py             procedural bristlecone (cached silhouette, cut/fall), ridges, moon, tree-ring section, pyramid, stamp
    geo.py                painted 14.6 km rock column (strata, fracture sets, water glints, parallax edges, squeezable borehole),
                          drill rig, tricone bit, rusty cap, snowfield, dinner plate, microfossils, Voyager
    particles.py          loop-safe snow / dust / embers with depth parallax, numpy aurora curtains
    volume.py             ray-marched volumetric mushroom cloud (puffs splatted into a 3D grid, self-shadowed, loop-safe)
    eye.py                photographic-style eye close-up (polar-space iris, lashes, lid shadow, corneal reflection slot)
    bio.py                real atmospheric carbon-14 record (+ clock morph), leaf, cell division, DNA helix, fat cells,
                          heart, brain, eye-lens growth shells, hologram silhouettes
    hud.py                crisp UI-layer text/lines/cards that follow scene transitions
    space.py              Milky Way sky, detailed 3D-projected Voyager, golden record, DSN dish, bulb,
                          pale-blue-dot frame, EEG/EKG traces
    data/                 c14_nh1_monthly.txt (Hua et al. 2022, Northern Hemisphere atmospheric 14C)
    plates.py             photo plates: local depth estimation (Depth Anything V2 Small) -> layered 2.5D camera
                          moves (push, orbit, dolly-zoom), hidden-background fill, titles tucked behind the subject
    postfx.py             bloom, light rays, motion blur, depth of field, heat haze, grade, vignette, grain
    captions.py           word-synced burned-in captions + SRT export
    render.py             parallel frame renderer -> ffmpeg (H.264 High, BT.709, faststart)
    audio.py              synths, SFX, reverb, ducking, limiter, loudness mastering, stutter/dip "edits"
    verify.py             technical QA of finished files (streams, loudness, black/frozen/silence, loop check)
  presets/LUMEN_STYLE_GUIDE.md
  episodes/ep001_head_older_than_feet/   "Your Head Is Older Than Your Feet" (gravity slows time)
  episodes/ep002_hole_in_your_vision/    "There's a Hole in Your Vision Right Now" (your brain edits reality)
  episodes/ep003_oldest_tree/            "He Cut Down the Oldest Tree on Earth" (creator-narrated: no AI voice)
  episodes/ep004_deepest_hole/           "The Deepest Hole Ever Dug" (creator-narrated: one continuous dive, 0 → 12 km → the whole Earth)
  episodes/ep005_bomb_timestamp/         "Nuclear Tests Left a Timestamp in Your Body" (creator-narrated: bomb-pulse dating of your cells)
  episodes/ep006_voyager_light_day/      "It Would Hear You Tomorrow" (creator-narrated: Voyager 1 one light-day away, Nov 18, 2026)
    final_video_ai_voice.mp4, final_video_no_voice.mp4, subtitles.srt,
    human_voiceover_script.txt, storyboard.md, publishing_kit.md, quality_report.md,
    thumbnail_cover.png
    production/           the editable project for this episode
      script.json         narration, pauses, emphasis, delivery and pronunciation notes, scene anchors
      episode.py          scene code (every animation anchored to line/word cues)
      sound.py            score + SFX cue sheet + mix
      build.py            orchestrator
      make_docs.py        generates human_voiceover_script.txt
      build/              timeline, narration, stems (music, SFX, processed voice)
```

## Setup

```bash
pip install -r video-studio/requirements.txt
```

FFmpeg with libx264 and the Inter / Inter Display / JetBrains Mono fonts must be installed (`fc-list | grep -i inter`). The Kokoro model files download automatically to `~/.cache/studio-models` on first use (override with `STUDIO_MODELS`).

## Build an episode

```bash
cd video-studio/episodes/ep001_head_older_than_feet/production
```

```bash
python3 build.py all
```

That runs: AI narration and timeline (`voice`), score/SFX/mix (`audio`), `subtitles.srt` (`srt`), and both videos (`video`). A full 60 s render takes about 3–4 minutes per video on 4 CPU cores. Renders write to a `.partial.mp4` first and only replace the deliverable when the encode finished. Check finished files with:

```bash
python3 -m engine.verify episodes/ep002_hole_in_your_vision/final_video_ai_voice.mp4
```

To look at frames without rendering video:

```bash
python3 build.py stills 0,12.5,44.8
```

## Replace the AI voice with your own

1. Record the script in `human_voiceover_script.txt` in one take (WAV, 48 kHz, 24-bit, mono).
2. Run:

```bash
python3 build.py human /path/to/your_take.wav
```

The aligner finds every word of the script in your take, cuts it per line (10 ms fades, no time-stretching), lays the lines on the 60 s canvas by tightening or relaxing only the pauses (long silences inside lines first, then the loop tail, then the gaps between lines — a line marked `"protect": true`, like EP002's try-it pause, keeps its minimum), re-times every scene, caption and sound cue, ducks the music under *your* voice, masters to -14 LUFS, and renders `final_video_human_voice.mp4` plus `subtitles_human.srt`. If your read is too long even with minimum pauses, the build reports the overrun so you can trim a line; it never speeds your voice up.

## Creator-narrated episodes (EP003 onward)

No AI voice ships. A scratch read (`build.py scratch`) only times the animation; `build.py video` then renders `final_video_no_voice.mp4` and `guide_record_along.mp4` (captions + a teleprompter band with the current line, the next line and a count-in dot). Record the script, run `build.py human your_take.wav`, and publish `final_video_human_voice.mp4` with the `subtitles.srt` written from your take. Words the aligner doesn't know go in the script's `"lexicon"` (ARPAbet), e.g. `"bristlecone": "B R IH S AH L K OW N"`.

## Camera and light effects (EP004 onward)

A scene can set these on the canvas and `postfx` applies them to the scene layers only (captions and HUD on the UI layer stay crisp):

- `cv.motion = (dx, dy)` — directional motion blur, pixels of travel during the shutter (use the camera's per-frame velocity × ~0.5).
- `cv.dof = (focus_y, band, sigma)` — tilt-shift depth of field: sharp around `focus_y`, softer toward the top and bottom.
- `cv.heat = (amount, y0, y1)` — heat shimmer growing from `y0` to `y1`.
- `cv.rays = (x, y, strength)` — volumetric light shafts from whatever glows, toward a light at (x, y).

Particles and the aurora take the video length as `loop`, so everything ambient completes whole cycles and the last frame flows into the first.

## Photo plates: your images as 3D camera moves (EP007 onward)

Any still (your own photo, licensed stock, public-domain NASA/ESA imagery, or an AI image) can become a moving shot. `engine/plates.py` estimates depth on this machine with Depth Anything V2 Small (Apache-2.0; ~99 MB, downloaded once to `~/.cache/lumen/models` and checksum-verified), splits the image into depth layers, fills what each layer hides, and renders a virtual camera move with real parallax. Titles can be slotted between layers, so the subject passes in front of the text.

Drop images in `episodes/<episode>/assets/` named by shot (`s01_hook.jpg`, `s02_…`). Best results: 9:16 portrait, at least 1080×1920 (ideally ~2000×3500), no text or watermarks, a clear subject with some distance to the background, nothing important in the bottom quarter (captions and platform buttons). Fine lattices, fences and hair are the hardest cases; keep those moves small.

Judge an image before using it (renders a 5 s move and a sheet: frame | depth | layers):

```bash
python3 -m engine.plates preview episodes/<episode>/assets/s01_hook.jpg --fx 0.4
```

In a scene:

```python
from engine.plates import Plate, Cam, blit, glow_from, rgba_layer
plate = Plate(ASSETS / "s01_hook.jpg", fx=0.4, cuts=[0.30, 0.40])   # cuts optional (auto)
cam = Cam(push=0.09 * x, orbit=(22 - 44 * x, -5 + 10 * x), focus=0.55)
img = plate.render(cam, inserts=[(2, title_rgba)])   # title behind layer 2 (the subject)
blit(cv, img); glow_from(cv, img)                     # then HUD, captions, particles as usual
```

`Cam`: `push` (dolly-in, near things grow faster), `zoom` (`vertigo_zoom()` for a dolly zoom), `orbit` (parallax around the `focus` depth), `pan`, `roll`. Keep orbit within about ±25 px and push within about 0.12 for clean edges.

## Make the next episode

1. Copy `episodes/ep001_head_older_than_feet` to a new folder.
2. Rewrite `production/script.json` (lines, pauses, emphasis, scene anchors).
3. Write new scenes in `episode.py` (reuse `Figure`, `DottedEarth`, `Limb`, `Fabric`, `ring_clock`, captions, transitions) and a new cue sheet in `sound.py` with a musical idea that belongs to the topic.
4. `python3 build.py all`, review stills/contact sheets, iterate, then write the quality report.

Keep the look and conventions in `presets/LUMEN_STYLE_GUIDE.md`; change the story, the hero visual and the bespoke transition every time.
