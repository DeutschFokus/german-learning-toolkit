# EP003 — Quality report

**He Cut Down the Oldest Tree on Earth** · 60.00 s · 9:16 · narration: the creator (pending — no AI voice in any deliverable)

## 1. Editorial scores (honest self-assessment, before your recording)

| # | Criterion | Score | Why |
|---|---|:-:|---|
| 1 | Opening hook | 9.5 | A true crime-story opening ("a student cut down the oldest known tree on Earth") with the crime visible in frame 0: the tree silhouetted against the moon, a red cut line at its base. |
| 2 | Storytelling & curiosity | 9.5 | The strongest arc of the three episodes: an act → the cost (4,844 rings) → why these trees are special → the survivor older than the Great Pyramid → why it's hidden → a loop line that turns the story into a moral. |
| 3 | Visual variety & quality | 8.5 | A new world for the channel (moonlit ridges, a procedural gnarled bristlecone, an eccentric tree-ring cross-section, a self-building pyramid, a secret grove). Still motion graphics, not photoreal; the carbon-dating graph is the plainest beat. |
| 4 | Voiceover quality | — | Pending your recording. The script is written for your deep, calm voice (123 words, every line with delivery notes). |
| 5 | Audio production | 8.0 | Wind, wood and stone tell the story (crack and fall on "down", ticks racing the ring counter, a pulse for the living strip, stone courses thudding as the pyramid rises). Measured, not heard. |
| 6 | Pacing & retention | 9.0 | 24 visual beats; the only silence is the deliberate 1.4 s after "they cut it down", filled by the fall. |
| 7 | Scientific & historical accuracy | 9.0 | Every on-screen claim is sourced (section 4); contested details (why he cut it, the exact ring count vs. age) are handled with neutral wording and the pinned-comment answers. The "can you blame them?" line is framed as the narrator's wink; the official reason (vandalism) is on screen. |
| 8 | Emotional impact | 9.5 | Regret, awe and protectiveness in 60 s — the most emotional of the three. |
| 9 | Shareability | 9.0 | "Older than the pyramids" + "its location is secret" is a strong send-to-a-friend combination. |
| 10 | Rewatch potential | 9.0 | The loop line completes the story; details reward a second look (the core sample, the 48 cm strip, the redacted forest). |

**Overall: 9.0 / 10 on the nine scored criteria.** Your voice decides the rest: a calm, grave read will lift the hook and the revelation further than anything visual.

## 2. Self-critique loop: what was revised

| Pass | Weakness found | Fix |
|---|---|---|
| Script timing | The first scratch read (0.86) left 5 s of dead air; 0.79 made the hook drag. | 0.83 plus larger pause growth (`pause_grow_max: 1.0`): narration fills 0.08–58.97 s at a calm, human-like pace. |
| Aligner | "bristlecone" wasn't in the alignment dictionary, so your take would have failed to align. | Script-level `lexicon` (ARPAbet) added to the engine. |
| Tree | The first procedural tree read as a tangle of sticks; the moon blew out to white. | The tree is rendered once as a solid silhouette with a single moonlit rim, parallel twisted grain and a root flare; the moon is a soft disc kept out of the bloom. |
| Cut scene | The APPROVED stamp overlapped the field-notes card. | Card fades out before the stamp lands. |
| Strip scene | A different tree than the hook, dead wood got darker instead of bleached, glow leaked under the ground line. | Same tree as the hook at 1.9×, dead wood bleaches silver on "die", tree clipped at the ground. |
| Time-lapse | Small pyramid, lots of empty sky. | Bigger pyramid and seedling, ground raised. |
| Docs (all episodes) | The voice notes in every script mentioned EP001's lines ("Tiny. / And you?"). | Generic wording; all three scripts regenerated. |

## 3. Verified technical checks

Measured with `python3 -m engine.verify`.

