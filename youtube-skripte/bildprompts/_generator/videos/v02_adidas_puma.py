NUMBER = "02"
TITLE = "Adidas gegen Puma – Der Bruderkrieg, der eine Stadt teilte"
SCRIPT = "02-adidas-puma.md"

STYLE = (
    "Semi-realistic cinematic historical illustration, a digital painting with subtle film grain, "
    "muted earthy palette of browns, greys, olive and faded cream with occasional deep-red accents, "
    "soft directional light, 35mm documentary framing. Setting: the small Franconian town of "
    "Herzogenaurach in Germany between the 1920s and the 1970s, with half-timbered houses, cobblestone "
    "streets and the narrow Aurach river. Faces are painterly, not photographic."
)
STYLE_ALT = {
    "modern": (
        "The same semi-realistic cinematic digital painting with subtle film grain, but a present-day "
        "setting with modern buildings and clothing, slightly brighter and cleaner colors."
    ),
}
RULES_EXTRA = (
    "No brand logos or brand marks, no flags, no swastikas or other political symbols, no military "
    "insignia, no blood. These are fictional characters; do not make them look like any real person."
)
DEFAULT_CAMERA = "Cinematic medium-wide shot, 35mm lens, natural window light, documentary feel"

_ADI_FACE = (
    "slim and of medium height, a narrow face, a straight prominent nose, thin lips, serious "
    "hazel-green eyes, clean-shaven"
)
_RUDOLF_FACE = "a broad, stocky build, a round face, a thin neat mustache, bright blue eyes, a strong chin"

