# Notes for Claude

## YouTube scripts (`youtube-skripte/`)

German edutainment scripts for a faceless, image-only 16:9 YouTube channel. Topics must be halal.

- Script format: narration as `> ` quote lines (at least ~1,550 words per video), numbered scenes `**NN** · \`short image idea\``, then Shorts cut-downs, description and pinned comment. Export narration to `youtube-skripte/sprechertext/NN-*.txt`.
- **Image prompts: always deliver full, copy-paste-ready Copilot prompts** — style, the complete fixed description of every character in the scene, camera/light and rules — plus the character bible. Never deliver short prompts only.
  - Characters, styles and scene details live in `youtube-skripte/bildprompts/_generator/videos/vNN_*.py`.
  - Rebuild with `python3 youtube-skripte/bildprompts/_generator/build.py`. The generated `*-bildprompts.md` and `charakter-bibel.md` are never edited by hand.
  - Every character gets a signature (color, garment or object) that no one else in that video has.
- Image rules: no depiction of prophets or Sahaba, modest clothing, no blood or gore, no extremist symbols, no brand logos, no readable text. Real people are never named in a prompt; living or recent real people appear only from behind, in shadow, as silhouettes or as hands.
