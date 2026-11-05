"""LUMEN studio engine: reusable pieces for 60-second vertical edutainment episodes.

markup    script markup ({display|spoken})
tts       Kokoro narration (open weights, offline)
align     pocketsphinx forced alignment (offline)
timeline  narration -> timeline.json (AI or human voice), lookups
gfx       cairo drawing helpers, easing, the LUMEN look
postfx    bloom, grade, vignette, grain
captions  word-synced captions + SRT
render    parallel frame renderer -> ffmpeg
audio     synths, SFX, score, mix and loudness
"""
