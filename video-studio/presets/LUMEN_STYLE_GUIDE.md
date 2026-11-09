# LUMEN — channel style guide

The recurring identity for every episode. The code source of truth is `engine/gfx.py` (`Look`), `engine/captions.py`, `engine/postfx.py` and `engine/audio.py`; this page explains the rules so new episodes stay on-brand without becoming a template.

## Visual identity

**World.** Deep-space navy, never pure black: vertical gradient `#03050c → #07102a → #020309` with a soft radial haze behind the subject, three parallax star layers and slow floating dust. Every ambient motion is periodic over the episode length so videos loop cleanly.

**Light, not paint.** Subjects are drawn as luminous line art (hologram figures, wireframe grids, dotted planets) with a bloom pass. Only things that *emit* go into the glow layer; text mostly does not.

**Colour semantics (keep them consistent across episodes):**

| Token | Hex | Meaning |
|---|---|---|
| CYAN | `#55e6ff` | fast, up, signal, "the surprising part" |
| AMBER | `#ffb347` | slow, heavy, gravity, deep |
| CORE | `#ff7a2f` | heat, the interior of things |
| WHITE | `#f3f6ff` | text, primary forms |
| DIM | `#7d8db0` | labels, units, footnotes |
| MAGENTA | `#ff4f8b` | error, wrong guess, warning |
| MINT | `#62ffb5` | confirmed, measured, corrected |

**Type.** Inter Display Black for claims and numbers that must hit; Inter SemiBold/Medium for sentences; JetBrains Mono (ExtraBold for values, Regular with wide tracking for labels) for anything measured. Numbers roll like counters when they arrive.

**Grade.** Gentle S-curve, navy-lifted shadows, slightly warm highlights, elliptical vignette, fine animated grain (0.007) to stop banding without bloating the bitrate.

**Motion.** Ease-out expo/back for arrivals, ease-in cubic for exits, 0.18 s directional dissolves (incoming rises 80 px, outgoing lifts away), hard cuts when content continues across a boundary. One bespoke transition per episode at the emotional peak (EP001: the radial laser cut into the Earth, then the "sink" back to the viewer).

**Honesty in visuals.** Exaggerated visual rates get a small "spacing exaggerated / not to scale" label. Every on-screen number is real and sourced.

## Layout and safe zones (1080×1920)

- Keep critical content inside x 80–940 and y 230–1480.
- Top 230 px: platform tabs/status bar. Bottom 440 px: description, sound ticker, buttons. Right rail (x > 940, y 880–1500): like/comment/share icons.
- Captions centered at y = 1338. Key visuals live between y 250 and 1250.
- The first frame always shows the claim in type and the subject in image. No logo sting, no fade from black.

## Captions

Uppercase Inter Display Black, 76 px, dark 12 px outline + soft shadow, max 17 characters / 4 words per chunk, break on punctuation. Spoken words white, upcoming words 42 % opacity, the active word pops 10 %. Only the script's emphasis words take the accent colour of the scene. Skip captions when an on-screen headline already says the line.

## Sound conventions

- Fully synthesized, no samples or licences: `engine/audio.py`.
- Each episode gets a *musical idea tied to the topic* (EP001: two clocks ticking at 2.5 Hz and 2 Hz that drift in and out of phase).
- Harmony ends on a dominant that resolves into the opening chord, so the loop sounds like a cadence; tails past the end fold onto the start.
- One impact family per episode: sub boom (pitch-dropping sine + transient), shimmer, whoosh, riser, ping, chime. Hit on cuts and on the key number, never on every word.
- Mix: narration -17 LUFS pre-master, music bed -27 LUFS ducked 8 dB under speech, SFX -25 LUFS ducked 5 dB; master to -14 LUFS integrated, true peak ≤ -1.4 dBTP. Check that narration stays ≥ 8 dB above the bed on every line.

## Voice

The channel voice is the creator: deep, calm, intimate, intelligent, never a trailer voice. Deep does not mean slow: 165–175 wpm inside sentences, drama comes from pauses. Scripts mark emphasis (CAPS), pauses (/ // ///) and suspended pitch (…). The AI stand-in is a Kokoro-82M blend (am_michael 0.60 / am_onyx 0.25 / am_puck 0.15, speed 0.90, median F0 ≈ 104 Hz); it is never used to imitate the creator.

## Writing rules

- 115–135 spoken words. One claim, one mechanism, two or three escalating proofs, one personal payoff, one loop line.
- Every sentence earns a new visual. If a line only repeats what is on screen, cut it or change the visual.
- Real numbers with honest qualifiers ("about", "a few hundred"). Put the sources in the description.

## Content guidelines (the creator's values)

- No claims about human evolution or a shared origin of humans and apes, in scripts, on-screen text or pictures. Early people are described only as people of their time ("ein Mann der Kupferzeit"), never as "primitive" or half-animal, and never with "Steinzeitmensch"-style caveman clichés.
- Prefer formats that work without instrumental music when the creator asks for it (atmosphere and sound effects only).
- Pictures of people: from behind, in shadow or out of focus; an objects-and-places-only version on request.
