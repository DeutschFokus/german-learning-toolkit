NUMBER = "07"
TITLE = "Der Döner – Wem gehört Deutschlands Lieblingsessen?"
SCRIPT = "07-doener.md"

STYLE = (
    "Cinematic semi-realistic digital illustration with warm, appetizing photographic lighting, rich "
    "amber, red and deep-green tones, authentic street atmosphere, realistic proportions."
)
STYLE_ALT = {
    "archival": (
        "1960s–1970s archival documentary photo look with faded warm colors, soft film grain and slightly "
        "soft focus."
    ),
    "ottoman": (
        "The same semi-realistic illustration with warm painterly light, set in a 19th-century Ottoman town."
    ),
}
RULES_EXTRA = "No logos, no readable signs, menus or documents, no flags. No real, identifiable person."
DEFAULT_CAMERA = "Cinematic medium shot, warm appetizing light, shallow depth of field"

_AHMET_FACE = "olive skin, warm dark-brown eyes"

CHARACTERS = {
    "AHMET_YOUNG": {
        "name": "Ahmet (guest worker, 1961)",
        "sheet_style": "archival",
        "explain": (
            "A fictional guest worker who carries the story of all of them — from arrival in 1961 to "
            "grandfather today. Signature at every age: a thick mustache and warm dark-brown eyes."
        ),
        "block": (
            f"Ahmet: a young Turkish man of about 20, slim, {_AHMET_FACE}, thick wavy black hair combed back and "
            "a thick black mustache. He wears a brown wool suit jacket over a white shirt buttoned to the top, "
            "grey trousers and worn black shoes, and carries a battered brown cardboard suitcase tied with a leather belt."
        ),
    },
    "AHMET_MID": {
        "name": "Ahmet (father, 1973)",
        "sheet_style": "archival",
        "explain": "The same Ahmet at about 32, now a factory worker and father.",
        "block": (
            f"Ahmet: the same Turkish man at about 32, {_AHMET_FACE}, a slightly fuller face, thick black hair "
            "cut shorter and a full black mustache. He wears a beige factory work jacket over a white shirt and grey trousers."
        ),
    },
    "AHMET_OLD": {
        "name": "Ahmet (grandfather, today)",
        "explain": "The same Ahmet at about 85: white hair, thick white mustache, grey cardigan and flat cap.",
        "block": (
            f"Ahmet: the same Turkish man at about 85, {_AHMET_FACE}, a deeply wrinkled face, white hair and a "
            "thick white mustache. He wears a grey knit cardigan over a white shirt and a flat grey cap."
        ),
    },
    "EMRE": {
        "name": "Emre (Ahmet's grandson)",
        "explain": "Ahmet's German-born grandson who runs the spit today. Signature: black T-shirt, white apron, short fade.",
        "block": (
            "Emre: Ahmet's German-born grandson, a young man of about 22, athletic build, light olive skin, "
            "short black hair with a fade, a short neat beard and dark-brown eyes. He wears a black T-shirt and a white apron."
        ),
    },
    "MERT": {
        "name": "Mert (Döner shop owner)",
        "explain": (
            "The face of today's Döner shops in every present-day scene. Signature: shaved head, black polo "
            "shirt, white apron, beard with grey streaks."
        ),
        "block": (
            "Mert: a Turkish-German Döner shop owner of about 45, stocky, olive skin, a shaved head, a short "
            "black beard with grey streaks and friendly dark-brown eyes. He wears a black polo shirt with the "
            "sleeves pushed up and a white apron."
        ),
    },
    "PIONEER": {
        "name": "The Pioneer (1972)",
        "faceless": True,
        "sheet_style": "archival",
        "explain": (
            "Stands in for the man credited with the Döner in bread. He was a real person, so his face is never "
            "shown clearly — profile, back view or shadow only. Signature: brown knitted vest, white apron, thick mustache."
        ),
        "block": (
            "The Pioneer: a Turkish snack-stand owner of about 39, medium build, a thick black mustache and short "
            "dark hair, wearing a white shirt with rolled-up sleeves under a brown knitted vest and a white apron; "
            "always shown in profile, from behind or with his face in shadow, never a clear frontal face."
        ),
    },
    "PIONEER_OLD": {
        "name": "The Pioneer (old age)",
        "faceless": True,
        "explain": "The same man around 78, shown only as a silhouette.",
        "block": "The Pioneer in old age: the same man at about 78 with a white mustache and a grey cardigan, shown only as a silhouette or from behind.",
    },
}