| Check | final_video_no_voice.mp4 | guide_record_along.mp4 |
|---|---|---|
| Duration | 60.000 s | 60.000 s |
| Frames | 1800 @ 30/1 fps | 1800 @ 30/1 fps |
| Resolution | 1080×1920, 9:16, H.264 High, yuv420p, BT.709 | same |
| Audio | AAC-LC 48 kHz stereo | same |
| File size / bitrate | 36.58 MB / 4.88 Mb/s | 33.95 MB / 4.53 Mb/s |
| Loudness | -24.7 LUFS (bed at its in-mix level) | -24.7 LUFS |
| True peak | -1.9 dBFS | -1.9 dBFS |
| Black ≥ 0.25 s / frozen ≥ 1.5 s / silence ≥ 1.2 s | no black · no frozen · no silence | no black · no frozen · no silence |
| Loop: first vs last frame (caption band excluded) | 0.99/255; 0.02 % > 24 | 1.67/255; 0.71 % > 24 |

Also checked:
- **Room for your voice:** with the scratch read in place, every line sits 9.1–15.3 dB above the bed (the bed ducks 8 dB wherever narration is expected; your take re-ducks to your actual timing).
- **Mix target:** the scratch mix masters at −14.0 LUFS / −1.6 dBTP, so your take will land on the same levels.
- **Alignment readiness:** all 123 script words are in the aligner's dictionary (with the bristlecone lexicon entry).
- **Visual QA:** about 30 look-dev stills plus the guide frames reviewed across every scene and the first/last frame.

## 4. Fact check

| Claim (where) | Status | Source |
|---|---|---|
| In 1964 a graduate student had the oldest known tree cut down (L01–L04) | ✔ Donald Currey, studying Ice Age glaciers on Wheeler Peak, Nevada; cut August 1964 with U.S. Forest Service permission | U.S. National Park Service, "The Prometheus Story" (Great Basin NP); Smithsonian Magazine; Live Science |
| He wasn't a vandal; he needed to count its rings (L02–L03) | ✔ research purposes; *why* a full cut was needed is disputed (stuck/broken borer is the most-told version) — the script avoids picking a version | NPS; Live Science |
| 4,844 rings (L05) | ✔ NPS count; a later count gave 4,862 and the age is estimated ≈ 4,900 years because harsh years can skip a ring (on screen) | NPS; secondary sources |
| Bristlecones survive by letting most of the tree die; this one lived through a single strip of bark ≈ 48 cm wide (L06–L07, on screen) | ✔ strip-bark growth; the specimen record for WPN-114 (Prometheus) lists bark on a single 19-inch (48 cm) strip | Great Basin NP / bristlecone literature |
| Their rings were used to correct carbon dating (L08) | ✔ Ferguson's bristlecone chronology → Suess's first radiocarbon calibration curve (1967) | Radiocarbon calibration literature (La Jolla measurements on Ferguson's dated wood) |
| Methuselah is still alive in California (L09) | ✔ White Mountains, Inyo National Forest, ~4,850 years | U.S. Forest Service coverage; Wikipedia summary |
| It was a seedling before the Great Pyramid was built (L10) | ✔ seeded c. 2833 BC; Great Pyramid c. 2560 BC (on screen: ≈ 270 years older) | as above |
| Its exact location is secret; the Forest Service won't say which tree (L11–L12) | ✔ unmarked and undisclosed to protect it from vandalism (on screen) | Forest Service policy as reported by multiple outlets |
| "Can you blame them? The last time we found the oldest tree…" (L13–L14) | Narrator's wink, not an official reason — the official reason is shown on screen | — |

## 5. Limitations

- **No narration yet.** The no-voice video and guide use a scratch timing only; the final deliverable is created from your take.
- **I could not listen.** The bed is verified by measurement (levels, margins, peaks), not by ear.
- **Procedural illustration:** the trees are stylized bristlecones, not portraits of Prometheus or Methuselah; the radiocarbon graph is schematic (shape and direction right, not plotted data).
- **Contested history** is worded neutrally (why the tree was cut; ring count vs. age).
- **Safe zones** follow the same conservative layout as EP001/EP002.
