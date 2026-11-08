# Story video pipeline

Turns a narrated German story (script plus a handful of stills) into a finished 9:16 video for YouTube:
neural voiceover, original score, sound design, 2.5D camera moves with depth parallax, rain, lightning,
lamp flicker, karaoke subtitles in German with an English line, and a vocabulary moment with the channel
outro.

```
stories/der-brief/
  story.json      script lines, voices, subtitle chunks (German + English), vocabulary to highlight
  cues.py         creative direction: score, sound design, shot list (all timed from the voiceover)
  extended.json   vocabulary cards and outro for the long cut
  images/1-5.webp the stills
storyvid/          the engine (tts, timeline, music, sfx, mix, assets, render, text, extended, build)
fonts/             La Belle Aurore and Cormorant Garamond (SIL OFL)
```

## Setup

```bash
apt-get install -y ffmpeg fluidsynth musescore-general-soundfont
```

```bash
pip install edge-tts numpy scipy pillow opencv-contrib-python-headless onnxruntime mido pyloudnorm
```

Models (put them in one folder and pass it with `--models`):

- `depth_anything_v2_vitb.onnx` from github.com/fabio-sim/Depth-Anything-ONNX (release v2.0.0)
- `EDSR_x3.pb` from github.com/Saafke/EDSR_Tensorflow (models folder)

The voiceover uses Microsoft's Edge neural voices, so the machine needs access to `speech.platform.bing.com`.
The Inter font is expected in `/usr/share/fonts/opentype/inter` (Debian/Ubuntu package `fonts-inter`).

## Build

```bash
python -m storyvid.build stories/der-brief --work /tmp/der-brief --models /path/to/models --extended
```

Outputs in the work folder:

- `der-brief.mp4` – the story alone (2:09, fits YouTube Shorts) plus `der-brief.de.srt` / `.en.srt`
- `der-brief_lang.mp4` – story + Wortschatz cards + outro, with its own `.srt` files
- `stems/` – voice, music, ambience and effects as separate WAVs for re-editing

Preview single frames before a full render:

```bash
python -m storyvid.build stories/der-brief --work /tmp/der-brief --models /path/to/models --stills 2,14.3,52
```

Everything is cached (voice lines, depth maps, upscales), so re-runs after a tweak are quick. Add `--remix`
after changing the score or sound design.

## Making a new story

1. Copy `stories/der-brief`, replace the images and write `story.json`: one entry per narrated line,
   split into subtitle chunks of at most ~45 characters, each with its English translation. Lines can use a
   different voice (`lorenz`, `brother`) and `"fx": "phone"` gives a telephone sound.
2. Generate the voice once (`--stills 1`), then look up the timings in `<work>/tts_timing.json`.
3. Edit `cues.py`. Times are anchors such as `"L12.w8.start"` (word 8 of line L12) or `"L04.end+0.3"`, so
   music hits, knocks and camera moves stay in sync if a line is re-recorded.
   Camera keys use `cx`, `cy` (0–1 position in the image), `z` (zoom) and parallax (`px`, `py`, `dolly`).
4. Check stills, then render.

Mixing targets YouTube: -14 LUFS integrated, -1 dBFS peak, with the narration ducking music and rain so every
word stays clear.