CHARACTERS = {
    "ADI_YOUNG": {
        "name": "Adi (younger brother, 1920s)",
        "explain": (
            "The younger brother and quiet inventor. Based on a real person, so the look is fictional and "
            "painterly; never type his real name into Copilot. Signature in every era: slim, clean-shaven, "
            "hair combed straight back, NO hat, light-grey or brown clothing."
        ),
        "block": (
            f"Adi, the younger brother, aged about 22: {_ADI_FACE}, dark-brown hair combed straight back. "
            "He wears a white collarless shirt with the sleeves rolled up, a brown leather work apron and "
            "grey wool trousers; no hat. Quiet, concentrated expression."
        ),
    },
    "ADI_MID": {
        "name": "Adi (younger brother, 1930s–1940s)",
        "explain": "Adi at about 40. Same face as in the 1920s, now in his light-grey suit with a pencil behind the ear.",
        "block": (
            f"Adi, the younger brother, aged about 40: {_ADI_FACE}, dark-brown hair combed straight back and "
            "slightly thinner at the temples. He wears a light-grey three-piece suit, a white shirt and a "
            "dark-brown tie, with a pencil behind his right ear; no hat. Quiet, reserved expression."
        ),
    },
    "ADI_OLD": {
        "name": "Adi (younger brother, 1950s)",
        "explain": "Adi at about 55: grey hair, round dark-rimmed glasses, light-grey cardigan.",
        "block": (
            f"Adi, the younger brother, aged about 55: {_ADI_FACE}, deeper lines in the face, round "
            "dark-rimmed glasses, grey hair combed straight back. He wears a light-grey cardigan over a white "
            "shirt and a dark-brown tie; no hat."
        ),
    },
    "RUDOLF_YOUNG": {
        "name": "Rudolf (older brother, 1920s)",
        "explain": (
            "The older brother and born salesman. Based on a real person, so the look is fictional and "
            "painterly. Signature in every era: stocky, thin mustache, slicked-back wavy blond hair, "
            "dark-navy suit, burgundy tie, grey fedora."
        ),
        "block": (
            f"Rudolf, the older brother, aged about 26: {_RUDOLF_FACE}, wavy dark-blond hair slicked back. "
            "He wears a dark-navy double-breasted suit, a white shirt, a burgundy tie and, outdoors, a grey "
            "felt fedora hat. Confident salesman's grin."
        ),
    },
    "RUDOLF_MID": {
        "name": "Rudolf (older brother, 1940s)",
        "explain": "Rudolf at about 45, in his dark-navy pinstripe suit with burgundy tie and grey fedora.",
        "block": (
            f"Rudolf, the older brother, aged about 45: {_RUDOLF_FACE}, wavy dark-blond hair slicked back. "
            "He wears a dark-navy pinstripe suit, a white shirt, a burgundy tie and, outdoors, a grey felt fedora hat."
        ),
    },
    "RUDOLF_WAR": {
        "name": "Rudolf (older brother, war years)",
        "explain": "Rudolf at about 45 in a plain grey greatcoat — deliberately WITHOUT any insignia or badges.",
        "block": (
            f"Rudolf, the older brother, aged about 45: {_RUDOLF_FACE}, wavy dark-blond hair slicked back. "
            "He wears a plain grey wool greatcoat, buttoned up, with no insignia, badges or symbols, and no hat."
        ),
    },
    "RUDOLF_OLD": {
        "name": "Rudolf (older brother, 1950s–1970s)",
        "explain": "Rudolf at 60 to 75: silver hair, grey mustache, still the dark-navy suit and burgundy tie.",
        "block": (
            "Rudolf, the older brother, aged about 65: a heavy-set build, a round face with deep lines, a grey "
            "mustache, bright blue eyes and silver-grey hair slicked back. He wears a dark-navy suit, a white "
            "shirt and a burgundy tie."
        ),
    },
    "KAETHE": {
        "name": "Käthe (Adi's wife)",
        "explain": "Adi's wife; she saves the factory in 1945. Signature: dark-green dress, low bun, grey coat.",
        "block": (
            "Käthe, Adi's wife, aged about 33: slim, a determined oval face, brown eyes, dark-brown hair pinned "
            "up in a low bun. She wears a long-sleeved dark-green wool dress with a white collar that reaches "
            "below the knee and, outdoors, a long grey wool coat."
        ),
    },
    "FRIEDL": {
        "name": "Friedl (Rudolf's wife)",
        "explain": "Rudolf's wife. Signature: light-blond waves, burgundy dress, dark coat with fur collar.",
        "block": (
            "Friedl, Rudolf's wife, aged about 38: a round face, blue eyes, light-blond hair set in tight "
            "waves. She wears a long-sleeved burgundy dress below the knee and, outdoors, a dark coat with a fur collar."
        ),
    },
    "HORST": {
        "name": "Horst (Adi's son, 1970)",
        "explain": "Adi's son. Inherits his father's slim look; black-rimmed glasses and a charcoal suit.",
        "block": (
            "Horst, Adi's son, aged about 34: tall and lean, a long narrow face, dark hair with sideburns, "
            "black-rimmed rectangular glasses, clean-shaven. He wears a slim charcoal suit, a white shirt and a narrow black tie."
        ),
    },
    "ARMIN": {
        "name": "Armin (Rudolf's son, 1970)",
        "explain": "Rudolf's son. Inherits his father's round face, mustache and burgundy tie.",
        "block": (
            "Armin, Rudolf's son, aged about 41: a sturdy build, a round face like his father's, light-blond "
            "hair combed back, a small neat mustache and blue eyes. He wears a navy suit, a white shirt and a burgundy tie."
        ),
    },
    "FACTORIES": {
        "name": "The two factories (recurring element)",
        "kind": "element",
        "explain": "The two factories facing each other across the river. Always the same colors and sides.",
        "block": (
            "The two factories: on the left bank of the narrow river stands Adi's red-brick factory with tall "
            "arched windows; on the right bank stands Rudolf's pale-yellow plastered factory with a dark slate "
            "roof. A small stone bridge connects the banks."
        ),
    },
}

