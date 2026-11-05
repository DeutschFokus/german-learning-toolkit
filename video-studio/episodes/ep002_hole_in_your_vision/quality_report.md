# EP002 — Quality report

**There's a Hole in Your Vision Right Now** · 60.00 s · 9:16 · AI reference narration (same Kokoro-82M blend as EP001)

## 1. Editorial scores (honest self-assessment)

Editorial judgements after three review passes, not audience data. I cannot listen to audio, so voice and sound scores are capped.

| # | Criterion | Score | Why |
|---|---|:-:|---|
| 1 | Opening hook | 9.5 | A true, testable claim about the viewer's own eyes. Frame 0 already shows the headline (the O in HOLE is a glowing iris), the test card and a big glowing eye; narration starts at 0.08 s. The cover itself is the experiment. |
| 2 | Storytelling & curiosity | 9.5 | The viewer's own experience is the mystery (the dot vanished — why?). Then an explicit 1-of-4 → 4-of-4 structure (fill-in, darkness, blur, time) escalates toward the relatable reveal (the frozen second hand) and the thesis ("you're seeing an edit"). |
| 3 | Visual variety & quality | 8.5 | Eight distinct set-pieces (test card, eye anatomy, paint-in, editor timeline + blinking eye, reading saccades, film strip, clock, final cut) in the LUMEN look. Some mono labels are small on a phone; motion graphics, not cinematic 3D. |
| 4 | Voiceover quality | 7.5 (AI) | Same calm deep blend as EP001; all 144 words located by forced alignment. Not auditioned by ear; a human read will land the "gotcha" moments better. |
| 5 | Audio production | 8.0 | The sound is part of the idea: the music stutters on "edit", dips into darkness on each blink, zips with every eye jump, plays a whoosh backwards for "back in time", and the clock tick goes missing while the hand "freezes". Measured, not heard. |
| 6 | Pacing & retention | 9.0 | 25 visual beats; the only quiet moment is the deliberate 2.2 s try-it pause (animated ring + heartbeat). The 1/4 → 4/4 counter gives a reason to stay. 144 words is above the 115–135 guideline because the test needs instructions. |
| 7 | Scientific accuracy | 9.0 | Blind spot, blink suppression and saccadic omission are textbook. The narration states the backdating account of the stopped-clock illusion more simply than the literature (still debated); the hold is labeled exaggerated on screen and the debate is in the pinned-comment answers. |
| 8 | Emotional impact | 9.0 | The moment the dot vanishes is a genuine personal "whoa"; the clock is something almost everyone has noticed. |
| 9 | Shareability | 9.5 | "Try this" content gets sent to friends; the cover is the test. |
| 10 | Rewatch potential | 9.5 | The loop ends on the test card: a second try. Details for rewatchers (Mariotte, the BLINK clips, the 4-track final cut). |

**Overall: 8.9 / 10 with the AI voice** — still short of 9.5. The creator's own voice is the biggest available lift (projected ~9.3); the next is a listen on phone speakers to tune the stutter and blink dips by ear.

## 2. Self-critique loop: what was revised

| Pass | Weakness found | Fix |
|---|---|---|
| Script | First read was only 43.6 s of speech: ~6 s of dead air before the loop. | Added a real escalation step (blinks: "never see the darkness"), lengthened the try-it pause to 2.2 s, slowed the read to 0.88. |
| Hook frame | Test card alone looked sparse below the headline. | Big glowing eye under the card on the first and last frame; it fades before the test pause so nothing moves near the dot. |
| Test | Ambient dust drifting past the dot could spoil the effect. | Starfield dimmed and dust switched off while the test card is up. |
| Anatomy | Labels sat on top of the eyeball and the optic nerve. | Labels moved below the eye with clean leaders. |
| Saccades | "SMEARED" and "CUT" labels overlapped mid-crossfade; a ✂ glyph fell back to another font. | Sequential crossfade, text-only label. |
| Stretch | Film strip ran off the right edge (unsafe zone). | Strip resized to fit 104–976 px. |
| Pacing | 22–25 s ("not the only edit") left most of the frame empty. | "EDIT 1 OF 4" card + EDIT 2/4…4/4 progress chips. |
| Outro | Final-cut timeline text too small for a phone. | Bigger panel, all timeline fonts ×1.45. |
| Captions (engine) | Two caption chunks could overlap for up to 2 frames when words ran together (35 times here, 28 in EP001). | Engine fix: 0 overlaps; EP001 re-rendered too. |
| Robustness (engine) | A container restart interrupted a render. | Renders now write to `.partial.mp4` and only replace a deliverable when the encode finished. |
| Human-voice path | Under heavy compression the try-it pause could shrink below 1 s and break the test. | `"protect": true` on L04: that pause never goes below 1.4 s. |

## 3. Verified technical checks

Measured on the delivered files with `python3 -m engine.verify`.

