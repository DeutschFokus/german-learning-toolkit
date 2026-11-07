#!/usr/bin/env python3
"""Build Copilot-ready image prompts and the character bible.

Source of truth:
  * the scripts (../../0X-*.md) for scene numbers, short image ideas and narration
  * videos/vXX_*.py for style, characters and per-scene prompt details

Every character description is written ONCE in the video module and pasted
verbatim into every prompt that uses it. Never edit the generated .md files by
hand - edit the module and run:  python3 build.py
"""
import importlib.util
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SCRIPTS_DIR = HERE.parents[1]          # youtube-skripte/
OUT_DIR = HERE.parent                  # youtube-skripte/bildprompts/
VIDEOS_DIR = HERE / "videos"

MAX_PROMPT_CHARS = 3800  # keep well below Copilot's message limit

GLOBAL_RULES = (
    "No text, letters, numbers, captions, labels, logos or watermarks anywhere in the image. "
    "Everyone wears modest clothing. Keep every character exactly as described: "
    "same face, hair, skin tone, body and clothing in every image."
)

SCENE_RE = re.compile(r"^\*\*(\d+)\*\* · `([^`]*)`\s*$")


def load_video(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_script(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    scenes, i = [], 0
    while i < len(lines):
        match = SCENE_RE.match(lines[i])
        if not match:
            i += 1
            continue
        narration, j = [], i + 1
        while j < len(lines) and lines[j].startswith("> "):
            narration.append(lines[j][2:])
            j += 1
        scenes.append({"num": int(match.group(1)), "short": match.group(2),
                       "narration": " ".join(narration)})
        i = j
    return scenes


def snippet(text, words=16):
    parts = text.split()
    return " ".join(parts[:words]) + (" …" if len(parts) > words else "")


def sentence(text):
    text = text.strip()
    if not text:
        return text
    text = text[0].upper() + text[1:]
    return text if text.endswith(".") else text + "."


def style_for(video, key):
    if not key:
        return video.STYLE
    return video.STYLE_ALT[key]


def scene_prompt(video, scene):
    detail = video.SCENES.get(scene["num"], {})
    keys = detail.get("chars", [])
    lines = [
        "Create one widescreen 16:9 landscape image.",
        f"STYLE: {style_for(video, detail.get('style'))}",
        f"SCENE: {sentence(detail.get('scene') or scene['short'])}",
    ]
    if keys:
        lines.append("KEEP THESE EXACTLY AS DESCRIBED:")
        lines += [f"- {video.CHARACTERS[k]['block']}" for k in keys]
    lines.append(f"CAMERA AND LIGHT: {sentence(detail.get('camera') or video.DEFAULT_CAMERA)}")
    lines.append(f"RULES: {GLOBAL_RULES} {video.RULES_EXTRA}")
    return "\n".join(lines)


def sheet_prompt(video, key):
    char = video.CHARACTERS[key]
    if char.get("kind") == "element":
        views = ("Show this recurring element from four angles side by side on a plain light-grey "
                 "background: front view, three-quarter view, side view and a detail close-up.")
        subject = "ELEMENT"
    elif char.get("faceless"):
        views = ("Show the same single person four times side by side on a plain light-grey studio "
                 "background: full-body back view, three-quarter back view, side profile with the face "
                 "in deep shadow, and a close-up of the hands and sleeves. The face is never visible.")
        subject = "CHARACTER"
    else:
        views = ("Show the same single person four times side by side on a plain light-grey studio "
                 "background: front view, three-quarter view, side profile and a full-body front view. "
                 "Neutral expression, relaxed pose, identical face, hair, body and clothing in all four views.")
        subject = "CHARACTER"
    return "\n".join([
        "Create one widescreen 16:9 character reference sheet.",
        views,
        f"STYLE: {style_for(video, char.get('sheet_style'))}",
        f"{subject}: {char['block']}",
        "LIGHT: even, soft studio lighting.",
        "RULES: No text, letters, numbers, labels or arrows. No other people and no background scenery. "
        f"Modest clothing. {video.RULES_EXTRA}",
    ])


def appearances(video, key, scenes):
    return [s["num"] for s in scenes if key in video.SCENES.get(s["num"], {}).get("chars", [])]


def fmt_nums(nums):
    return ", ".join(f"{n:02d}" for n in nums) if nums else "reference only"


def character_section(video, scenes, heading="###"):
    out = []
    for key, char in video.CHARACTERS.items():
        out.append(f"{heading} {char['name']}")
        out.append("")
        out.append(f"**Who / why this look:** {char['explain']}")
        out.append("")
        out.append(f"**Appears in scenes:** {fmt_nums(appearances(video, key, scenes))}")
        out.append("")
        out.append("**Fixed description** (already pasted into every scene prompt — never change a word):")
        out.append("")
        out.append(f"> {char['block']}")
        out.append("")
        out.append("**Reference sheet prompt** (generate this first, save the best result):")
        out.append("")
        out.append("```text")
        out.append(sheet_prompt(video, key))
        out.append("```")
        out.append("")
    return out


def style_section(video):
    out = [f"**Main style:** {video.STYLE}", ""]
    for key, text in video.STYLE_ALT.items():
        nums = [n for n, d in sorted(video.SCENES.items()) if d.get("style") == key]
        out.append(f"**Alternative style `{key}`** (scenes {fmt_nums(nums)}): {text}")
        out.append("")
    out.append(f"**Video-specific rules:** {video.RULES_EXTRA}")
    out.append("")
    return out


def build_video(video, scenes, problems):
    names = {k: c["name"] for k, c in video.CHARACTERS.items()}
    out = [
        f"# {video.NUMBER} · {video.TITLE} — Copilot image prompts",
        "",
        f"Script: [`{video.SCRIPT}`](../{video.SCRIPT}) · {len(scenes)} scenes · "
        "general workflow: [README.md](README.md) · all characters: [charakter-bibel.md](charakter-bibel.md)",
        "",
        "**How to use:** open ONE new Copilot chat for this video. First paste every reference sheet "
        "prompt below and save the best sheet per character. Then paste the scene prompts in order. "
        "If a face drifts, attach that character's saved sheet and write: “Use exactly the character "
        "from this reference sheet”, then paste the scene prompt again. Never shorten or reword the "
        "character descriptions.",
        "",
        "## Look of this video",
        "",
        *style_section(video),
        "## Characters and recurring elements",
        "",
        *character_section(video, scenes),
        "## Scene prompts",
        "",
    ]
    for scene in scenes:
        detail = video.SCENES.get(scene["num"], {})
        keys = detail.get("chars", [])
        prompt = scene_prompt(video, scene)
        if len(prompt) > MAX_PROMPT_CHARS:
            problems.append(f"{video.NUMBER} scene {scene['num']:02d}: prompt has {len(prompt)} characters")
        who = ", ".join(names[k] for k in keys) if keys else "no recurring characters"
        out.append(f"### Scene {scene['num']:02d} — {who}")
        out.append("")
        out.append(f"Narration: „{snippet(scene['narration'])}“")
        out.append("")
        out.append("```text")
        out.append(prompt)
        out.append("```")
        out.append("")
    return "\n".join(out)


def check(video, scenes, problems):
    nums = {s["num"] for s in scenes}
    for num, detail in video.SCENES.items():
        if num not in nums:
            problems.append(f"{video.NUMBER}: scene {num} is configured but not in the script")
        for key in detail.get("chars", []):
            if key not in video.CHARACTERS:
                problems.append(f"{video.NUMBER} scene {num}: unknown character {key}")
        if detail.get("style") and detail["style"] not in video.STYLE_ALT:
            problems.append(f"{video.NUMBER} scene {num}: unknown style {detail['style']}")
    for key, char in video.CHARACTERS.items():
        if char.get("sheet_style") and char["sheet_style"] not in video.STYLE_ALT:
            problems.append(f"{video.NUMBER}: unknown sheet style for {key}")


def build_bible(videos):
    out = [
        "# Character bible — all videos",
        "",
        "This is the master list of every recurring character and element. Each one has a fixed "
        "description that is pasted word for word into every scene prompt where it appears, plus a "
        "reference sheet prompt. The per-video prompt files contain the same blocks, so you can work "
        "from either.",
        "",
        "## Rules that apply to every image",
        "",
        f"- {GLOBAL_RULES}",
        "- Every prompt asks for a widescreen 16:9 landscape image.",
        "- No depiction of the Prophet Muhammad or of his companions — only architecture, landscapes or objects.",
        "- Real people are never named in a prompt (Copilot refuses or invents a different face). "
        "Characters based on real people have a fictional, fixed look; real people from recent decades "
        "and all living people are shown only from behind, in profile in shadow, as silhouettes or as hands.",
        "- No blood, no gore, no swastikas or other extremist symbols, no brand logos.",
        "",
        "## How consistency is guaranteed",
        "",
        "1. **Same words every time.** The description of a character is generated once and copied "
        "unchanged into every prompt. Copilot gets the identical face, hair and clothing details each time.",
        "2. **Signature details.** Every character has 2–3 features nobody else in that video has "
        "(a color, a garment, an object), so viewers recognize them even when Copilot varies the face slightly.",
        "3. **Reference sheet first.** Generate the sheet, save it, and attach it to the chat whenever "
        "a face drifts.",
        "4. **One chat per video.** Copilot keeps the earlier images of the conversation in mind.",
        "",
    ]
    for video, scenes in videos:
        out.append(f"## {video.NUMBER} · {video.TITLE}")
        out.append("")
        out += style_section(video)
        out += character_section(video, scenes, heading="###")
    return "\n".join(out)


def main():
    problems, built = [], []
    for path in sorted(VIDEOS_DIR.glob("v*.py")):
        video = load_video(path)
        scenes = parse_script(SCRIPTS_DIR / video.SCRIPT)
        check(video, scenes, problems)
        target = OUT_DIR / f"{video.SCRIPT[:-3]}-bildprompts.md"
        target.write_text(build_video(video, scenes, problems) + "\n", encoding="utf-8")
        built.append((video, scenes))
        print(f"{target.name}: {len(scenes)} scenes, {len(video.CHARACTERS)} characters/elements")
    (OUT_DIR / "charakter-bibel.md").write_text(build_bible(built) + "\n", encoding="utf-8")
    print("charakter-bibel.md written")
    if problems:
        print("\nPROBLEMS:")
        print("\n".join(problems))
        sys.exit(1)


if __name__ == "__main__":
    main()
