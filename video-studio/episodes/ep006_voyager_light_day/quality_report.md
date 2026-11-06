# EP006 — Quality report

**It Would Hear You Tomorrow** · 60.00 s · 9:16 · narration: the creator (pending — no AI voice in any deliverable)

## 1. Editorial scores (honest self-assessment, before your recording)

| # | Criterion | Score | Why |
|---|---|:-:|---|
| 1 | Opening hook | 9.5 | "SAY HELLO NOW, IT HEARS YOU TOMORROW" is personal, paradoxical and true. Frame 0 shows Voyager against the Milky Way with a "hello" riding the radio waves; within a second a countdown makes the day-long delay concrete. |
| 2 | Storytelling & curiosity | 9.5 | A clean arc: milestone (one light-day) → awe (a fridge bulb's power, still heard) → humility (the pale blue dot) → intimacy (a love story on the record) → eternity (40,000 years) → "still listening", which loops into the hook. |
| 3 | Visual variety & quality | 9.0 | A detailed 3D-projected Voyager (dish, gold bus, RTGs, booms, the record on its side), a Milky Way sky, a dawn launch, a solar-system light pulse with a racing clock, a bulb against a 70 m dish, the pale-blue-dot frame, a golden record with its engraved cover, brainwaves, a red dwarf. Procedural illustration throughout; the rocket and the dish are simpler than the hero shots. |
| 4 | Voiceover quality | — | Pending your recording. 123 words, delivery notes on every line, and pronunciations for Druyan, Sagan and the dates. |
| 5 | Audio production | 8.5 | A four-note radio "hello" motif that rides the waves and closes the loop; a clock racing to 24:00; a filament tink and mains hum; a camera shutter; vinyl crackle and an original music-box lullaby; a real heartbeat; a hum beating at ~10 Hz for her brainwaves. Measured, not heard. |
| 6 | Pacing & retention | 9.5 | 11 lines and 9 scenes, with a new visual event every 2–4 s. Pauses of 0.5–0.9 s are each filled by motion (pulse, turn, flip, orbit); the loop gap is 0.6 s. |
| 7 | Scientific & historical accuracy | 9.5 | The date and distance come from NASA. Power, the photo, the record's contents and the star flyby are sourced (section 4). Two details I couldn't verify (Druyan's job title, the wedding year) are left out. The love-story wording follows Druyan's own account. |
| 8 | Emotional impact | 9.5 | The turn at 38 s (her brainwaves, days after falling in love) lands on a space story nobody expects to be romantic. "Still carrying their love story" and "still listening" close it gently. |
| 9 | Shareability | 9.5 | A real news peg (Nov 18, 2026), a quotable hook ("it hears you tomorrow") and a love story. These are the three things people forward. |
| 10 | Rewatch potential | 9.5 | A perfect loop (last frame = frame 0; "it's still listening" → "if you said hello…"). Details reward a second look: the "hello" riding the waves, the record on the bus, the 0.12-pixel Earth, the two stars. |

**Overall: 9.3 / 10 on the nine scored criteria**, level with EP005. Your read can push it further: a quiet, close "tomorrow" and "still listening" are worth more than any effect. Post it in the days before November 18 (see the publishing kit).

## 2. Self-critique loop: what was revised

| Pass | Weakness found | Fix |
|---|---|---|
| Voyager pose | The first pose showed only the dish; the iconic gold bus was hidden; the magnetometer boom looked like a third leg. | Re-posed like NASA's classic illustration (dish tilted up, bus beneath, booms out to the sides); boom re-aimed. |
| Hook waves | Thin arcs read as random lines. | Wave packets (three crests) from the Sun's glint, with a "hello" riding each wave. |
| Launch | The rocket flew straight through the "1977" title. | Rocket and tower moved right, titles on the left. |
| Star scene | "+40,000 YEARS" overlapped "STILL CARRYING THEIR LOVE STORY"; the Gliese label was lost in the glare. | One title at a time; Gliese label moved to a clear spot with a shadow. |
| Layout vs captions | The DSN label and the "CARL SAGAN" name sat in the caption band; the milestone label collided with "THE SUN". | Lifted above the captions; milestone label moved next to Voyager. |
| Mix | The launch roar left only 5.5 dB between the voice and the bed on "Voyager 1 left Earth in 1977". | Launch trimmed relative to the other SFX (the SFX bus is loudness-normalised as a whole); lowest margin now 9.9 dB. |

## 3. Verified technical checks

Measured with `python3 -m engine.verify`.

| Check | final_video_no_voice.mp4 | guide_record_along.mp4 |
|---|---|---|
| Duration | 60.000 s | 60.000 s |
| Frames | 1800 @ 30/1 fps | 1800 @ 30/1 fps |
| Resolution | 1080×1920, 9:16, H.264 High, yuv420p, BT.709 | same |
| Audio | AAC-LC 48 kHz stereo | same |
| File size / bitrate | 40.49 MB / 5.40 Mb/s | 38.90 MB / 5.19 Mb/s |
| Loudness | -25.7 LUFS (bed at its in-mix level) | -25.7 LUFS |
| True peak | -2.7 dBFS | -2.7 dBFS |
| Black ≥ 0.25 s / frozen ≥ 1.5 s / silence ≥ 1.2 s | no black · no frozen · no silence | no black · no frozen · no silence |
| Loop: first vs last frame (caption band excluded) | 1.34/255; 0.38 % > 24 | 2.15/255; 1.18 % > 24 (teleprompter text differs) |

Also checked:
- **Loop seam in-engine:** last frame → first frame differs exactly as much as two neighbouring frames (1.36 vs 1.36 mean).
- **Room for your voice:** with the scratch read in place, every line sits 9.9–14.7 dB above the bed. The bed ducks 8 dB wherever narration is expected, and your take re-ducks to your actual timing.
- **Mix target:** the scratch mix masters at −14.0 LUFS / −1.4 dBTP.
- **Replacement pipeline dry run:** a stand-in take (a different stock voice, one continuous read with irregular pauses and room noise) went through `build_human`. It fit without compressing any pause, every cue followed its words (stills reviewed), and the mix landed at −14.0 LUFS / −1.9 dBTP.
- **Alignment readiness:** all 123 script words are in the aligner's dictionary (lexicon entries: "brainwaves", "druyan").
- **Visual QA:** about 45 look-dev stills across every scene, the dry run and the loop seam, plus a contact sheet of the encoded guide video.

## 4. Fact check

| Claim (where) | Status | Source |
|---|---|---|
| A hello sent now would arrive tomorrow (L01) | ✔ From Nov 18, 2026 the one-way light time is 24 h, and it grows ~30 min a year at ~17 km/s | NASA milestone announcement (June 2026) |
| Voyager 1 left Earth in 1977; "SEPT 5 · CAPE CANAVERAL" (L02) | ✔ Launched 5 September 1977 from Cape Canaveral on a Titan IIIE-Centaur | NASA/JPL mission history |
| On November 18, 2026 it crosses a full light-day; 25.9 billion km (L03) | ✔ NASA: 12:16:07 a.m. CST on Nov 18, 2026; the first human-made object at that distance | NASA (June 17, 2026), as reported by EarthSky and IFLScience |
| It still calls home on about the power of a fridge light bulb; "≈ 22 W" (L04) | ✔ The transmitter puts out about 22–23 W; JPL uses the fridge-bulb comparison | JPL |
| 70 m Deep Space Network dishes (on screen) | ✔ The DSN's largest antennas are 70 m | NASA DSN |
| In 1990 it turned around and took a photo of us: a pale blue dot; "FEB 14, 1990 · 6 billion km · 0.12 pixel" (L05) | ✔ 14 February 1990, from about 6 billion km, at Carl Sagan's urging; Earth is about 0.12 pixel | NASA, "Voyager 1's Pale Blue Dot"; JPL Photojournal |
| It carries a golden record, for whoever finds it (L06) | ✔ Contents chosen to represent life on Earth for any finder | NASA; Wikipedia summary |
| Music, greetings in 55 languages, a heartbeat; "90 MIN · 115 images" (L07) | ✔ 90 minutes of music, 55 languages, 115 images, a sounds-of-Earth montage including a heartbeat | Smithsonian; NASA |
| The brainwaves of a woman who had just fallen in love; "June 1977 · two days after they decided to marry" (L08) | ✔ An hour of Ann Druyan's EEG, recorded 3 June 1977, two days after she and Sagan agreed to marry; compressed to about a minute on the record | Druyan's account (quoted in phys.org 2011 and others); Wikipedia |
| Carl Sagan led the project; "chaired the committee that chose its contents" (L09) | ✔ The contents were selected by a committee chaired by Sagan | NASA; Wikipedia |
| In 40,000 years it will drift past another star; "Gliese 445 · within 1.6 light-years" (L10) | ✔ About 40,000 years; 1.6 light-years from Gliese 445 (AC +79 3888) | NASA Voyager mission pages |
| It's still listening; "receiving commands" (L11) | ✔ Commands still reach it (they take ~23 h in 2026); two science instruments remain on | NASA Voyager blog (April 2026) |

Left out on purpose: Druyan's job title on the project and the year of the wedding (not verified in this pass). The publishing kit says only that they married and stayed together until Sagan's death in 1996.

## 5. Limitations

- **No narration yet.** The no-voice video and the guide use a scratch timing only; the final deliverable is created from your take.
- **I could not listen.** The bed is verified by measurement (levels, margins, peaks), not by ear.
- **Illustrative, not footage:** Voyager, the launch, the record and the pale-blue-dot frame are recreations, not NASA images. No real person's likeness is shown; the people appear only as names.
- **Time-sensitive wording:** "On November 18, 2026, it crosses…" is accurate before and after the date; the countdown in the hook is illustrative (exact from the 18th).
- **Safe zones** follow the same conservative layout as earlier episodes; the guide's teleprompter band overlaps the top headlines (guide only, never published).
