# Image prompts for Copilot — how to get consistent characters

Every scene of every script has a complete, copy-paste-ready prompt here. Each prompt already contains the video's style, the full fixed description of every character in that scene, camera/light and the rules. You never have to add anything — just copy, paste, download.

| Video | Prompt file | Scenes | Characters / recurring elements |
|---|---|---|---|
| 01 Mansa Musa | [01-mansa-musa-bildprompts.md](01-mansa-musa-bildprompts.md) | 49 | The King, The Old King, The Sultan, The Architect, The Librarian |
| 02 Adidas gegen Puma | [02-adidas-puma-bildprompts.md](02-adidas-puma-bildprompts.md) | 42 | Adi (3 ages), Rudolf (4 versions), Käthe, Friedl, Horst, Armin, the two factories |
| 03 Die Handy-Falle | [03-handy-falle-bildprompts.md](03-handy-falle-bildprompts.md) | 41 | The Visionary, Jonas, Lena, Markus, Maya |
| 04 Zeiss & die Chipmaschine | [04-zeiss-chipmaschine-bildprompts.md](04-zeiss-chipmaschine-bildprompts.md) | 40 | Anna, Heinrich |
| 05 Konstantinopel 1453 | [05-konstantinopel-1453-bildprompts.md](05-konstantinopel-1453-bildprompts.md) | 45 | The young Sultan, The Teacher, The Emperor, The Commander, The Cannon Master, The Patriarch |
| 06 Deutsche Bahn | [06-deutsche-bahn-bildprompts.md](06-deutsche-bahn-bildprompts.md) | 40 | Tobias (2 outfits), Helga, Werner, the German train, the Swiss train |
| 07 Der Döner | [07-doener-bildprompts.md](07-doener-bildprompts.md) | 37 | Ahmet (3 ages), Emre, Mert, The Pioneer (2 ages) |
| 08 Die Zuckerlüge | [08-zucker-luege-bildprompts.md](08-zucker-luege-bildprompts.md) | 39 | The American scientist, The British scientist (2 ages), The Executive, The Researcher, Sarah |

All characters with their explanations and reference sheet prompts in one place: [charakter-bibel.md](charakter-bibel.md).

## The workflow (per video)

1. **Open one new Copilot chat for the whole video** (copilot.microsoft.com or the Copilot app, signed in) and stay in it until the video is done. Copilot takes the earlier images of the same chat into account.
2. **Generate the reference sheets first.** In the prompt file, go to "Characters and recurring elements" and paste each "Reference sheet prompt". Regenerate until the sheet matches the description, then download it (name it like `01-KING-sheet.png`).
3. **Generate the scenes in order.** Paste each scene prompt and download the result as `01-03.png` (video 01, scene 03). The numbers match the scene numbers in the script.
4. **If a face or outfit drifts:** attach the saved reference sheet to your message and write "Use exactly the character from this reference sheet — same face, hair, beard and clothes." Then paste the scene prompt into the same message.
5. **Fix small mistakes by chatting, not by rewriting the prompt:** "Same image, but without the text on the sign." · "Same image in 16:9 widescreen." · "Same image, but his turban must be white with one golden-yellow band."

## Rules that keep the characters consistent

- **Never shorten or reword a character description.** The identical wording in every prompt is what keeps the face, hair and clothes stable.
- Every character has a signature (a color, a garment, an object) that no one else in that video has — for example the King's white-and-gold robe, Tobias's orange keychain or Anna's copper-red hair strand. If Copilot gets the face slightly wrong, the signature still makes the character recognizable. Check the signature before you accept an image.
- Don't type real names into Copilot. It refuses public figures or invents a different face. The prompts already describe everyone without names.
- Characters based on recent or living real people (The Librarian, The Visionary, The Pioneer, The Researcher, The British scientist) are deliberately shown only from behind, in profile in shadow, as a silhouette or as hands.

## Common problems

- **The image isn't 16:9:** reply "Same image in 16:9 widescreen", or extend the sides in your editor's AI expand tool.
- **Copilot refuses a scene** (most likely in the battle scenes of 05 or the war scenes of 02): reply "Make it calmer: no weapons in use, show the moment just before" or replace words like "soldiers" with "men in uniforms". Don't add names or real logos.
- **Text appears in the image** (signs, newspapers, screens): reply "Same image, remove all text and letters".
- **Shorts (9:16):** reply "Same image as a vertical 9:16 version, keep everything identical", or crop the 16:9 image in your editor.

## YouTube note

Turn on "altered or synthetic content" in YouTube Studio when realistic AI images show real events or real people.

## Changing or adding prompts

The prompt files and the bible are generated. Never edit them by hand — edit the matching file in `_generator/videos/` (style, characters, scene details) and run:

```bash
python3 youtube-skripte/bildprompts/_generator/build.py
```
