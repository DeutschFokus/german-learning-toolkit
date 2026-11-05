# EP001 — Quality report

**Your Head Is Older Than Your Feet** · 60.00 s · 9:16 · AI reference narration (Kokoro-82M blend)

## 1. Editorial scores (honest self-assessment)

These are my editorial judgements after four review passes, not audience data. Where I could not perceive something directly (I cannot listen to audio), the score is capped and says why.

| # | Criterion | Score | Why |
|---|---|:-:|---|
| 1 | Opening hook | 9.5 | The claim is counterintuitive, personal and literally true (NIST used the same line in 2010). Frame 0 already shows the full claim, the subject and both clocks; narration starts at 0.08 s with an impact under it. No logo, no fade-in. |
| 2 | Storytelling & curiosity | 9.0 | Claim → literal → mechanism → measured proof → everyday stakes → huge-scale revelation → back to you → loop. Each step raises the scale (ns → µs → years). The GPS "11 km" beat is the most abstract step. |
| 3 | Visual variety & quality | 8.5 | Eight distinct set-pieces in one coherent look, a new visual beat every 1.5–4 s, real continents, true-ratio Earth layers. It is premium motion design, not photoreal/cinematic 3D; the light/GPS screens carry a lot of small mono labels. |
| 4 | Voiceover quality | 7.5 (AI) | Natural-sounding open-weights voice blend, median pitch 104 Hz, calm pacing; every one of the 132 words was found by forced alignment. I could not listen to it, and TTS still lacks a human's micro-emphasis. Expected 9+ with the creator's own read. |
| 5 | Audio production | 8.0 | Original score with a real idea (two clocks drifting in and out of phase; A7sus4 → D-minor loop cadence), hits on the edits, measured mix. Not auditioned by ear. |
| 6 | Pacing & retention | 9.0 | 24 visual beats in 60 s, no silence over 1.2 s (measured), revelation at 44.6 s inside the 35–50 s window. |
| 7 | Scientific accuracy | 9.5 | Every claim checked against primary or reputable sources (section 4). Hedged where the science is hedged ("about", "a few hundred"); the 2.5-year figure is footnoted as a calculation; exaggerated tick spacing is labeled. |
| 8 | Emotional impact | 8.5 | Wonder plus a personal turn ("And you?") and a playful "Tiny. But real." Limited by the synthetic voice. |
| 9 | Shareability | 9.5 | A "tell someone tonight" fact with a built-in argument starter (gravity is zero at the center, so why is time slowest there?). |
| 10 | Rewatch potential | 9.0 | Seamless loop (last frame = first frame, last line completes with the first) and Easter eggs: Feynman's struck-out guess, 10.22999999543 MHz, the Hanover light under the figure's feet. |

**Overall: 8.8 / 10 with the AI voice.** That is below the 9.5 target, and I'd rather say so than round it up. The single biggest lift available is the creator's own voice (projected ~9.3 overall); the next is listening to the mix on phone speakers and adjusting the hit levels by ear.

## 2. Self-critique loop: what was revised

| Pass | Weakness found | Fix |
|---|---|---|
| Look-dev | The planet's atmosphere glow washed out "YOUR FEET"; the dotted planet was too sparse to read as Earth. | Pre-rendered limb with 140k-point real geography, thin rim light, outlined amber label. |
| Look-dev | Headline stack unbalanced (big gap above "YOUR FEET"). | Re-spaced IS / OLDER / THAN between head and feet. |
| Scene 2 | Gravity well too shallow, Earth and clocks tiny, title weak. | Deeper well, closer camera, larger Earth and clocks, big EINSTEIN name card. |
| Scene 3 | The tick-rate panel collided with the lifted clock; labels overlapped. | "2010" steps up out of the way, panel moved, labels re-placed. |
| Scene 6 | The core's glow swallowed the CENTER clock and labels; "2.5" overlapped "YEARS"; layer leader lines crossed. | Glow dims when the clocks arrive, dark clock face, measured text layout, labels level with their points on one ray. |
| Scene 7 | Lifetime counter dropped a digit. | Fixed formatting: +0.000 000 300 s. |
| Mix | Opening boom and the "down" hit masked narration (worst line only 5.1 dB above the bed). | Hits rebalanced and offset, SFX ducking deepened: every line now 8.1–20.7 dB above the bed. |
| Mix | True peak −0.92 dBTP. | Limiter ceiling lowered: −1.4 dBTP measured after AAC encoding. |
| Edit | Text-on-text dissolves looked muddy (EINSTEIN over the hook headline; legs over the Earth core). | 0.36 s directional dissolves, Einstein card delayed past the cut, bespoke "sink" transition from the core to the figure. |
| Delivery | First render was 122 MB at 16 Mbps (too big for GitHub and wasteful). | Grain 0.020 → 0.007, CRF 19, 12 Mbps cap: 39.9 MB at 5.3 Mbps, checked at 4× contrast for banding. |

