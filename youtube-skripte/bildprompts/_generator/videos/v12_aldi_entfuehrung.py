NUMBER = "12"
TITLE = "Die Aldi-Entführung – Der reiche Mann, den keiner erkannte"
SCRIPT = "12-aldi-entfuehrung.md"

STYLE = (
    "Cinematic semi-realistic digital illustration with a 1970s West German film look, rainy streets and "
    "sodium street lamps, muted browns, beiges, greys and olive greens, soft film grain, realistic proportions."
)
STYLE_ALT = {
    "early": "Warm sepia-tinted early 20th-century photo look, soft grain, faded edges, realistic proportions.",
    "modern": "Clean, bright present-day photo-realistic look, natural light, shallow depth of field.",
    "map": "Clean minimalist infographic map illustration, flat muted colors, soft glow, no labels, names or text.",
}
RULES_EXTRA = (
    "Everyone in this story is a real person: never show an identifiable face — only from behind, as a "
    "silhouette, in deep shadow or as hands. No weapons, no violence. No real store logos or brand names, no "
    "readable price tags; shop fronts and products are plain and unbranded."
)
DEFAULT_CAMERA = "Cinematic medium-wide shot, moody low light, soft film grain"

CHARACTERS = {
    "THEO": {
        "name": "Theo",
        "faceless": True,
        "explain": (
            "The kidnapped Aldi founder. Real, recent person, so never his face. Signature: plain beige belted "
            "raincoat and a plain black briefcase — the look that confused his kidnappers."
        ),
        "block": (
            "Theo: a modest German businessman of about 49, medium height, slightly stooped, thinning dark-blond hair "
            "combed back, always seen from behind, as a silhouette or with his face in deep shadow — never his face; "
            "wearing a plain beige belted raincoat over a cheap grey off-the-rack suit, a plain dark tie and black "
            "lace-up shoes, carrying a plain black leather briefcase."
        ),
    },
    "KARL": {
        "name": "Karl",
        "faceless": True,
        "explain": "His older brother, head of the southern half. Never his face. Signature: grey felt hat and navy-blue overcoat.",
        "block": (
            "Karl: a German businessman of about 51, tall and lean with an upright posture, short grey-brown hair, "
            "always seen from behind, as a silhouette or with his face in deep shadow — never his face; wearing a "
            "grey felt hat, a navy-blue wool overcoat over a dark suit and dark leather gloves."
        ),
    },
    "THEO_YOUNG": {
        "name": "Theo (young shopkeeper)",
        "faceless": True,
        "explain": "Theo in the late 1940s and 1950s. Signature: beige shop coat (a hint of the later raincoat).",
        "block": (
            "Young Theo: a thin young German shopkeeper of about 26 with dark-blond hair, always seen from behind or "
            "with his face in shadow; wearing a beige cotton shop coat over a white shirt with rolled-up sleeves and "
            "dark trousers."
        ),
    },
    "KARL_YOUNG": {
        "name": "Karl (young shopkeeper)",
        "faceless": True,
        "explain": "Karl in the late 1940s and 1950s. Signature: grey shop coat and a dark tie.",
        "block": (
            "Young Karl: a tall, lean young German shopkeeper of about 28 with short dark-brown hair, always seen from "
            "behind or with his face in shadow; wearing a grey cotton shop coat over a white shirt with a dark tie "
            "and dark trousers."
        ),
    },
    "THEO_OLD": {
        "name": "Theo (old age)",
        "faceless": True,
        "explain": "Theo in his eighties. Same beige raincoat.",
        "block": (
            "Old Theo: the same modest man in his eighties, slightly stooped, thin white hair, seen only from behind; "
            "wearing a plain beige belted raincoat over a grey suit."
        ),
    },
    "KARL_OLD": {
        "name": "Karl (old age)",
        "faceless": True,
        "explain": "Karl in his eighties. Same grey felt hat and navy coat.",
        "block": (
            "Old Karl: the same tall, lean man in his eighties with an upright posture and white hair under a grey "
            "felt hat, seen only from behind; wearing a navy-blue wool overcoat."
        ),
    },
    "LAWYER": {
        "name": "The lawyer (kidnapper)",
        "faceless": True,
        "explain": "The indebted lawyer who planned the kidnapping. Never his face. Signature: camel-colored overcoat and brown leather gloves.",
        "block": (
            "The lawyer: a well-fed man of about 40 with slicked-back dark hair, always seen from behind, as a "
            "silhouette or with his face in deep shadow; wearing a camel-colored double-breasted overcoat over a "
            "brown suit and brown leather gloves."
        ),
    },
    "BURGLAR": {
        "name": "The safecracker (kidnapper)",
        "faceless": True,
        "explain": "His accomplice. Never his face. Signature: black leather jacket and dark-grey flat cap.",
        "block": (
            "The safecracker: a burly man of about 45 with broad shoulders and short-cropped grey hair, always seen "
            "from behind, as a silhouette or with his face in deep shadow; wearing a black leather jacket, a dark-grey "
            "flat cap and dark trousers."
        ),
    },
    "BISHOP": {
        "name": "The bishop",
        "faceless": True,
        "explain": "The bishop of Essen who delivered the ransom. Only from behind. Signature: black cassock with purple sash and purple skullcap.",
        "block": (
            "The bishop: a tall Catholic bishop of about 60 with grey hair, seen only from behind or in deep shadow; "
            "wearing a long black cassock with a wide purple sash and a small purple skullcap, without visible jewelry."
        ),
    },
}

