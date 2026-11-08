# EP007 — Quality report

**There Are Seashells on Top of Everest** · 60.00 s · 9:16 · narration: the creator (pending — no AI voice in any deliverable) · first episode built on the creator's images as 2.5D photo plates

## 1. Editorial scores (honest self-assessment, before your recording)

| # | Criterion | Score | Why |
|---|---|:-:|---|
| 1 | Opening hook | 9.5 | "THERE ARE SEASHELLS UP HERE" over a photoreal summit at dawn: one line, instantly surprising, true. |
| 2 | Storytelling & curiosity | 9.5 | Fossils → an ancient sea → India's sprint → collision → 9 km rise → still rising → the 1924 mystery → the 2024 boot → the lost camera → "they stood on seashells", which loops into the hook. |
| 3 | Visual variety & quality | 9.5 | The biggest jump yet: eight photoreal images moving in 3D (depth parallax), plus a real-data globe, a collision shockwave, an altitude counter and labels that stick to the fossils. Images arrived at 941×1672 (chat size), so plates are upscaled ~1.4× and slightly soft. |
| 4 | Voiceover quality | — | Pending your recording. 128 words with delivery and pronunciation notes. |
| 5 | Audio production | 8.5 | Wind and spindrift, bubbles in the ancient sea, a riser and boom for the collision, film flutter for 1924, meltwater drips, a dry camera click, an original piano motif that returns at the loop. Measured, not heard. |
| 6 | Pacing & retention | 9.0 | 11 lines, 11 scenes, a new image every 4–6 s and a new graphic event every 1–3 s. The script is near the 60 s limit (pauses tightened in the scratch read). |
| 7 | Scientific & historical accuracy | 9.5 | All claims sourced (preproduction.md §4). Images checked: no fish or modern life in the Ordovician sea, no modern gear in 1924, no remains in the boot shot, no faces. "Seashells" is plain language for shelly fossil fragments (brachiopods). |
| 8 | Emotional impact | 9.0 | The turn at 36 s from geology to two men who vanished, the boot in the ice and the never-found camera. |
| 9 | Shareability | 9.5 | A quotable, counter-intuitive fact plus a famous unsolved mystery. |
| 10 | Rewatch potential | 9.5 | Perfect loop (last frame = frame 0; "…they stood on seashells" → "There are seashells…"). |

**Overall: 9.3 / 10 on the nine scored criteria**, level with EP005/EP006, with the visual score the highest so far. Bigger source images (2000×3500) would lift the sharpness further.

## 2. Self-critique loop: what was revised

| Pass | Weakness found | Fix |
|---|---|---|
| Depth plates | Thin "echo" outlines around subjects, smudgy fills in busy areas | Depth edge snapping, smooth depth past silhouettes, texture-preserving fill (engine/plates.py) |
| Titles | Gold/white titles weak on bright snow, sepia and ice | A soft dark scrim behind every top title |
| Globe | Speed bars overlapped the top of the globe | Globe moved down, bars above it |
| Name tag | "A.C. IRVINE" tag sat on the "2024" title | Moved beside the sock with a leader line |
| Fossil labels | Labels ran off the right edge | Centred under each ring |

## 3. Verified technical checks

Measured with `python3 -m engine.verify` on the first full render (the re-render only moved three labels):
- 60.000 s, 1800 frames @ 30 fps, 1080×1920, H.264 High, yuv420p, BT.709, AAC 48 kHz stereo.
- Bed loudness −26.4 LUFS, true peak −3.5 dBFS; scratch mix masters at −14.0 LUFS / −1.8 dBTP.
- No black (≥0.25 s), frozen (≥1.5 s) or silent (≥1.2 s) segments.
- Loop, first vs last frame: 1.64/255 mean difference (no-voice), 2.25/255 (guide, teleprompter differs).
- Visual QA: three rounds of stills across all scenes plus a contact sheet of the encoded video.

Not yet done: the per-line voice-over-bed margin check and the stand-in take dry run (done for EP004–EP006); they need your take or a stand-in.

## 4. Fact check

See `preproduction.md` §4 (all claims sourced). Re-check before publishing whether DNA confirmation of Irvine's identity has been announced; the script's wording is true either way.

## 5. Limitations

- No narration yet; the final video is created from your take.
- I could not listen; the sound is verified by measurement only.
- AI illustrations, not photographs: disclose them (YouTube "altered or synthetic content", TikTok AI label).
- The India drift is simplified (a block moving north on a modern globe), labelled by age only.
