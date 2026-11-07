NUMBER = "06"
TITLE = "Deutsche Bahn – Warum die Bahn nie pünktlich ist"
SCRIPT = "06-deutsche-bahn.md"

STYLE = (
    "Cinematic semi-realistic digital illustration with photographic lighting, contemporary Germany and "
    "Switzerland, overcast cool blue-grey palette with warm yellow station-light accents, realistic "
    "proportions, documentary framing."
)
STYLE_ALT = {
    "archival": "1990s archival documentary photo look with faded colors and soft film grain.",
    "painting": "A 19th-century oil painting with visible brushstrokes, warm varnished colors and soft daylight.",
}
RULES_EXTRA = (
    "No logos, no railway company branding, no readable signs, screens or timetables, no flags. "
    "No real, identifiable person."
)
DEFAULT_CAMERA = "Cinematic medium-wide shot, 35mm lens, natural overcast light, documentary feel"

_TOBIAS = (
    "Tobias: a German commuter of about 34, average build, light skin, short dark-blond hair, a neatly "
    "trimmed short beard and brown eyes."
)

CHARACTERS = {
    "TOBIAS": {
        "name": "Tobias (the commuter)",
        "explain": (
            "The viewer's stand-in on every platform. Signature: navy-blue parka, charcoal backpack with a "
            "small ORANGE keychain (the one bright spot that makes him easy to find in crowds)."
        ),
        "block": (
            f"{_TOBIAS} He wears a navy-blue parka over a grey hoodie, dark jeans and black sneakers, and "
            "carries a charcoal-grey backpack with a small orange keychain."
        ),
    },
    "TOBIAS_SUMMER": {
        "name": "Tobias (summer outfit)",
        "explain": "Same Tobias in the summer heat: grey T-shirt instead of the parka, same backpack with orange keychain.",
        "block": (
            f"{_TOBIAS} In the summer heat he wears a light-grey T-shirt, dark jeans and black sneakers, and "
            "carries the same charcoal-grey backpack with a small orange keychain."
        ),
    },
    "HELGA": {
        "name": "Helga",
        "explain": "Half of the elderly couple in the hook scene. Signature: red wool coat, white curls.",
        "block": "Helga: a German woman of about 72 with short white curly hair and round glasses, wearing a red wool coat and a beige scarf.",
    },
    "WERNER": {
        "name": "Werner",
        "explain": "Helga's husband. Signature: grey flat cap, brown corduroy jacket.",
        "block": "Werner: a tall, thin German man of about 74 with a grey flat cap, a dark-brown corduroy jacket and a grey scarf.",
    },
    "GERMAN_TRAIN": {
        "name": "The German high-speed train (recurring element)",
        "kind": "element",
        "explain": "Always the same train design so viewers read it as 'the German train' without any real logo.",
        "block": (
            "The German high-speed train: a sleek white high-speed train with one continuous red stripe along "
            "its side and dark tinted windows, no logos or lettering."
        ),
    },
    "SWISS_TRAIN": {
        "name": "The Swiss train (recurring element)",
        "kind": "element",
        "explain": "Always red with a white roof — the visual opposite of the German train.",
        "block": "The Swiss train: a bright red intercity train with a white roof and large windows, no logos or lettering.",
    },
}

SCENES = {
    1: {
        "chars": ["GERMAN_TRAIN", "SWISS_TRAIN", "TOBIAS"],
        "scene": (
            "At Basel station, the German high-speed train has stopped at the end of its journey; confused "
            "passengers step out with their luggage, Tobias among them in the foreground; on the opposite "
            "platform the Swiss train waits, perfectly on time"
        ),
    },
    2: {
        "chars": ["TOBIAS"],
        "scene": (
            "Travelers in a large German station hall look up at a huge departure board covered in red delay "
            "markers with no readable text; Tobias stands in the foreground rubbing his forehead in frustration"
        ),
    },
    3: {
        "chars": ["HELGA", "WERNER"],
        "scene": "Helga and Werner sit on their old suitcases on a cold, empty platform at night, waiting, their breath visible in the air",
        "camera": "Medium shot, cold platform lights, deep night blue",
    },
    4: {"style": "archival"},
    6: {
        "chars": ["TOBIAS"],
        "scene": "Tobias stands alone on an empty platform in the evening and checks his phone; no train in sight; long shadows",
    },
    7: {
        "chars": ["SWISS_TRAIN"],
        "scene": (
            "A spotless Swiss railway station with a large classic black-and-white station clock without "
            "numbers; the Swiss train arrives precisely; snowy mountains in the background"
        ),
    },
    9: {
        "chars": ["TOBIAS_SUMMER"],
        "scene": (
            "A crowded platform in summer heat: travelers fan themselves with papers, Tobias wipes sweat from "
            "his forehead, a delayed train is visible far away"
        ),
    },
    10: {
        "style": "painting",
        "scene": "The first German steam locomotive with open passenger carriages in 1835, a cheering crowd in period clothing along the tracks",
    },
    11: {
        "style": "archival",
        "chars": ["GERMAN_TRAIN"],
        "scene": "1991: the new German high-speed train is presented to an audience on a platform, camera flashes everywhere",
    },
    12: {"style": "archival"},
    13: {"style": "archival"},
    14: {"style": "archival"},
    15: {"style": "archival"},
    16: {
        "chars": ["GERMAN_TRAIN"],
        "scene": "On a single-track line without any siding, the German high-speed train is stuck behind a slow, rusty freight train",
    },
    19: {"style": "archival"},
    21: {
        "chars": ["GERMAN_TRAIN"],
        "scene": "The German high-speed train, a red regional train and a heavy freight train share the same pair of tracks in a busy corridor",
        "camera": "Wide aerial shot, all three trains visible at once",
    },
    23: {
        "scene": (
            "Interior of an old mechanical signal box with a long row of large iron levers and wire pulls; a "
            "railway worker in his 60s with a grey mustache and a dark-blue uniform jacket operates a lever"
        ),
    },
    27: {
        "chars": ["SWISS_TRAIN"],
        "scene": (
            "A Swiss hub station where several Swiss trains arrive at the same minute; passengers change "
            "platforms calmly; a big station clock without numbers"
        ),
    },
    30: {
        "chars": ["TOBIAS"],
        "scene": "Tobias sits on the floor of a crowded train corridor between suitcases, tired but smiling ironically",
        "camera": "Medium shot from a low angle, harsh train interior light",
    },
    35: {
        "scene": (
            "A female train driver in her 50s with short grey hair and a navy uniform jacket sits in the cab at "
            "dusk, focused, hands on the controls, warm cabin light"
        ),
    },
    37: {
        "chars": ["TOBIAS"],
        "scene": "Tobias sits in a station café with a coffee cup and fills out a refund form on his smartphone, relieved",
    },
    38: {
        "chars": ["GERMAN_TRAIN"],
        "scene": "The German high-speed train crosses a newly renovated bridge at golden hour; hopeful mood",
    },
    39: {
        "chars": ["TOBIAS", "GERMAN_TRAIN"],
        "scene": "Tobias stands on a platform, checks the time on his phone and smiles slightly as the German high-speed train arrives",
    },
    40: {
        "chars": ["GERMAN_TRAIN"],
        "scene": (
            "An empty platform at night; the red taillights of the German high-speed train disappear into the "
            "distance; calm end frame with empty space for end-screen elements"
        ),
    },
}