SCENES = {
    1: {
        "chars": ["LAWYER", "BURGLAR"],
        "scene": (
            "A dark, rainy parking lot outside a plain 1970s office building in the Ruhr area at night; the lawyer "
            "and the safecracker wait in a parked car, seen from behind through the rear window"
        ),
    },
    2: {
        "chars": ["THEO"],
        "scene": "Theo leaves a plain office building at night with his briefcase, seen from behind, rain glistening under a street lamp",
    },
    3: {"camera": "Low wide shot, red taillights reflecting on wet asphalt, motion blur"},
    4: {"scene": "A plain 1970s discount supermarket at dusk with simple shelves of unbranded cardboard boxes; a customer pushes a cart"},
    5: {"style": "early"},
    6: {"style": "early"},
    7: {
        "style": "early",
        "scene": "Two young boys, seen from behind, stack tins on shelves in a small corner grocery shop in the 1920s, warm light",
    },
    8: {"style": "early"},
    9: {
        "style": "early",
        "chars": ["THEO_YOUNG", "KARL_YOUNG"],
        "scene": "Young Theo and young Karl stand in their small shop in the late 1940s, seen from behind, discussing a short handwritten list",
    },
    10: {
        "style": "early",
        "chars": ["THEO_YOUNG", "KARL_YOUNG"],
        "scene": "In a small 1950s self-service shop with plain unbranded products, young Theo hands a customer a paper bag while young Karl restocks a shelf, both seen from behind",
    },
    14: {"style": "map"},
    15: {
        "chars": ["THEO", "KARL"],
        "scene": "In a plain 1960 office, Theo and Karl face each other across a desk with a sealed cardboard carton between them, tension, both faces in shadow",
        "camera": "Side view, hard window light, silhouettes",
    },
    16: {"style": "map"},
    19: {
        "chars": ["LAWYER"],
        "scene": "The lawyer sits in a parked car on a rainy evening, seen from behind, studying a newspaper without readable text",
    },
    20: {
        "chars": ["LAWYER"],
        "scene": "A desk at night covered with unpaid bills and letters and an empty wallet; the lawyer stands at the window, seen from behind",
    },
    21: {
        "chars": ["THEO", "LAWYER", "BURGLAR"],
        "scene": "At night in the rain, the lawyer and the safecracker guide Theo into a car; his briefcase lies on the wet ground; no weapons visible",
        "camera": "Wide shot from behind, street lamp glow, all faces in shadow",
    },
    22: {
        "chars": ["THEO"],
        "scene": "A small dark room in a city building with a cot and a single lamp; Theo sits quietly in the shadows",
    },
    23: {
        "chars": ["THEO"],
        "scene": "Theo sits on a cot in a dim room, seen from behind; a tray with bread and a glass of water beside him",
    },
    26: {
        "chars": ["BISHOP"],
        "scene": "The bishop carries a heavy leather bag through a dark, empty church aisle, seen from behind",
        "camera": "Wide shot from behind, candlelight, long shadows",
    },
    27: {
        "chars": ["BISHOP"],
        "scene": "On a quiet country road at night a car has stopped with its headlights on; the bishop hands over a heavy bag to a figure in shadow",
    },
    28: {
        "chars": ["BURGLAR"],
        "scene": "In a 1970s police interrogation room, the safecracker, seen from behind, faces two police officers in plain clothes",
    },
    32: {"scene": "A 1979 tax office with towering stacks of files; a man in a plain dark suit, seen from behind, hands a thick file across a counter"},
    37: {"camera": "Wide shot, overcast daylight, no people"},
    38: {"style": "modern"},
    39: {"style": "modern"},
    40: {"style": "modern"},
    41: {"scene": "An elderly man's hands with the cuff of a beige raincoat write figures in a simple notebook with a short pencil, morning light"},
    42: {
        "chars": ["THEO_OLD", "KARL_OLD"],
        "scene": "Old Theo and old Karl walk side by side on a quiet path with autumn leaves, seen from behind",
        "camera": "Wide shot from behind, soft autumn light",
    },
    43: {"scene": "A long early-morning queue of people in 1990s winter coats outside a plain discount store, breath in the cold air"},
    44: {"style": "modern"},
    45: {"scene": "A plain beige belted raincoat hangs on a simple coat hook beside a plain black leather briefcase, symbolic still life"},
    46: {"style": "modern"},
    47: {"style": "modern"},
    48: {"style": "modern", "camera": "Wide shot, soft dawn light, calm, empty space for end-screen elements"},
}
