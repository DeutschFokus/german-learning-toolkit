NUMBER = "04"
TITLE = "Die wichtigste Maschine der Welt – und ihr deutsches Herz"
SCRIPT = "04-zeiss-chipmaschine.md"

STYLE = (
    "Cinematic sci-fi realism as a semi-realistic digital painting: sterile clean-room whites and cool "
    "greys, glowing violet ultraviolet light, precise macro details, crisp high-tech atmosphere, realistic proportions."
)
STYLE_ALT = {
    "flashback": (
        "Black-and-white archival photograph look from the 1900s to the 1940s, soft film grain, slightly "
        "faded contrast, documentary realism."
    ),
}
RULES_EXTRA = "No logos, no company names, no flags, no military insignia. No real, identifiable person."
DEFAULT_CAMERA = "Cinematic wide shot, clean symmetrical composition, cool light with violet highlights"

CHARACTERS = {
    "ANNA": {
        "name": "Anna (clean-room engineer)",
        "explain": (
            "The face of today's mirror makers. Because she is always in a clean-room suit, Copilot only has to "
            "keep her eyes and one strand of copper-red hair consistent. Nobody else has red hair in this video."
        ),
        "block": (
            "Anna: a German optical engineer of about 35, always fully dressed in a white clean-room suit with "
            "hood, a white face mask and clear safety goggles, so that only her calm green eyes and one small "
            "strand of copper-red hair at her forehead are visible. She wears light-blue nitrile gloves."
        ),
    },
    "HEINRICH": {
        "name": "Heinrich (Zeiss engineer, 1945)",
        "sheet_style": "flashback",
        "explain": (
            "One of the 77 specialists taken west in 1945 — a fictional face for the story of all of them. "
            "Signature: round wire-rimmed glasses, scar through the left eyebrow, felt hat, worn suitcase."
        ),
        "block": (
            "Heinrich: a German optics engineer of about 40, a thin face, round wire-rimmed glasses, short dark "
            "hair parted on the side and a small scar through his left eyebrow. He wears a long grey wool coat "
            "over a brown tweed suit and a dark felt hat, and carries a worn brown leather suitcase."
        ),
    },
}

SCENES = {
    2: {
        "chars": ["ANNA"],
        "scene": "Anna stands beside an immaculate curved mirror in a clean room and inspects it closely; the mirror reflects violet light",
        "camera": "Medium shot, the mirror glowing in the foreground, Anna slightly behind it",
    },
    4: {
        "style": "flashback",
        "chars": ["HEINRICH"],
        "scene": (
            "1945: US Army trucks drive along a country road; in the back of the first truck sit men in long "
            "coats with suitcases; Heinrich sits at the tailgate in the foreground and looks back at the town he is leaving"
        ),
        "camera": "Medium-wide shot from behind the truck, dusty road, overcast sky",
    },
    17: {
        "chars": ["ANNA"],
        "scene": (
            "Anna and two colleagues in identical white clean-room suits measure a large curved mirror with "
            "laser interferometers; violet reflections shine on their goggles; Anna stands in the foreground"
        ),
    },
    19: {"scene": "A giant machine the size of a bus stands in a clean room; technicians in white suits look tiny next to it"},
    23: {
        "scene": "Point-of-view shot of a hand holding a smartphone, a faint violet glow shining from inside the device",
        "camera": "First-person close-up, dark room, violet glow",
    },
    24: {"style": "flashback"},
    25: {
        "style": "flashback",
        "scene": (
            "An elderly 19th-century physicist with a full grey beard, a high forehead and small round "
            "spectacles, wearing a dark frock coat, sits in a study full of microscopes and optical instruments, seen from the side"
        ),
    },
    26: {
        "style": "flashback",
        "chars": ["HEINRICH"],
        "scene": (
            "Spring 1945: American soldiers walk through the streets of a German university town with factory "
            "chimneys behind; Heinrich watches from a doorway, holding his hat in his hands"
        ),
    },
    27: {"style": "flashback"},
    28: {
        "style": "flashback",
        "chars": ["HEINRICH"],
        "scene": (
            "1946: in a modest workshop in a rural Swabian town, Heinrich and a few men in coats set up old "
            "lathes and optical instruments; winter light falls through dusty windows"
        ),
    },
    29: {"style": "flashback"},
    32: {
        "chars": ["ANNA"],
        "scene": (
            "The first production machine is unveiled in a clean room; technicians in white suits applaud; Anna "
            "stands in the front row, her green eyes smiling above the mask"
        ),
    },
    38: {
        "chars": ["ANNA"],
        "scene": "Close-up of Anna's gloved hands polishing a mirror surface; her green eyes and goggles are reflected in the perfect mirror",
        "camera": "Macro close-up, violet reflections, extreme sharpness",
    },
    39: {
        "scene": "A hand holding a smartphone whose dark screen reflects a tiny image of a small town in green hills",
        "camera": "Close-up, soft evening light",
    },
}