| Check | final_video_ai_voice.mp4 | final_video_no_voice.mp4 |
|---|---|---|
| Duration | 60.000 s | 60.000 s |
| Frames | 1800 @ 30/1 fps | 1800 @ 30/1 fps |
| Resolution / aspect | 1080×1920, 9:16 | 1080×1920, 9:16 |
| Video codec | H.264 High, yuv420p, BT.709 tagged, +faststart | same |
| Audio | AAC-LC 48 kHz stereo | same |
| File size / bitrate | 36.14 MB / 4.82 Mb/s | 35.62 MB / 4.75 Mb/s |
| Integrated loudness | -14.0 LUFS | -27.3 LUFS (bed kept at its in-mix level) |
| True peak | -1.5 dBFS | -3.1 dBFS |
| Black segments ≥ 0.25 s | none | none |
| Frozen segments ≥ 1.5 s | none | none |
| Silences ≥ 1.2 s (< −50 dB) | none | none |
| Loop: first vs last frame (caption band excluded) | mean abs diff 0.99/255; 0.03 % of pixels differ > 24 | mean abs diff 1.0/255; 0.03 % of pixels differ > 24 |

Also checked:
- **Narration over bed:** 9.9–20.7 dB per line (pyloudnorm, pre-AAC).
- **Alignment:** all 144 spoken words located; 0 caption-chunk overlaps; `subtitles.srt` has 28 cues.
- **Blind-spot geometry:** + and dot are 780 px apart on the same row. On a 6.5–7.5 cm-wide phone screen that is 4.7–5.4 cm, which falls in the blind spot (≈ 13–18° temporal) at about 15–22 cm: hence the on-screen hint "usually about 15–25 cm".
- **Sync by construction:** the gaze hops, blink clips, clock ticks and their sounds are computed from the same cue times in `episode.py` and `sound.py` (3 hops/s; ticks silent between the glance and the end of "freeze").
- **Human-voice path:** dry run with a stand-in synthetic take reading the script in one 65.8 s take (55.3 s of speech, slower than the AI read; *not* a real human recording): all lines aligned, all 55 scene cues resolved, the edit fit exactly 60.0 s with the voice untouched, and the protected try-it pause held at 1.4 s.
- **Visual QA:** about 40 stills plus a 24-frame contact sheet of the final file reviewed (every scene, every transition, first/last frame).

## 4. Fact check

| Claim (where) | Status | Source |
|---|---|---|
| Each eye has a blind spot where the optic nerve leaves; no rods or cones there (L05) | ✔ | Standard anatomy; peer-reviewed article PMC8568268 (PubMed Central) |
| ≈ 6° × 7° of your view; first described by Mariotte in the 1660s (on screen) | ✔ (5.5–6° × 7–7.5°, centred ~15–16° temporal, ~1.5–2° below horizontal) | PMC8568268; Mariotte (1660s) |
| The brain fills the hole in; with both eyes open each eye covers the other's (L06, on screen) | ✔ | Perceptual filling-in literature (same article) |
| You blink about fifteen times a minute and don't see the darkness (L08) | ✔ resting rate ~10–25/min, average ~14–17; blink suppression is neural | Bentivoglio et al., Mov. Disord. 12, 1028 (1997); Volkmann, Riggs & Moore, Science 207, 900 (1980) |
| Your eyes jump about three times a second (L09) | ✔ typical (reading and scene viewing ~3–4/s) | Frontiers in Systems Neuroscience review (2015); standard eye-movement literature |
| Each jump would smear the image; the blur isn't perceived (L10) | ✔ saccadic omission / suppression | Campbell & Wurtz, Vision Res. 18, 1297 (1978); Idrees et al., Nat. Commun. (2020) |
| The gap is covered by stretching the next image back in time; the second hand seems to freeze (L11–L13) | ✔ phenomenon; mechanism simplified — backdating is the leading account, later studies add post-saccadic time dilation | Yarrow, Haggard, Heal, Brown & Rothwell, Nature 414, 302 (2001) and follow-ups |
| "You're not seeing the world live. You're seeing an edit." (L14) | Interpretation, consistent with the above (perception is reconstructed and partly delayed) | — |

## 5. Limitations

- **I could not listen.** Voice and mix are verified by measurement only. Listen once on phone speakers before posting.
- **The test depends on the device.** It is tuned for phones held about 15–25 cm away. On tablets or desktop monitors the + and dot are farther apart and the right distance changes; some eye conditions also change the result. The loop gives a second try.
- **144 spoken words**, above the 115–135 guideline: the try-it instructions cost ~25 words.
- **Exaggerations, labeled:** the clock's frozen hold is much longer than the real effect ("hold time exaggerated"); blink and saccade visuals are schematic.
- **Simplified mechanism:** the narration states the backdating explanation plainly; the literature still debates it.
- **AI voice stand-in** (Kokoro-82M, open weights, no voice cloning); label as synthetic where required.
- **Human-voice pipeline** was tested with a synthetic stand-in take, not a real recording.
- **No guarantee of virality.**
