# EP004 — Quality report

**The Deepest Hole Ever Dug** · 60.00 s · 9:16 · narration: the creator (pending — no AI voice in any deliverable)

## 1. Editorial scores (honest self-assessment, before your recording)

| # | Criterion | Score | Why |
|---|---|:-:|---|
| 1 | Opening hook | 9.0 | Frame 0 is the strongest cover of the series so far (a small rusty lid in Arctic snow under the aurora, "12 KM" above it), and the absurd second line ("narrower than a dinner plate") pays off at 5 s with a plate covering the hole. Kola is a known internet topic, so some viewers arrive half-knowing it. |
| 2 | Storytelling & curiosity | 9.0 | Every depth breaks a prediction (fossils, no basalt, water, heat, soft rock), then two pull-backs re-frame it (deeper than the ocean → only 0.2 %), and the Voyager contrast turns the fact into a feeling. The middle is a list of depths by nature; the continuous dive keeps it from feeling like one. |
| 3 | Visual variety & quality | 9.0 | The most cinematic episode yet: one camera from the aurora to 12 km to the whole Earth and back, with motion blur on the dives, depth of field, heat haze, light rays, loop-safe aurora/snow/dust/embers, a magnifier, a glitching "predicted" layer, a to-scale chart and an iris transition. Still procedural motion graphics, not photoreal; the rock is painterly and the Voyager model is simple. |
| 4 | Voiceover quality | — | Pending your recording. Written for your deep, calm voice (127 words, delivery and pronunciation notes on every line). |
| 5 | Audio production | 8.0 | The score literally descends (D minor → B♭ → G minor → E♭), drops out at the bottom of the hole, lifts to F for the ocean and resolves on A7sus4 → D minor at the loop. Wind, diesel drive, a ping per kilometre, crackle, drips, heat roar, stone groans, impact, clank, telemetry. Measured, not heard. |
| 6 | Pacing & retention | 9.0 | 15 shots; a new visual event every 2–4 s; four dives act as a rhythm; no dead air (narration 0.08–59.40 s in the scratch timing). |
| 7 | Scientific & historical accuracy | 9.0 | Every on-screen number is sourced (section 4). Simplifications are labelled here: an illustrative cut-away, the hole drawn far wider than to scale inside the rock, "behaved like plastic" as the plain-language version of plastic deformation. |
| 8 | Emotional impact | 8.5 | Awe → humility ("0.2 %") → a quiet sting at the end. Less personal than EP003's human story. |
| 9 | Shareability | 9.0 | "Narrower than a dinner plate" and "0.2 % of the way" are quotable; the "Well to Hell" myth reliably pulls comments (ready answer in the kit). |
| 10 | Rewatch potential | 9.0 | Seamless loop (last frame = frame 0); details reward a second look (the fossils, the ruler's "NEVER REACHED", the fracture network, the 23 cm outline under the plate). |

**Overall: 8.8 / 10 on the nine scored criteria.** Your voice decides the rest: a calm read that lets "zero point two percent" land will do more than any effect.

## 2. Self-critique loop: what was revised

| Pass | Weakness found | Fix |
|---|---|---|
| Rock look | Candy-coloured stripes; fractures looked like sticks, then like worms; a detail layer turned the rock into TV static. | Narrow tint range, soft bed contacts, crystalline grain; fractures in three joint sets with wet, darkened halos and water glints; a subtle full-resolution grain layer. |
| Aurora | Drowned the headline; its ray texture wasn't periodic, so the sky jumped at the loop seam. | Lowered and dimmed below the headline; periodic ray texture. Seam now differs no more than any two neighbouring frames (1.51 vs 1.28 mean abs diff in-engine). |
| Sonar rings | A ring popped in at full strength on frame 0 of the loop. | Rings fade in at birth. |
| Zoom to the Earth | A reversed-range bug filled the screen with mantle orange and hid the ocean column and globe. | Fixed (fade driven by the negated log radius); the chart → globe pull-back is one continuous exponential zoom. |
| Transitions | UI text ignored scene transitions (a ghost "0.2 %" during the Earth→cap dissolve); the dissolve itself was muddy. | The UI layer now follows each transition; labels clear first; the globe rushes into the hole's marker and the surface opens in an iris (bloom cleared inside it). |
| Legibility | Captions over the white-hot core; "180 °C" orange on orange; small sub-labels. | Globe moved up and its core bloom reduced; white headline numbers with coloured glow and a soft dark scrim in the dive; larger sub-labels and ruler. |
| Snow | The snowfield read as flat grey fog. | Darker, colder palette and twinkling snow crystals. |
| Mix | The impact at the bottom landed on the spoken number (L09 only 7.5 dB above the bed). | The bit now hits bottom in the pause after "meters"; trimmed groans/roar/impact. Lowest line margin now 9.4 dB. |

## 3. Verified technical checks

Measured with `python3 -m engine.verify`.

| Check | final_video_no_voice.mp4 | guide_record_along.mp4 |
|---|---|---|
| Duration | 60.000 s | 60.000 s |
| Frames | 1800 @ 30/1 fps | 1800 @ 30/1 fps |
| Resolution | 1080×1920, 9:16, H.264 High, yuv420p, BT.709 | same |
| Audio | AAC-LC 48 kHz stereo | same |
| File size / bitrate | 47.59 MB / 6.35 Mb/s | 45.46 MB / 6.06 Mb/s |
| Loudness | -25.7 LUFS (bed at its in-mix level) | -25.7 LUFS |
| True peak | -4.8 dBFS | -4.8 dBFS |
| Black ≥ 0.25 s / frozen ≥ 1.5 s / silence ≥ 1.2 s | no black · no frozen · no silence | no black · no frozen · no silence |
| Loop: first vs last frame (caption band excluded) | 1.55/255; 0.16 % > 24 | 2.30/255; 0.91 % > 24 (teleprompter text differs) |

Also checked:
- **Room for your voice:** with the scratch read in place, every line sits 9.4–14.5 dB above the bed (the bed ducks 8 dB wherever narration is expected; your take re-ducks to your actual timing).
- **Mix target:** the scratch mix masters at −14.0 LUFS / −1.4 dBTP.
- **Replacement pipeline dry run:** a stand-in take (a different stock voice, deliberately slow: 57.2 s of speech) went through `build_human`: every line aligned, the edit re-timed to it (cues follow the words; stills reviewed), the mix landed at −14.0 LUFS / −2.0 dBTP. Because that read was so long, the pipeline compressed pauses below the script minimums and reported it, as designed. It never time-stretches.
- **Alignment readiness:** all 127 script words are in the aligner's dictionary (no lexicon entries needed).
- **Visual QA:** about 80 look-dev stills across every scene, the loop seam and the human-timeline dry run, plus a contact sheet of the encoded guide video.

## 4. Fact check

| Claim (where) | Status | Source |
|---|---|---|
| The deepest hole humans ever dug is 12 km deep (L01) | ✔ Kola Superdeep Borehole SG-3 reached 12,262 m in 1989; still the deepest by true vertical depth (some oil wells are longer but deviated; China's Shendi Take-1 reached 10,910 m vertical in Feb 2025) | Kozlovsky (ed.), *The Superdeep Well of the Kola Peninsula* (Springer 1987) and later summaries; CNPC via Offshore Technology (2025) |
| Narrower than a dinner plate; ⌀ 23 cm vs ≈ 27 cm (L02, on screen) | ✔ the borehole is about 23 cm (9 in) wide; dinner plates are about 25–28 cm | ZME Science, ScienceAlert summaries |
| 1970, Soviet scientists, aiming for 15 km (L03) | ✔ drilling began 24 May 1970 with a 15 km target | as above |
| Plankton microfossils at 6 km (L04) | ✔ microscopic plankton fossils reported at about 6 km | as above |
| At 7 km the predicted rock wasn't there; "NO BASALT AT 7 KM" (L05) | ✔ the expected granite-to-basalt transition was not found | as above |
| Cracked rock soaked with water (L06) | ✔ heavily fractured, water-saturated granite at depth | as above |
| 180 °C at the bottom, almost twice the ~100 °C expected (L07) | ✔ 180 °C vs about 100 °C predicted | as above |
| The rock got so soft the hole kept squeezing shut (L08) | ✔ in plain words: at that temperature the rock deformed plastically and the hole tended to close when the bit was pulled | as above (simplified wording) |
| 12,262 m, no further; reached 1989; "15 KM: NEVER REACHED" (L09) | ✔ closure dates differ by source (1992 to 2008), so none is shown | as above; ScienceAlert, WorldAtlas |
| Deeper than the deepest ocean; ≈ 10,935 m (L10) | ✔ Challenger Deep 10,935 ± 6 m (one recent estimate 10,984 m; Kola is deeper either way) | Greenaway et al. 2021 / NOAA |
| 0.2 % of the way to Earth's centre; 6,371 km (L11) | ✔ 12.262 ÷ 6,371 = 0.19 % | Earth's mean radius (IUGG) |
| Sealed under a rusty metal cap (L12) | ✔ the abandoned site's hole is covered by a welded metal cap | ZME Science, ScienceAlert |
| A spacecraft in interstellar space; "since 2012" (L13) | ✔ Voyager 1 crossed the heliopause in August 2012 | NASA/JPL |
| We've never gone deeper into our own planet (L14) | ✔ no hole is deeper by vertical depth; the deepest mines reach about 4 km | as above |

## 5. Limitations

- **No narration yet.** The no-voice video and the guide use a scratch timing only; the final deliverable is created from your take.
- **I could not listen.** The bed is verified by measurement (levels, margins, peaks), not by ear.
- **Illustrative, not documentary:** a painted cut-away. The borehole is drawn far wider than to scale inside the rock; the strata, fractures and fossils are stylised; depths, temperatures and ratios are true. The to-scale chart and the Earth's layer radii are drawn to real proportions.
- **Contested details are left out:** closure dates and the exact construction of today's cap vary by source.
- **File size** is higher than EP001–EP003 (~6.3 Mb/s) because the textured rock and particles carry more detail; well within platform limits.
- **Safe zones** follow the same conservative layout as EP001–EP003; the guide's teleprompter band overlaps the top headlines (guide only, never published).
