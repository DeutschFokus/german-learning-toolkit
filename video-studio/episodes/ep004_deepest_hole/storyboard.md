# EP004 — The Deepest Hole Ever Dug · Storyboard

9:16 · 1080×1920 · 30 fps · 60.00 s · LUMEN look · **narrated by the creator** (no AI voice in any deliverable)

Times below come from a *scratch* read that exists only to time the animation (`production/build/timeline_scratch.json`). Every animation, caption and sound cue is anchored to a line or a word, so when you run `build.py human your_take.wav` the whole edit re-times to your actual read.

## 1. Topic selection

After physics (EP001), perception (EP002) and a nature/history story (EP003), EP004 had one extra brief: **make it visually much more attractive**. So "how far can the camera travel?" counted twice. Twelve candidates, scored 1–10:

| # | Candidate | Curiosity | Novelty | Personal | Share | Visual (×2) | Evidence | Total |
|---|-----------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | **The deepest hole ever dug: 12 km down, narrower than a dinner plate, only 0.2 % of the way to Earth's centre (Kola)** | 9 | 7 | 6 | 9 | 10 | 9 | **60** |
| 2 | Atomic-bomb tests timestamped your cells (bomb-pulse dating) | 9 | 9 | 7 | 8 | 7 | 9 | 56 |
| 3 | In the age of dinosaurs a year had ~372 days | 10 | 9 | 6 | 9 | 7 | 8 | 56 |
| 4 | A radio message to Voyager 1 takes almost a day to arrive | 8 | 7 | 4 | 8 | 8 | 9 | 52 |
| 5 | Why no tree can grow taller than ~130 m | 8 | 7 | 3 | 7 | 9 | 8 | 51 |
| 6 | The Moon drifts 3.8 cm a year (Apollo laser mirrors) | 8 | 6 | 4 | 7 | 8 | 9 | 50 |
| 7 | Bacteria don't outnumber your cells 10:1 (it's about 1:1) | 8 | 7 | 8 | 7 | 5 | 9 | 49 |
| 8 | A blue whale's heart beats about twice a minute on a dive | 8 | 7 | 3 | 7 | 7 | 9 | 48 |
| 9 | Glass frogs hide their blood to turn transparent | 9 | 9 | 3 | 8 | 5 | 9 | 48 |
| 10 | The deepest humans have physically gone underground is ~4 km (gold mines) | 7 | 6 | 4 | 6 | 7 | 8 | 45 |
| 11 | Lightning is about 5× hotter than the Sun's surface | 7 | 3 | 4 | 7 | 7 | 9 | 44 |
| 12 | Tardigrades survive space | 7 | 3 | 3 | 7 | 5 | 8 | 38 |

**Winner: #1.** One continuous camera move carries the whole story: from the Arctic night (aurora, snow, a rusty lid in the ground) down a 12 km borehole through fossils, cracked wet granite and 180 °C rock, out to a to-scale ocean comparison, out again to the whole Earth (0.2 %), back to the lid, up to Voyager, and home to frame 0. It also has a twist structure (every depth broke a prediction) and a loop line that turns a fact into a feeling.

## 2. Story architecture

| Window | Job | What happens |
|---|---|---|
| 0–3 s | Hook | Frame 0: "12 KM / THE DEEPEST HOLE / EVER DUG" over a rusty steel cap in Arctic snow under the aurora, the abandoned station on the horizon, sonar pings rippling out of the cap. |
| 3–14 s | Mystery → the plan | Top-down into the hole: ⌀ 23 cm. A dinner plate slides over and covers it completely. 1970, Kola Peninsula: a derrick under the aurora starts drilling, aiming for 15 km (ruler with the target). |
| 14–37 s | Discoveries (one continuous dive) | 6 km: plankton microfossils (magnifier). 7 km: the predicted basalt layer glitches away — NOT THERE. Fractured granite lights up, soaked with water. The dive to the bottom: 180 °C vs ~100 °C expected; the rock behaved like plastic, the hole squeezes shut. |
| 37–49 s | Revelation | The bit hits 12,262 m (deepest human-made point, 1989; the 15 km target never reached). Pull back: to scale, deeper than the deepest ocean… pull back further: the whole Earth. 0.2 % of the way to the centre. |
| 49–60 s | Payoff + loop | Dive through the hole's marker into an iris: the cap today, sealed. Tilt up past the aurora to Voyager 1 in interstellar space; tilt back down to the cap; the headline returns line by line — the last frame is frame 0. |

