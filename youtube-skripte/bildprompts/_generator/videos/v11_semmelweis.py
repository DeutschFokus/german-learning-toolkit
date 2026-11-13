NUMBER = "11"
TITLE = "Semmelweis – Der Arzt, der das Händewaschen erfand"
SCRIPT = "11-semmelweis.md"

STYLE = (
    "Cinematic semi-realistic digital painting with an oil-painting feel, Vienna in the 1840s, candlelight "
    "and grey daylight, deep browns, blacks and creamy whites with muted green accents, soft shadows, "
    "realistic proportions."
)
STYLE_ALT = {
    "modern": "Clean, bright present-day photo-realistic look, natural light, crisp whites, shallow depth of field.",
}
RULES_EXTRA = (
    "Hospital scenes are always dignified: patients fully covered and modestly dressed, women with long "
    "sleeves and covered hair. No dead bodies, no wounds, no blood, no medical gore; dissection tables are "
    "always covered with a plain white sheet and nothing beneath it is visible. No depiction of the Prophet "
    "Muhammad or his companions."
)
DEFAULT_CAMERA = "Cinematic medium shot, candlelight or soft window light, deep shadows"

CHARACTERS = {
    "IGNAZ": {
        "name": "Ignaz (young doctor)",
        "explain": (
            "The hero, a doctor of the 1840s, so he gets a fixed look loosely inspired by old portraits. "
            "Signature: dark-green waistcoat and the thick brown ledger with a green ribbon."
        ),
        "block": (
            "Ignaz: a doctor of about 29, stocky, a round full face with ruddy cheeks, light-blue eyes, receding "
            "light-brown hair combed back, light-brown side whiskers and a full moustache, wearing a black frock "
            "coat over a dark-green waistcoat, a white shirt with a black cravat, often carrying a thick brown "
            "ledger with a green ribbon bookmark."
        ),
    },
    "IGNAZ_OLD": {
        "name": "Ignaz (older, 1860s)",
        "explain": "The same man in his mid-40s, worn out and angry. Same green waistcoat, now crumpled.",
        "block": (
            "Older Ignaz: the same doctor at about 45, heavier, a bald crown with grey hair at the sides, grey side "
            "whiskers and moustache, light-blue eyes with deep tired lines, wearing a crumpled black frock coat over "
            "a dark-green waistcoat, a white shirt and a loosened black cravat."
        ),
    },
    "KLEIN": {
        "name": "Professor Klein",
        "explain": "His boss, who refused to listen. Signature: bald head with bushy white side whiskers and a stern jaw.",
        "block": (
            "Professor Klein: an elderly Viennese professor of about 60, bald with bushy white side whiskers, small "
            "stern grey eyes, a heavy jaw and a disapproving mouth, wearing a long black tailcoat, a high white "
            "collar and a black silk cravat."
        ),
    },
    "KOLLETSCHKA": {
        "name": "Jakob (the friend)",
        "explain": "His friend and colleague whose death gave him the answer. Signature: round wire spectacles and a brown frock coat.",
        "block": (
            "Jakob: a friendly doctor of about 43, slim, dark curly hair, round wire spectacles, clean-shaven, a "
            "warm smile, wearing a brown frock coat over a grey-striped waistcoat and a white shirt with a dark "
            "cravat."
        ),
    },
}