SCENES = {
    1: {
        "scene": (
            "In a 1950s street of the small Franconian town, passers-by in coats and hats glance down at each "
            "other's shoes as they pass; half-timbered houses and a church tower, overcast light"
        ),
        "camera": "Street-level medium-wide shot, shoes sharp in the foreground, faces slightly soft",
    },
    2: {
        "chars": ["FACTORIES"],
        "scene": "Aerial view of the small town divided by the narrow river; the two factories face each other across the water",
        "camera": "High aerial wide shot, soft morning light",
    },
    3: {
        "chars": ["ADI_MID", "RUDOLF_MID"],
        "scene": (
            "Adi and Rudolf stand back to back in an empty factory hall, each looking away from the other "
            "with arms crossed; dramatic side light splits the image into light and shadow"
        ),
        "camera": "Symmetrical medium shot, hard side light",
    },
    4: {
        "scene": (
            "The heavy steel door of a dark air-raid shelter swings open; the silhouettes of a man and a woman "
            "step inside against faint light from the stairs; inside, the dim shapes of a family on benches"
        ),
    },
    5: {
        "scene": (
            "Herzogenaurach around 1920: a cobblestone street, half-timbered houses, a few poorly dressed "
            "people and a horse cart; post-war poverty on a grey morning"
        ),
    },
    6: {
        "chars": ["ADI_YOUNG"],
        "scene": (
            "Adi works alone in a tiny former laundry room turned workshop: he cuts leather on a wooden table "
            "by the light of a single lamp, surrounded by shoe lasts, hammers, needles and scraps of old canvas"
        ),
        "camera": "Medium shot, warm lamplight, deep shadows",
    },
    7: {
        "chars": ["RUDOLF_YOUNG"],
        "scene": (
            "In a small 1920s shop, Rudolf shakes hands with a sports-club official, smiling confidently; a "
            "pair of handmade running shoes stands on the counter between them"
        ),
    },
    8: {
        "chars": ["ADI_YOUNG", "RUDOLF_YOUNG"],
        "scene": (
            "Adi and Rudolf stand together in their small factory, workers at sewing machines behind them and "
            "stacks of shoe boxes around; Adi holds up a running shoe while Rudolf points at it proudly; warm, optimistic light"
        ),
    },
    9: {
        "scene": (
            "The Berlin Olympic stadium in 1936: packed stands, an athletics track, summer light; no flags, no "
            "banners and no symbols anywhere"
        ),
    },
    10: {
        "chars": ["ADI_MID"],
        "scene": (
            "Adi drives a black 1930s car along a tree-lined road toward a sports village; a leather suitcase "
            "full of running spikes lies on the passenger seat"
        ),
        "camera": "Side view of the car, Adi visible through the open window",
    },
    11: {
        "scene": (
            "An athlete in a white running vest sprints on a cinder track, seen from behind in strong motion "
            "blur so that no face is visible; a roaring crowd in the stands"
        ),
    },
    12: {
        "chars": ["ADI_MID", "RUDOLF_MID"],
        "scene": (
            "In a busy factory office, Rudolf talks on a black telephone with a big smile while Adi studies a "
            "shoe design at his desk; order books pile up and secretaries carry papers"
        ),
    },
    13: {
        "chars": ["ADI_MID", "KAETHE", "RUDOLF_MID", "FRIEDL"],
        "scene": (
            "In a large villa dining room, both families sit at one long table: Adi and Käthe on the left, "
            "Rudolf and Friedl on the right; Käthe and Friedl exchange cold looks while the brothers avoid "
            "each other's eyes"
        ),
        "camera": "Wide shot down the length of the table, chandelier light, tense silence",
    },
    14: {
        "chars": ["RUDOLF_WAR", "FRIEDL"],
        "scene": "At a small train station, Rudolf in his plain grey greatcoat says goodbye to Friedl; a steam train waits; grim, grey mood",
    },
    15: {
        "scene": (
            "Night sky over a small German town in 1943: searchlight beams cross the clouds, dark aircraft "
            "shapes high above, the town's rooftops in the foreground"
        ),
    },
    16: {
        "chars": ["RUDOLF_MID", "FRIEDL", "ADI_MID", "KAETHE"],
        "scene": (
            "Inside a cramped, dimly lit air-raid shelter, Rudolf and Friedl already sit on a wooden bench "
            "while Adi and Käthe step in through the heavy door; everyone turns their heads, tension in the air"
        ),
        "camera": "Medium-wide shot from inside the shelter, a single bare bulb as light source",
    },
    17: {
        "chars": ["RUDOLF_MID"],
        "scene": "Close-up of Rudolf's face in the dark shelter, half lit by a single lamp, his eyes narrowing in anger and hurt",
        "camera": "Close-up in profile, strong chiaroscuro",
    },
    18: {
        "chars": ["KAETHE", "FACTORIES"],
        "scene": (
            "April 1945: American army jeeps roll into the small town and white sheets hang from the windows; "
            "in front of the red-brick factory, Käthe stands calmly and explains something with open hands to "
            "an American officer, who is seen from behind; no weapons pointed at anyone"
        ),
    },
    19: {
        "chars": ["RUDOLF_WAR"],
        "scene": "Rudolf stands behind a tall wire fence at a grey post-war holding compound, looking into the distance; cold grey light",
    },
    20: {
        "chars": ["ADI_MID", "RUDOLF_MID"],
        "scene": "Adi and Rudolf shout at each other across an office desk; papers fly, a desk lamp is knocked over",
        "camera": "Medium shot across the desk, dramatic tense light",
    },
    21: {
        "chars": ["RUDOLF_MID", "FACTORIES"],
        "scene": (
            "Rudolf carries a wooden box across the small stone bridge toward his pale-yellow factory, a small "
            "group of workers following him; on the other bank the red-brick factory stays behind"
        ),
    },
    22: {
        "chars": ["ADI_MID"],
        "scene": "Adi sits at his workbench stitching three parallel leather stripes onto the side of a sports shoe, completely focused",
        "camera": "Medium close-up, warm desk lamp",
    },
    23: {"scene": "Two bakeries on opposite street corners of the small town, each with its own queue of customers; people throw cold glances across the street"},
    24: {"scene": "A young couple holds hands nervously in a small town square while two disapproving families watch from opposite sides"},
    25: {
        "scene": "Two plain leather sneakers without any logos face each other on a wooden floor like boxers in a ring",
        "camera": "Low close-up, a single spotlight from above, dark background",
    },
    26: {"scene": "Bern 1954: heavy rain pours onto a muddy football pitch, players in heavy wool shirts, a packed stadium behind; no flags"},
    27: {
        "chars": ["ADI_OLD"],
        "scene": (
            "Close-up of Adi's hands, with his light-grey cardigan sleeves, screwing long studs into a leather "
            "football boot at the edge of a rainy pitch; raindrops drip from the boot"
        ),
        "camera": "Extreme close-up of hands and boot, rain in the light",
    },
    28: {
        "chars": ["RUDOLF_OLD", "FACTORIES"],
        "scene": (
            "Rudolf, older now, sits in his office reading a newspaper with no readable text, his jaw clenched; "
            "through the window the red-brick factory is visible across the river"
        ),
    },
    29: {
        "scene": (
            "A sprinter in a white tracksuit stands on an Olympic podium in Rome in 1960, seen from behind, "
            "holding a pair of running shoes; bright sunlight; no faces visible"
        ),
    },
    30: {
        "chars": ["HORST", "ARMIN"],
        "scene": (
            "Horst and Armin shake hands reluctantly in a modern 1970 hotel lobby in Mexico; polite smiles "
            "that do not reach their eyes"
        ),
    },
    31: {
        "scene": (
            "Close-up of a football player kneeling on the pitch and tying the laces of his black boots, face "
            "not visible; TV cameras zoom in from the side; a blurred stadium crowd behind"
        ),
    },
    33: {
        "chars": ["RUDOLF_OLD"],
        "scene": "Rudolf, now an old man, lies in a hospital bed by a window in dim light; an empty chair stands beside the bed",
        "camera": "Medium-wide shot, cold window light, quiet and lonely mood",
    },
    35: {"style": "modern"},
    36: {"style": "modern"},
    37: {"style": "modern"},
    38: {"style": "modern"},
    39: {"style": "modern"},
    40: {"scene": "An old, empty laundry room with a single pair of handmade leather shoes on a wooden table, warm nostalgic light"},
    41: {"style": "modern"},
    42: {
        "chars": ["FACTORIES"],
        "scene": "The narrow river at dusk with both factories softly lit on either bank, calm end frame with empty space for end-screen elements",
    },
}
