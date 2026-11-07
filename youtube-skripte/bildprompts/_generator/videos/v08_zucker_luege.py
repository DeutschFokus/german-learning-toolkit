NUMBER = "08"
TITLE = "Die Zuckerlüge – Wie die Industrie die Wissenschaft kaufte"
SCRIPT = "08-zucker-luege.md"

STYLE = (
    "Cinematic semi-realistic digital illustration with clean, slightly clinical lighting, whites, soft "
    "greys and warm sugar-gold highlights, crisp modern scenes, shallow depth of field, realistic proportions."
)
STYLE_ALT = {
    "archival": "Archival 1950s–1970s documentary photo look with faded colors and soft film grain.",
}
RULES_EXTRA = (
    "No logos, no brand names, no readable labels, letters or documents. No real, identifiable person. "
    "Never show anyone's body in a mocking or shaming way."
)
DEFAULT_CAMERA = "Cinematic medium shot, clean soft light, shallow depth of field"

CHARACTERS = {
    "AMERICAN": {
        "name": "The American scientist",
        "sheet_style": "archival",
        "explain": (
            "The loud champion of the fat theory. Based on a real person, so he is fictional-looking and "
            "shown in profile. Signature: dark-grey suit, slicked-back hair with grey temples."
        ),
        "block": (
            "The American scientist: a confident American nutrition scientist in his 50s with a square jaw, "
            "slicked-back dark hair with grey temples and energetic gestures, wearing a dark-grey suit, a white "
            "shirt and a thin dark tie; shown in profile or from the side."
        ),
    },
    "BRITON": {
        "name": "The British scientist",
        "faceless": True,
        "sheet_style": "archival",
        "explain": (
            "The quiet warner about sugar. Based on a real person, so shown from behind or in profile. "
            "Signature: tweed jacket with elbow patches, round tortoiseshell glasses."
        ),
        "block": (
            "The British scientist: a quiet British physiologist in his 60s, slim, balding with a fringe of grey "
            "hair and round tortoiseshell glasses, wearing a brown tweed jacket with leather elbow patches over a "
            "beige knitted vest, a white shirt and a brown tie; usually seen from behind or in profile."
        ),
    },
    "BRITON_OLD": {
        "name": "The British scientist (old age)",
        "faceless": True,
        "sheet_style": "archival",
        "explain": "The same man in his 80s, seen from behind.",
        "block": (
            "The British scientist in old age: the same quiet man in his 80s, slim, white hair around a bald "
            "crown, round tortoiseshell glasses and a brown tweed jacket, seen from behind."
        ),
    },
    "EXECUTIVE": {
        "name": "The Executive",
        "sheet_style": "archival",
        "explain": "The sugar-industry boss of the 1960s (fictional). Signature: navy pinstripe suit, thick black glasses, silver hair, shiny cufflinks.",
        "block": (
            "The Executive: an American sugar-industry executive of about 55, heavyset, slicked-back silver "
            "hair, clean-shaven, thick black-framed glasses, wearing a navy pinstripe suit, a white pocket square "
            "and shiny cufflinks."
        ),
    },
    "RESEARCHER": {
        "name": "The Researcher",
        "faceless": True,
        "explain": (
            "Stands in for the dentist who found the documents. She is a real, living person, so her face is "
            "NEVER shown. Signature: wavy auburn hair, navy blazer."
        ),
        "block": (
            "The Researcher: a woman in her 40s, always seen from behind or over her shoulder and never her "
            "face, with shoulder-length wavy auburn hair, wearing a navy-blue blazer over a cream blouse and dark trousers."
        ),
    },
    "SARAH": {
        "name": "Sarah (the viewer)",
        "explain": "The everyday viewer in all present-day 'you' scenes. Signature: teal-green knit sweater, curly hair in a loose bun.",
        "block": (
            "Sarah: a German woman of about 35, light-brown skin, dark curly hair tied in a loose bun and warm "
            "brown eyes, wearing a teal-green knit sweater and blue jeans."
        ),
    },
}