SCENES = {
    1: {"camera": "Wide shot, gas-lamp glow, cold night, wet cobblestones"},
    2: {
        "scene": (
            "In a hospital entrance hall at night, a pregnant young woman in a modest long dark dress and headscarf "
            "kneels before a hospital porter and begs; the porter looks away"
        ),
    },
    3: {
        "chars": ["IGNAZ"],
        "scene": "Ignaz studies the columns of numbers in his ledger by lamplight, intense and focused",
        "camera": "Close-up, single warm lamp, dark background",
    },
    4: {"style": "modern", "camera": "Macro close-up, bright clean light, water droplets"},
    6: {
        "chars": ["IGNAZ"],
        "scene": (
            "A long, gloomy hospital ward with rows of iron beds; women lie ill, fully covered under blankets with "
            "covered hair; Ignaz walks between the beds"
        ),
    },
    7: {"scene": "A midwife in a long grey dress and white apron helps a mother in a modest nightgown and headscarf in a simple room, warm candlelight"},
    9: {
        "chars": ["KLEIN"],
        "scene": "Professor Klein dismisses a question with an impatient wave of his hand in his wood-panelled office",
    },
    10: {
        "chars": ["IGNAZ"],
        "scene": "Ignaz arrives at the Vienna General Hospital with his ledger under his arm, eager and curious",
    },
    11: {
        "chars": ["IGNAZ"],
        "scene": "Ignaz writes columns of numbers in his ledger at a desk covered with records, by candlelight",
    },
    12: {
        "chars": ["IGNAZ"],
        "scene": (
            "Ignaz sits at the bedside of a sick young mother in a modest nightgown and headscarf, fully covered by "
            "a blanket, and holds her hand gently; candlelight"
        ),
    },
    13: {"scene": "A priest in long black robes walks through the hospital ward ringing a small bell; women in the beds, fully covered, watch anxiously"},
    14: {
        "chars": ["IGNAZ"],
        "scene": "Ignaz sits alone on a bench in an empty hospital corridor at night, head in his hands, defeated",
    },
    15: {
        "chars": ["IGNAZ"],
        "scene": "Ignaz stands in a dark corridor and looks through a window into the calm, candle-lit midwives' ward, thoughtful",
        "camera": "Shot from behind his shoulder through the window",
    },
    16: {
        "chars": ["IGNAZ", "KOLLETSCHKA"],
        "scene": "Ignaz and Jakob laugh together on a bench in a sunny hospital garden",
        "camera": "Medium shot, warm spring daylight",
    },
    17: {"camera": "Wide shot, cold grey window light, students seen from behind"},
    18: {
        "chars": ["IGNAZ"],
        "scene": "Ignaz reads a report at his desk, his eyes widening with sudden realization",
        "camera": "Close-up, dramatic lamplight from below",
    },
    19: {"scene": "A long hospital corridor leading from a door with a covered dissection table behind it straight to a maternity ward; a doctor in a black coat walks from one to the other"},
    21: {"scene": "A white porcelain basin filled with cloudy liquid on a stand beside a clinic door, a blank paper notice pinned above it"},
    22: {
        "chars": ["IGNAZ"],
        "scene": "Doctors and students line up to wash their hands in a porcelain basin, some grumbling; Ignaz watches strictly",
    },
    23: {"scene": "A nurse in a long grey dress, white apron and white cap carefully washes metal instruments in a steaming basin in a 19th-century clinic"},
    24: {"scene": "A smiling young mother in a modest nightgown and headscarf holds her healthy, swaddled newborn in a hospital bed, soft morning light"},
    25: {"style": "modern"},
    26: {
        "chars": ["IGNAZ"],
        "scene": "In a lecture hall, 19th-century physicians in top hats laugh and shake their heads at Ignaz, who stands alone at the front",
    },
    27: {"camera": "Profile shot, soft window light"},
    28: {
        "chars": ["KLEIN", "IGNAZ"],
        "scene": "In his office, Professor Klein angrily points at the door; Ignaz stands before him, clutching his ledger",
    },
    30: {
        "chars": ["IGNAZ"],
        "scene": "Ignaz sits in a horse-drawn coach leaving Vienna in the rain and looks back at the city through the wet window",
    },
    31: {
        "chars": ["IGNAZ"],
        "scene": (
            "A small, modest wedding in 1857, seen from behind: Ignaz stands beside a young bride in a long, "
            "high-collared white dress with long sleeves and a veil; a few guests"
        ),
        "camera": "Wide shot from behind, soft church-window light",
    },
    32: {
        "chars": ["IGNAZ_OLD"],
        "scene": "Older Ignaz writes furiously at his desk at night; crumpled letters lie on the floor, ink spilled",
    },
    33: {"scene": "Stacks of printed open letters on a table; a hand holds one up angrily", "camera": "Close-up, hard lamplight"},
    34: {
        "chars": ["IGNAZ_OLD"],
        "scene": "Older Ignaz stares exhausted out of a window, grey light on his tired face",
    },
    35: {"camera": "Wide shot, grey overcast light, oppressive mood"},
    36: {
        "chars": ["IGNAZ_OLD"],
        "scene": "At a barred asylum door, two guards in grey uniforms hold back older Ignaz, who struggles to leave; no blood, no injuries",
        "camera": "Medium shot, cold grey light, motion blur",
    },
    40: {"scene": "A 19th-century laboratory with microscopes and glass flasks; a scientist seen from behind looks through a brass microscope"},
    42: {"scene": "An elderly physicist writes at a desk in a study full of books in the 1940s, seen from behind"},
    43: {"style": "modern"},
    44: {"style": "modern"},
    45: {"style": "modern"},
    46: {"style": "modern"},
    47: {
        "style": "modern",
        "scene": "A man washes his hands, face and forearms at a simple stone fountain in a mosque courtyard at dawn, seen from behind",
        "camera": "Wide shot from behind, soft blue dawn light, peaceful",
    },
    48: {
        "chars": ["IGNAZ"],
        "scene": "Ignaz stands in a sunlit hospital doorway with a faint, peaceful smile",
        "camera": "Backlit doorway, warm golden light",
    },
    49: {"style": "modern", "camera": "Close-up, calm, empty space on one side for end-screen elements"},
}