## 3. Shot-by-shot timeline (scratch timing)

| # | Time | Line | Visual | Sound |
|---|---|---|---|---|
| 1 | 0.00–4.36 | L01 "The deepest hole humans ever dug is 12 kilometers deep." | Headline (no caption — the headline is the caption). Perspective Arctic night: aurora curtains (numpy-rendered, loop-safe), falling snow with depth, glinting snow crystals, the SG-3 buildings in silhouette, the rusty bolted cap on its concrete pad; amber sonar rings every 2.5 s; light rays from the aurora. "12 KM" pulses on "12". | Low boom, Arctic wind, sonar pings, D-minor pad. |
| 2 | 4.36–7.43 | L02 "And it's narrower than a dinner plate." | Dolly into the cap → top-down view straight down the shaft (rings receding and flowing outward, as if falling in). Cyan dimension: "THE BOREHOLE · 23 cm". On "dinner" a plate slides in and covers the hole; the hole's outline stays dashed on top: "DINNER PLATE ≈ 27 cm". | Falling whoosh; plate slide; a tiny porcelain clink. |
| 3 | 7.43–12.82 | L03 "In 1970, Soviet scientists started drilling, aiming for 15 kilometers." | Cut-away: aurora sky, snow lying on the surface, a lit derrick with volumetric light rays; rock cross-section below. "1970 · KOLA PENINSULA · USSR · SOVIET SUPERDEEP DRILLING PROJECT". On "drilling" the bit bites and the shaft starts; on "aiming" the depth ruler (0–15 km) draws in with "TARGET 15 KM" and a dashed planned path. | Diesel drive, grinding bit, a two-note blip on "15". B♭ pad, the falling four-note motif. |
| 4 | 12.82–15.2 | (end of L03 → L04 "At 6 kilometers…") | **The dive.** The camera drops 6 km in 2.3 s with motion blur, depth of field, parallax rock edges and drifting dust; the depth counter rolls to 6,000 m. | Long downward whoosh, rumble, a sonar ping for every kilometre, counter ticks, arrival thump. G-minor pad. |
| 5 | 15.2–18.84 | L04 "…fossils of microscopic plankton." | Microfossils glow in the rock; a magnifier pops: radiolarians and a diatom. "PLANKTON FOSSILS · MICROFOSSILS · 6 KM DOWN". | Shimmer and chime. |
| 6 | 18.84–22.6 | L05 "At 7, the rock they'd predicted simply wasn't there." | Short dive to 7 km. A hatched blueprint band "PREDICTED: BASALT" appears around the bit, then glitches apart into shards; stamp "NOT THERE · NO BASALT AT 7 KM". | Scan blips; glitch buzz and ticks; stamp. |
| 7 | 22.78–27.25 | L06 "Instead: cracked rock, soaked with water nobody expected." | Dive to 8.3 km. A scan line sweeps down and the fracture network lights up cyan: "FRACTURED GRANITE"; on "water" hundreds of glints twinkle along the cracks: "SOAKED WITH WATER". | Rock crackle; water drips and a trickle. |
| 8 | 27.25–32.6 | L07 "At the bottom: 180 degrees. Almost twice what they expected." | Dive to 11.7 km; the rock turns red-hot orange, heat haze ripples the picture, embers rise, the bit glows. "180 °C" counts up 100→180; "EXPECTED: ~100 °C" gets struck through on "twice"; "≈ 2×". | Heat roar and crackle, a pulse that quickens. E♭ pad, motif an octave lower. |
| 9 | 32.82–36.78 | L08 "The rock got so soft, the hole kept squeezing shut." | "ROCK BEHAVED LIKE PLASTIC" (wobbling); the borehole walls wave and pinch shut; the TEMPERATURE readout moves to the corner. | Two stone groans, rumble. |
| 10 | 36.78–42.48 | L09 "At 12,262 meters, they could go no further." | Final approach; "12,262 m" counts up with the read and slams when the bit hits bottom (in the pause after "meters"), with shake and chromatic aberration. "DEEPEST HUMAN-MADE POINT ON EARTH · REACHED IN 1989". On "further" the bit stops spinning, sparks die, and the ruler's unreached 12.3–15 km turns magenta: "NEVER REACHED". | Music drops out entirely; impact boom + steel clank; the drive winds down. |
| 11 | 42.48–45.0 | L10 "Deeper than the deepest ocean…" | Pull back until the rock column is a bar on a chart, TO SCALE; an ocean column pours in beside it: "≈ 10,935 m · DEEPEST OCEAN" vs "12,262 m · KOLA BOREHOLE", a dashed line marking the difference. | Reverse swell, pour; F-major lift, rising plucks. |
| 12 | 45.0–49.3 | L11 "…but just 0.2% of the way to Earth's center." | **Revelation.** One exponential pull-back from the chart to the whole Earth (true radius ratios for crust, mantle, outer and inner core); the surface line curves into the planet's limb. "0.2% · 12 km ÷ 6,371 km"; a cyan marker "THE HOLE"; a dashed radius "6,371 km TO THE CENTER". | Deep whoosh, sub boom, shimmer; D minor again (deflate). |
| 13 | 49.3–52.7 | L12 "Today, it's sealed under a rusty metal cap." | The globe rushes toward the marker; an iris opens out of it onto the Arctic surface. Card: "TODAY · KOLA SUPERDEEP BOREHOLE · SG-3 · KOLA PENINSULA, RUSSIA · SEALED"; a dashed amber ring draws around the cap. | Whoosh through, wind returns, steel clank on "sealed". B♭ pad. |
| 14 | 52.7–56.3 | L13 "We've sent a spacecraft into interstellar space…" | Tilt up past the aurora into deep sky (motion blur): Voyager 1 drifting on a dotted trail, "VOYAGER 1 · IN INTERSTELLAR SPACE SINCE 2012". | Rising whoosh, shimmer, telemetry blips; C-major lift. |
| 15 | 56.3–60.0 | L14 "…but we've never gone deeper into our own planet." | Tilt back down to the cap; the headline returns line by line; the last frame is frame 0. | Riser on A7sus4 → resolves to D minor at the loop; a sonar ping lines up with the first ripple. |

## 4. New in the engine for this episode (reusable)

- `engine/particles.py` — loop-safe snow / dust / embers with depth parallax; numpy aurora curtains with periodic ray texture.
- `engine/geo.py` — painted 14.6 km rock column (banded strata, jointed fracture sets with wet halos, water glints, crystalline grain, full-res detail layer, seamless parallax edge silhouettes, a squeezable borehole); drill rig, tricone bit, rusty bolted cap, snowfield with glints, dinner plate, microfossils, Voyager.
- `engine/postfx.py` — camera motion blur, tilt-shift depth of field, heat haze, volumetric light rays.

## 5. Captions and the record-along guide

- `final_video_no_voice.mp4`: picture + music + sound, no captions (they must follow your real read).
- `guide_record_along.mp4`: the same, plus burned-in captions and a teleprompter band at the top (current line, next line, a green count-in dot 0.6 s before each line). It's a pacing aid only: your take does **not** have to match it.
- After `build.py human`, `final_video_human_voice.mp4` gets word-synced captions from *your* voice and `subtitles.srt` is written from your take.