SCENES = {
    1: {
        "scene": (
            "A large frozen Döner meat skewer wrapped in clear film is loaded into the cargo hold of an official "
            "government airplane by ground crew in high-visibility vests; serious mood"
        ),
    },
    5: {
        "style": "ottoman",
        "scene": (
            "In a 19th-century Ottoman town, a cook in a white apron and a red fez stands beside a vertical "
            "rotating meat spit over glowing charcoal, slicing meat"
        ),
    },
    7: {
        "style": "archival",
        "chars": ["AHMET_YOUNG"],
        "scene": (
            "1961: a train arrives at a big German station; guest workers with suitcases step onto the platform; "
            "Ahmet stands in the foreground and looks around, nervous and hopeful"
        ),
    },
    8: {
        "style": "archival",
        "chars": ["AHMET_YOUNG"],
        "scene": "A 1960s workers' dormitory room with bunk beds; Ahmet sits on a lower bunk writing a letter home by lamplight while other men rest",
    },
    9: {"style": "archival"},
    10: {
        "style": "archival",
        "chars": ["AHMET_MID"],
        "scene": (
            "1973 at a train station: Ahmet kneels and opens his arms as his two small children run toward him; "
            "his wife in a headscarf and a long coat follows with a suitcase"
        ),
    },
    11: {"style": "archival"},
    12: {
        "style": "archival",
        "chars": ["PIONEER"],
        "scene": "1972, opposite a busy train station: the Pioneer stands at his small snack stand slicing meat from a vertical spit, seen in profile",
    },
    13: {
        "style": "archival",
        "chars": ["PIONEER"],
        "scene": "Close-up of the Pioneer's hands stuffing sliced meat, onions and salad into a flatbread pocket; quick street food",
        "camera": "Close-up of hands and bread, warm light",
    },
    14: {
        "chars": ["PIONEER_OLD"],
        "scene": "Silhouette of the Pioneer in old age standing in front of a small snack stand at dusk, nostalgic warm light",
    },
    15: {"style": "archival"},
    16: {
        "chars": ["MERT"],
        "scene": "In a modern Döner shop, Mert carves meat from the spit with a long knife; colorful salads and sauces fill the counter; customers wait",
    },
    17: {
        "chars": ["MERT"],
        "scene": "Late at night, laughing teenagers order at the counter while Mert prepares their food; neon glow without readable text",
    },
    18: {"style": "archival"},
    21: {
        "chars": ["MERT"],
        "scene": "Mert stacks marinated meat slices layer by layer onto a vertical skewer; spices and herbs on the table",
        "camera": "Close-up of hands and meat, warm side light",
    },
    22: {"scene": "A small framed certificate with an ornamental border and no readable text hangs on a shop wall beside a meat spit; soft focus, warm light"},
    24: {
        "chars": ["MERT"],
        "scene": "In Mert's shop a customer counts coins in his palm in front of a menu board with blurred prices; Mert waits behind the counter",
    },
    29: {
        "chars": ["MERT"],
        "scene": "After closing time, Mert and a second shop owner sit in the empty shop reading an official letter with worried faces",
    },
    32: {
        "chars": ["MERT"],
        "scene": "In the morning light Mert smiles with relief in his shop, an official letter lying on the counter",
    },
    33: {
        "chars": ["AHMET_OLD", "EMRE"],
        "scene": "In a cozy Döner shop, Emre carves the spit while his grandfather Ahmet sits on a stool beside him, watching proudly",
        "camera": "Medium shot, warm golden light, both faces visible",
    },
    35: {
        "chars": ["AHMET_OLD", "EMRE"],
        "scene": "Close-up of two hands — Ahmet's old, wrinkled hand and Emre's young hand — holding the same Döner wrap together",
        "camera": "Extreme close-up, warm light, symbolic",
    },
    37: {
        "chars": ["MERT"],
        "scene": (
            "A Döner shop at night with warm light spilling onto a wet street; inside, Mert stands behind the "
            "counter as a silhouette; calm end frame with empty space for end-screen elements"
        ),
    },
}
