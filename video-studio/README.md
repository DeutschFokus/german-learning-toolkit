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
    postfx.py             bloom, grade, vignette, grain
    captions.py           word-synced burned-in captions + SRT export
    render.py             parallel frame renderer -> ffmpeg (H.264 High, BT.709, faststart)
    audio.py              synths, SFX, reverb, ducking, limiter, loudness mastering
  presets/LUMEN_STYLE_GUIDE.md
  episodes/ep001_head_older_than_feet/
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

That runs: AI narration and timeline (`voice`), score/SFX/mix (`audio`), `subtitles.srt` (`srt`), and both videos (`video`). A full 60 s render takes about 3–4 minutes per video on 4 CPU cores. To look at frames without rendering video:

```bash
python3 build.py stills 0,12.5,44.8
```

## Replace the AI voice with your own

1. Record the script in `human_voiceover_script.txt` in one take (WAV, 48 kHz, 24-bit, mono).
2. Run:

```bash
python3 build.py human /path/to/your_take.wav
```

The aligner finds every word of the script in your take, cuts it per line (10 ms fades, no time-stretching), lays the lines on the 60 s canvas by tightening or relaxing only the pauses, re-times every scene, caption and sound cue, ducks the music under *your* voice, masters to -14 LUFS, and renders `final_video_human_voice.mp4` plus `subtitles_human.srt`. If your read is too long even with minimum pauses, the build reports the overrun so you can trim a line; it never speeds your voice up.

## Make the next episode

1. Copy `episodes/ep001_head_older_than_feet` to a new folder.
2. Rewrite `production/script.json` (lines, pauses, emphasis, scene anchors).
3. Write new scenes in `episode.py` (reuse `Figure`, `DottedEarth`, `Limb`, `Fabric`, `ring_clock`, captions, transitions) and a new cue sheet in `sound.py` with a musical idea that belongs to the topic.
4. `python3 build.py all`, review stills/contact sheets, iterate, then write the quality report.

Keep the look and conventions in `presets/LUMEN_STYLE_GUIDE.md`; change the story, the hero visual and the bespoke transition every time.