## 3. Verified technical checks

Measured on the delivered files with `python3 -m engine.verify` (ffprobe + ffmpeg ebur128/blackdetect/freezedetect/silencedetect) unless noted.

| Check | final_video_ai_voice.mp4 | final_video_no_voice.mp4 |
|---|---|---|
| Duration | 60.000 s | 60.000 s |
| Frames | 1800 @ 30/1 fps | 1800 @ 30/1 fps |
| Resolution / aspect | 1080×1920, 9:16 | 1080×1920, 9:16 |
| Video codec | H.264 High, yuv420p, BT.709 tagged, +faststart | same |
| Audio | AAC-LC 48 kHz stereo, ~300 kb/s | same |
| File size / bitrate | 39.90 MB / 5.32 Mb/s | 39.49 MB / 5.26 Mb/s |
| Integrated loudness | −14.0 LUFS | −27.3 LUFS (bed kept at its in-mix level, so a voice dropped on top lands at ≈ −14) |
| True peak | −1.4 dBFS | −6.6 dBFS |
| Loudness range | 2.6 LU | 8.3 LU |
| Black segments ≥ 0.25 s | none | none |
| Frozen segments ≥ 1.5 s | none | none |
| Silences ≥ 1.2 s (< −50 dB) | none | none |
| Loop: first vs last frame (caption band excluded) | mean abs diff 1.78/255; 1.67 % of pixels differ > 24 | 1.78/255; 1.64 % |

Also checked:
- **Narration intelligibility proxy:** pocketsphinx forced alignment located all 132 spoken words of the AI read, line by line.
- **Voice choice:** pitch/voice-quality measured with Praat for 13 candidates; chosen blend median F0 104.5 Hz, 7.4 semitone range (not monotone), HNR 8.6 dB, no worse than the source voices.
- **Narration over bed:** 8.1–20.7 dB per line (pyloudnorm, pre-AAC).
- **Visual QA:** about 90 stills reviewed across look-dev and the final file (every scene, every transition, first/last frame); see section 2 for what changed.
- **Safe zones:** captions centered at y = 1338 with max width 800 px (x 140–940); claims and key numbers kept inside x 80–940, y 230–1480 by construction.
- **Captions vs speech:** caption words carry the aligner's word times; `subtitles.srt` has 28 cues built from the same times.
- **Human-voice pipeline:** two dry runs on a stand-in take (a different synthetic voice reading the whole script in one continuous 69.7 s take, slower than the AI read, with irregular pauses and room tone; *not* a real human recording). All 19 lines were located, 100 % of the speech energy landed inside the detected line spans, every line started on speech, word times stayed monotonic, the re-mix hit −14.0 LUFS / −1.6 dBTP, and the full video re-rendered with every scene following the new voice. The take holds 56.0 s of speech, more than the 54.5 s the script's minimum pauses allow: run 1 (before the fix) extended the video to 61.3 s rather than speed the voice up; run 2, after adding the fallback chain (shorten long in-line silences → shorter loop tail → compress between-line pauses toward 0.12 s), fit exactly 60.00 s with the voice untouched and the last frame still matching the first.

## 4. Fact check

