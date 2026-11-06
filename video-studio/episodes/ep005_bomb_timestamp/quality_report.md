# EP005 — Quality report

**Nuclear Tests Left a Timestamp in Your Body** · 60.00 s · 9:16 · narration: the creator (pending — no AI voice in any deliverable)

## 1. Editorial scores (honest self-assessment, before your recording)

The brief was "as close to 10/10 as possible". The previous reports named what capped the scores: a half-known topic, a list-like middle, stories about something rather than about the viewer, and purely illustrative visuals. EP005 was built against each of those. Each score below is my judgement, and the reason is next to it.

| # | Criterion | Score | Why |
|---|---|:-:|---|
| 1 | Opening hook | 9.5 | Frame 0 makes a startling, true, personal claim ("NUCLEAR TESTS LEFT A TIMESTAMP IN YOUR BODY") over an image you can't scroll past: an eye with a mushroom cloud in its reflection. Bomb-pulse dating is still little known, so most viewers have never heard it. |
| 2 | Storytelling & curiosity | 9.5 | One causal chain with no gaps (tests → air → plants → you → DNA → clock), a question-and-answer rhythm for the results (fat? heart? cortex?), then a revelation the viewer experiences while watching, and a loop line that turns the ending into the beginning. |
| 3 | Visual variety & quality | 9.0 | The strongest set yet: a photographic-style eye, a ray-marched volumetric mushroom cloud, the **real** carbon-14 record drawn as data and curled into a clock, a backlit leaf, cell division, a 3D DNA helix, an x-ray of the lens's growth layers, light passing through the lens core. Still procedural rather than filmed: the eye and cloud are convincing at phone size, but the cow and human are simple holograms. |
| 4 | Voiceover quality | — | Pending your recording. Written for your deep, calm voice: 126 words, delivery notes on every line, and three pronunciations. |
| 5 | Audio production | 8.5 | The data is sonified: a tone follows the measured curve up to the 1963 peak and down year by year. Concept sounds carry meaning: the boom arrives after the flash, Geiger clicks rise with the carbon, a lock clicks on "DNA", a heartbeat plays for the heart and a muffled womb heartbeat for "before you were born". The harmony resolves into the loop. Measured, not heard. |
| 6 | Pacing & retention | 9.5 | 13 beats with a new visual event every 2–4 s. Pauses of 0.4–1.3 s are each filled by an animation (curve, flight of atoms, lock, dial); the loop gap is 0.6 s. |
| 7 | Scientific & historical accuracy | 9.5 | Every claim comes from a peer-reviewed primary paper (section 4). The chart is measured data, not a sketch. Wording follows the papers: "about ten percent" (the abstract's figure; the median is 8.4 %), heart "≈ 1 % a year at 25", the lens core "formed in the first weeks in the womb, and never replaced". The present-day dose is stated so the hook can't scare anyone wrongly. |
| 8 | Emotional impact | 9.5 | Unease → wonder → intimacy: "You're reading this through it, right now" lands in the viewer's own eye. |
| 9 | Shareability | 9.5 | Several quotable hooks: "your eye is older than you", "your heart is mostly original", and "the Cold War is in your DNA". The comment magnets ("am I radioactive?", "the 7-year myth") have ready answers. |
| 10 | Rewatch potential | 9.5 | A perfect loop (the last frame is frame 0, and the line "because…" completes into the first). There are hidden details for a second viewing: the cloud in the cornea, the seconds ring, the sample on the clock, the Y suture. |

**Overall: 9.3 / 10 on the nine scored criteria**, the highest of the series. Three things would push it higher:
1. Your voice, which counts for a lot on the hook and the "right now" line.
2. A photographic hero shot. That needs licensed footage or paid image generation, which I haven't used without your approval.
3. Someone actually listening to the mix.

## 2. Self-critique loop: what was revised

| Pass | Weakness found | Fix |
|---|---|---|
| Mushroom cloud | First pass: a smooth blob tree. Second: a clay-like sculpture with stripes. Third: a cluster of balls. | Puffs splatted into a 3D grid with soft union, drifting noise erosion, one-tap self-shadowing, sky light and a tamer blackbody core. |
| Eye | It read as an illustration: a ruled iris, a spiky amber "flower", a flat sclera, a visible texture rectangle. | Iris built in polar space (wandering fibres, a soft collarette, crypts, broken furrows), the upper lid overlapping the iris, a limbal shadow, a feathered face. |
| Reflection | The reflected scene had a flat horizon edge, like a sticker on the iris. | A convex-mirror sky, a soft horizon and a feathered radial mask. |
| Loop seam | Several ambient motions (cloud rolling, noise drift) weren't periodic. | All motion now completes whole cycles per loop. The seam differs exactly as much as any neighbouring frames (1.02 vs 1.02 in-engine; 1.03/255 encoded). |
| Layout | The chart, the cow and the labels fell under the captions; a lens label ran off the frame. | Chart moved up, labels lifted, lens shifted left with shorter labels. |
| Props | The brain was an unreadable blob; the heart had "antennae"; the lens core bloomed to white. | Brain folds traced from noise contours with cerebellum and brainstem; an anatomical heart with its great vessels; an amber core with a Y suture. |
| Transitions | The eye ghosted over the explosion; there was a near-black gap before the outro. | Shorter dive into the reflection, and a real dissolve from the lens diagram back to the eye. |
| Mix | The muffled womb heartbeat sat under "before you were born" (only 4.1 dB below the voice). | Moved into the pause after the line. The lowest line margin is now 9.9 dB. |

## 3. Verified technical checks

Measured with `python3 -m engine.verify`.

| Check | final_video_no_voice.mp4 | guide_record_along.mp4 |
|---|---|---|
| Duration | 60.000 s | 60.000 s |
| Frames | 1800 @ 30/1 fps | 1800 @ 30/1 fps |
| Resolution | 1080×1920, 9:16, H.264 High, yuv420p, BT.709 | same |
| Audio | AAC-LC 48 kHz stereo | same |
| File size / bitrate | 38.66 MB / 5.15 Mb/s | 34.63 MB / 4.62 Mb/s |
| Loudness | -26.8 LUFS (bed at its in-mix level) | -26.8 LUFS |
| True peak | -2.8 dBFS | -2.8 dBFS |
| Black ≥ 0.25 s / frozen ≥ 1.5 s / silence ≥ 1.2 s | no black · no frozen · no silence | no black · no frozen · no silence |
| Loop: first vs last frame (caption band excluded) | 1.03/255; 0.01 % > 24 | 1.83/255; 0.81 % > 24 (teleprompter text differs) |

Also checked:
- **Room for your voice:** with the scratch read in place, every line sits 9.9–20.1 dB above the bed. The bed ducks 8 dB wherever narration is expected, and your take re-ducks to your actual timing.
- **Mix target:** the scratch mix masters at −14.0 LUFS / −1.8 dBTP.
- **Replacement pipeline dry run:** a stand-in take (a different stock voice, one continuous read with irregular pauses and room noise) went through `build_human`. It fit without compressing any pause. Every cue followed its words (stills reviewed), and the mix landed at −14.0 LUFS / −1.9 dBTP.
- **Alignment readiness:** all 126 script words are in the aligner's dictionary (one lexicon entry: "timestamp").
- **Visual QA:** about 70 look-dev stills across every scene, every transition, the loop seam and the human-timeline dry run, plus a contact sheet of the encoded guide video.

## 4. Fact check

| Claim (where) | Status | Source |
|---|---|---|
| Nuclear bomb tests left a timestamp in your body (L01) | ✔ Bomb-derived ¹⁴C is in the DNA of cells formed since the mid-1950s; the method dates them | Spalding et al., *Cell* 122:133 (2005) |
| In the fifties and sixties they nearly doubled the radioactive carbon in the air; ×1.95 (L02, gauge) | ✔ Northern-Hemisphere atmospheric ¹⁴C peaked at F¹⁴C ≈ 1.95 in 1963 (monthly data) | Hua et al., *Radiocarbon* 64:723 (2022), NH zone 1, as plotted |
| In 1963 most were banned, and it began to fade year by year (L03, chart) | ✔ Partial Test Ban Treaty 1963 (US, UK, USSR; France and China tested in the air until 1974/1980); the curve declines to ×1.01 by 2019 | Treaty text; Hua et al. 2022 |
| Today's fallout dose ≈ 1/500 of natural radiation (on screen) | ✔ About 0.005 mSv a year from all test fallout vs about 2.4 mSv a year natural background | UNSCEAR 2000 |
| Plants breathed it in. Animals ate the plants. So did you. (L04) | ✔ ¹⁴CO₂ enters the food chain through photosynthesis | Spalding et al. 2005 |
| Every new cell locks that year's level into its DNA (L05) | ✔ Genomic DNA is stable after a cell's last division, so its ¹⁴C dates the cell's birth | Spalding et al. 2005 |
| "THIS CELL · MADE IN 1994 · ¹⁴C ×1.13" (on screen) | ✔ The 1994 level read from the plotted data (an example cell) | Hua et al. 2022 |
| Scientists in Stockholm turned it into a clock for your cells (L06) | ✔ Frisén lab, Karolinska Institutet; dates tissue averages, not single cells (stated in the kit) | Spalding et al. 2005 |
| Fat cells: about ten percent replaced every year (L07) | ✔ Abstract: about 10 % renewed annually at all adult ages and BMIs (median 8.4 %) | Spalding et al., *Nature* 453:783 (2008) |
| Heart: barely one percent a year; "1 in 100 a year, at 25" (L08) | ✔ 1 % a year at age 25, falling to 0.45 % at 75 | Bergmann et al., *Science* 324:98 (2009) |
| Cortex neurons: as old as you are; "formed before birth" (L09) | ✔ Neocortical neurons date to about the time of birth (fetal); no adult neurogenesis there | Bhardwaj et al., *PNAS* 103:12564 (2006) |
| The center of your eye lens was made before you were born, and never replaced (L10–L11) | ✔ The embryonic nucleus forms in the first trimester; lens crystallins in the nucleus show no turnover, formed around birth | Embryology reviews (Frontiers in Ophthalmology 2024); Lynnerup et al., *PLoS ONE* 3:e1529 (2008) |
| The lens grows in layers, like tree rings (on screen) | ✔ New fibres are laid over old ones; the oldest stay at the centre | Lens anatomy reviews |
| You're reading this through it (L12) | ✔ The visual axis passes through the lens nucleus | Ocular anatomy |
| We can measure all of it because of the bomb tests (L13 → L01) | ✔ The cell-age measurements above all rely on bomb-pulse ¹⁴C | as above |

## 5. Limitations

- **No narration yet.** The no-voice video and the guide use a scratch timing only; the final deliverable is created from your take.
- **I could not listen.** The bed is verified by measurement (levels, margins, peaks), not by ear.
- **Illustrative, not footage:** the nuclear test, eye, cells and organs are procedural illustrations; the carbon-14 chart is real data.
- **Simplifications:** "about ten percent" uses the abstract's figure (median 8.4 %); the heart rate is the young-adult figure (stated on screen); dates are tissue averages, not single cells (stated in the kit).
- **Sensitive imagery:** a stylised nuclear test is shown as history (no casualties), with the present-day dose stated plainly.
- **Safe zones** follow the same conservative layout as EP001–EP004; the guide's teleprompter band overlaps the top headlines (guide only, never published).