SCENES = {
    1: {
        "style": "archival",
        "scene": (
            "A 1960s university office: a scientist in a white shirt and tie, seen from the side, reads a letter; "
            "on the desk lie a stack of dollar bills and a single sugar cube"
        ),
    },
    2: {
        "chars": ["RESEARCHER"],
        "scene": "In a dim archive room, the Researcher lifts old letters out of a cardboard box; dust floats in a beam of light",
        "camera": "Over-the-shoulder shot from behind, beam of light, dust particles",
    },
    3: {
        "chars": ["SARAH"],
        "scene": (
            "Sarah stands in a supermarket aisle in front of a shelf full of low-fat yogurts and light products "
            "and holds a magnifying glass over a blurred nutrition label"
        ),
    },
    4: {"style": "archival"},
    5: {
        "style": "archival",
        "chars": ["AMERICAN", "BRITON"],
        "scene": (
            "The American scientist and the British scientist sit facing each other across a table, seen from "
            "the side: a butter dish stands in front of the American, a sugar bowl in front of the Briton; tension"
        ),
        "camera": "Side view, symmetrical composition, hard window light",
    },
    6: {
        "style": "archival",
        "chars": ["AMERICAN"],
        "scene": "The American scientist points at a world map with pins in seven countries in a 1950s research office with charts on the walls",
    },
    7: {
        "style": "archival",
        "chars": ["BRITON"],
        "scene": "The British scientist writes at a desk in London, seen from behind; rain on the window and a sugar bowl beside his notes",
    },
    8: {"style": "archival", "scene": "An empty conference hall with a single chair in the middle; melancholic light; no people"},
    9: {
        "style": "archival",
        "chars": ["EXECUTIVE"],
        "scene": "In a 1965 office, the Executive dictates a letter to a secretary; plain sacks of sugar without labels are stacked in the background",
    },
    10: {
        "style": "archival",
        "chars": ["EXECUTIVE"],
        "scene": "The Executive gives a speech at a podium in a 1950s banquet hall, seen from behind; an audience in suits listens",
    },
    11: {
        "style": "archival",
        "chars": ["EXECUTIVE"],
        "scene": "Close-up: the Executive's hand with a shiny cufflink hands a check across a wooden desk to another man's hand; a fountain pen lies beside it",
        "camera": "Close-up of hands, warm desk-lamp light",
    },
    12: {
        "style": "archival",
        "scene": "Three academics in suits review stacks of papers in a wood-paneled university office, warm lamp light",
    },
    13: {"style": "archival"},
    14: {"style": "archival"},
    15: {"style": "archival"},
    16: {"style": "archival"},
    17: {"style": "archival"},
    21: {
        "chars": ["RESEARCHER"],
        "scene": (
            "In a conference room in 2007, the Researcher sits in the audience, seen from behind, and frowns at a "
            "presentation slide showing only abstract charts"
        ),
    },
    22: {
        "chars": ["RESEARCHER"],
        "scene": "At night in a quiet archive, the Researcher sits among boxes of documents and reads intensely under a desk lamp, seen from behind",
        "camera": "Medium shot from behind, warm desk lamp, dark archive shelves",
    },
    25: {
        "chars": ["SARAH"],
        "scene": "Sarah stands at a kitchen counter with a cup of tea and a sugar bowl in cozy morning light",
    },
    31: {
        "chars": ["SARAH"],
        "scene": "In the afternoon Sarah sits at a kitchen table and chooses a glass of water and a bowl of nuts instead of a chocolate bar; calm atmosphere",
    },
    32: {
        "scene": "In a bright dental clinic, a friendly dentist in a white coat shows a healthy tooth model to a patient",
    },
    34: {
        "chars": ["SARAH"],
        "scene": "Close-up: Sarah's hand turns a product in her shopping basket, which holds water, plain yogurt and fruit, to read the label",
        "camera": "Close-up of hand and basket, bright supermarket light",
    },
    35: {
        "style": "archival",
        "chars": ["BRITON_OLD"],
        "scene": "The British scientist in old age stands in a library, seen from behind, in golden light",
    },
    38: {
        "chars": ["SARAH"],
        "scene": "Sarah stands in a supermarket reading a health claim on a product with a thoughtful expression",
    },
}