| Claim (where) | Status | Source |
|---|---|---|
| Clocks closer to a mass run slower (gravitational time dilation), predicted by Einstein (L04–L05) | ✔ established physics | Einstein 1907/1911/1915; confirmed by Pound–Rebka 1959 onward |
| 2010: lifting an optical atomic clock 33 cm made it tick faster; shift ≈ 4 parts in 10¹⁷ (L06–L08, on screen) | ✔ measured | Chou, Hume, Rosenband, Wineland, *Optical Clocks and Relativity*, Science 329, 1630 (2010); NIST press release "NIST Clock Experiment Demonstrates That Your Head is Older Than Your Feet"; Physics World coverage |
| 33 cm ≈ two stairs (on screen) | ✔ typical riser 17–18 cm; NIST's own framing ("climbing a couple of steps") | NIST release |
| 2022: measured across just 1 mm (on screen, outro) | ✔ measured | Bothwell et al., *Resolving the gravitational redshift across a millimetre-scale atomic sample*, Nature 602, 420 (2022), JILA |
| GPS clocks gain about 38 µs/day vs. ground: +45 µs from weaker gravity, −7 µs from orbital speed (L10, on screen) | ✔ | Ashby, *Relativity in the Global Positioning System*, Living Rev. Relativ. 6, 1 (2003); Ohio State (Pogge) GPS & relativity notes |
| GPS orbit ≈ 20,200 km up (on screen) | ✔ | GPS.gov / Ashby 2003 |
| Light travels 11 km in that time (L11) | ✔ 299,792,458 m/s × 38 µs = 11.4 km (exact arithmetic) | — |
| Satellites are built to correct for it; clocks set to 10.22999999543 MHz before launch (L12, on screen) | ✔ | Ashby 2003 (10.23 MHz × (1 − 4.4647×10⁻¹⁰)) |
| The center of the Earth is about 2.5 years younger than its surface (L14) | ✔ as a calculation (theory, not a measurement) — footnoted on screen | Uggerhøj, Mikkelsen, Faye, *The young centre of the Earth*, Eur. J. Phys. 37, 035602 (2016) |
| Feynman's estimate was "a day or two" (on screen) | ✔ | Same paper, quoting Feynman's gravitation lectures |
| Over a lifetime your head gains "a few hundred billionths of a second" (L16) | ✔ computed: gh/c² × lifetime = 1.86×10⁻¹⁶ × 2.5×10⁹ s ≈ 470 ns standing 1.7 m for 80 years; sitting and sleeping lower it, hence "a few hundred". NIST: 90 ns for 33 cm over 79 years | NIST release; own arithmetic |
| Earth layer radii (visual) | ✔ outer core 3480 km (0.546 R), inner core 1220 km (0.192 R) | PREM (Dziewonski & Anderson 1981) |

Deliberately avoided: the popular "GPS would drift 10 km per day" claim (physicists dispute the framing); the script only states the exact light-travel arithmetic and that satellites are built to correct.

## 5. Limitations

- **I could not listen.** Voice and mix were verified by measurement only (alignment, pitch, HNR, LUFS, true peak, per-line margins, spectrogram review). Please listen once on phone speakers and on headphones before publishing.
- **AI narration is a stand-in.** Kokoro-82M (Apache-2.0), a blend of stock voices; no cloning of the creator's voice. The AI-voice file should be labeled as synthetic voice where platforms require it.
- **No AI image/video generation.** Connected generators (OpenArt, Cloudinary) consume paid credits, so they were not used without approval. All visuals are original procedural motion graphics; the pipeline can take stills or footage later.
- **Stylized rates.** The head and feet clocks tick at visibly different rates in the hook and in the gravity well; the real difference is ~10⁻¹⁶. The lab tick panel is labeled "spacing exaggerated"; the ring clocks are not labeled, as a visual metaphor.
- **The no-voice export has no burned-in captions** (they must follow the real recording); captions and `subtitles_human.srt` are regenerated from the creator's take.
- **Human-voice pipeline tested with a synthetic stand-in**, not a real human recording. Real takes with long breaths, mouth noise or ad-libs that differ from the script will need a clean read of the script as written (the aligner expects the script's words).
- **If a human read is longer than the canvas** even after tightening pauses, the build extends the video slightly and prints which lines to trim rather than speeding the voice up; exactly 60 s then needs a tighter read.
- **Safe zones** are conservative estimates of current Shorts/TikTok/Reels/FB UI; app updates can move overlays.
- **No guarantee of virality.** The piece is built for retention and sharing, but performance depends on the platform, timing and audience.
