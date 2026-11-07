NUMBER = "05"
TITLE = "Konstantinopel 1453 – Die Nacht, in der Schiffe über einen Berg fuhren"
SCRIPT = "05-konstantinopel-1453.md"

STYLE = (
    "Epic cinematic digital oil painting with painterly brushwork, 15th-century Ottoman and Byzantine "
    "historical detail, dramatic torchlight and golden-hour tones, deep blues and warm ambers, atmospheric "
    "smoke and haze, grand scale."
)
STYLE_ALT = {
    "modern": (
        "The same epic cinematic digital oil painting with painterly brushwork, but present-day Istanbul, "
        "warm dusk light and calm atmosphere."
    ),
}
RULES_EXTRA = (
    "No blood, no gore, no dead bodies, no visible wounds. Respectful depiction of both sides. No depiction "
    "of the Prophet Muhammad or of his companions. No banners with writing."
)
DEFAULT_CAMERA = "Epic cinematic wide shot, dramatic light, atmospheric smoke and depth"

CHARACTERS = {
    "SULTAN": {
        "name": "The young Sultan",
        "explain": (
            "Mehmed II, aged 19 to 21. Never named in the prompt. Signature: large white turban with a small "
            "red cap, deep-green kaftan with gold-colored embroidery, red sash, red boots, white horse in later scenes."
        ),
        "block": (
            "The young Sultan: an Ottoman ruler of about 21, slender but strong, light olive skin, a narrow "
            "face with a slightly hooked nose, intense dark-brown eyes, a short thin black beard and mustache. "
            "He wears a large white wrapped turban with a small red cap at its top, a long deep-green kaftan of "
            "fine wool with gold-colored floral embroidery over a white undergarment, a wide red sash, red "
            "leather boots and a curved sword in a plain dark scabbard at his side."
        ),
    },
    "TEACHER": {
        "name": "The Teacher",
        "explain": "Akşemseddin, the Sultan's spiritual teacher. Shown from behind or in profile. Signature: long white beard, plain white turban, brown robe, prayer beads.",
        "block": (
            "The Teacher: an elderly Ottoman scholar of about 65 with a long white beard and kind deep-set "
            "eyes, wearing a large plain white turban and a simple brown wool robe, prayer beads in his hand; "
            "usually seen from behind or in profile."
        ),
    },
    "EMPEROR": {
        "name": "The Emperor",
        "explain": "Constantine XI, the last Byzantine emperor, about 49. Signature: purple cloak, gilded scale armor, simple gold circlet.",
        "block": (
            "The Emperor: a Byzantine emperor of about 49, tall, a weathered face, a short greying dark-brown "
            "beard and tired but resolute grey eyes. He wears gilded scale armor over a deep-purple tunic, a "
            "purple cloak fastened with a round gold brooch and a simple gold circlet crown."
        ),
    },
    "COMMANDER": {
        "name": "The Commander",
        "explain": "Giovanni Giustiniani, the Genoese commander. Signature: polished steel plate armor over red, red-and-white sash, scar on the chin.",
        "block": (
            "The Commander: a Genoese military commander of about 45, sun-tanned skin, a strong jaw, short "
            "black curly hair, clean-shaven, with a pale scar across his chin. He wears polished steel plate "
            "armor over a red tunic and a red-and-white sash."
        ),
    },
    "CANNON_MASTER": {
        "name": "The Cannon Master",
        "explain": "Orban, the cannon founder. Signature: bald head, bushy reddish-brown beard, leather apron.",
        "block": (
            "The Cannon Master: a burly Central European foundry master of about 50, ruddy fair skin, a bald "
            "head and a bushy reddish-brown beard, wearing a heavy leather apron over a rough linen shirt and thick leather gloves."
        ),
    },
    "PATRIARCH": {
        "name": "The Patriarch",
        "explain": "The Orthodox patriarch appointed by the Sultan after the conquest. Appears once.",
        "block": (
            "The Patriarch: an Orthodox monk-scholar of about 50 with a long black beard streaked with grey and "
            "serious dark eyes, wearing black monastic robes and a tall black cylindrical hat with a black veil."
        ),
    },
}

SCENES = {
    1: {
        "chars": ["SULTAN"],
        "scene": (
            "At night, thousands of men pull ropes and oxen strain to haul dozens of wooden galleys up a "
            "forested hill over greased wooden logs, torches everywhere; on the hilltop the young Sultan "
            "watches from his horse"
        ),
    },
    9: {
        "chars": ["SULTAN"],
        "scene": "The young Sultan studies maps of a walled city by candlelight in a richly carpeted tent, one hand on the map, intense focus",
        "camera": "Medium close-up, warm candlelight, deep shadows",
    },
    10: {
        "chars": ["TEACHER", "SULTAN"],
        "scene": (
            "In a study full of books, maps and a brass astrolabe, the Teacher, seen from behind, explains "
            "something to the young Sultan, who listens attentively"
        ),
        "camera": "Over-the-shoulder shot from behind the Teacher, warm window light",
    },
    11: {"scene": "An old book with Arabic calligraphy lies open on a carved wooden stand in soft light; no people"},
    12: {"scene": "A domed stone mausoleum beside ancient city walls in peaceful evening light; no people"},
    13: {
        "chars": ["SULTAN"],
        "scene": (
            "The young Sultan stands on a hill overlooking a massive stone fortress rising on the shore of the "
            "Bosporus; thousands of workers build at great speed while ships pass on the water"
        ),
    },
    14: {
        "chars": ["CANNON_MASTER"],
        "scene": "In a 15th-century foundry, the Cannon Master supervises workers pouring glowing molten bronze into the mold of a giant cannon",
        "camera": "Medium-wide shot, orange glow of molten metal, sparks and smoke",
    },
    15: {
        "chars": ["CANNON_MASTER"],
        "scene": (
            "A giant bronze cannon is hauled along a hilly road by dozens of oxen and hundreds of men; the "
            "Cannon Master walks beside it giving instructions"
        ),
    },
    17: {
        "chars": ["EMPEROR"],
        "scene": (
            "At night, exhausted defenders repair a breach in the city wall with timber, earth and barrels by "
            "torchlight; the Emperor helps carry a wooden beam among them"
        ),
    },
    18: {
        "chars": ["COMMANDER"],
        "scene": "The Commander stands on the battlements and directs soldiers, pointing toward the enemy lines, determined",
        "camera": "Low-angle medium shot, dramatic sky behind him",
    },
    21: {
        "chars": ["SULTAN"],
        "scene": (
            "The young Sultan rides his horse into the shallow sea, his green kaftan and cloak flying, furious, "
            "staring after tall sailing ships that escape across the waves"
        ),
    },
    22: {
        "chars": ["SULTAN"],
        "scene": (
            "At night, workers lay a long track of greased wooden logs up a hill behind a harbor town, torches "
            "everywhere; the young Sultan on horseback directs the work"
        ),
    },
    25: {"scene": "Split image: an Ottoman helmet on one side and a Byzantine helmet on the other, dark background, dramatic light"},
    28: {
        "chars": ["EMPEROR"],
        "scene": (
            "The Emperor stands alone on the city walls at sunset, solemn and resolute, his purple cloak moving "
            "in the wind as he looks toward the enemy camp"
        ),
    },
    29: {
        "chars": ["SULTAN"],
        "scene": (
            "The night before the battle: a vast Ottoman camp with thousands of campfires; long rows of "
            "soldiers pray together, and the young Sultan prays in the front row, seen from behind"
        ),
    },
    30: {
        "scene": (
            "A massive night assault on the city walls: waves of soldiers in tall white felt caps and dark-blue "
            "robes climb ladders while defenders in chain mail hold the battlements; torches and smoke; no blood"
        ),
    },
    31: {
        "chars": ["COMMANDER"],
        "scene": (
            "The injured Commander is carried away from the wall by two of his men, clutching his side with no "
            "visible wound; chaos and smoke around them"
        ),
    },
    33: {
        "chars": ["EMPEROR"],
        "scene": (
            "Seen from behind: the Emperor throws off his purple cloak and gold circlet and charges into the "
            "smoke of the battle with his sword raised"
        ),
        "camera": "Medium shot from behind, backlit by fire and smoke",
    },
    34: {
        "chars": ["SULTAN"],
        "scene": "The young Sultan rides a white horse through a great city gate into the conquered city in morning light",
    },
    35: {
        "chars": ["SULTAN"],
        "scene": (
            "In front of the Hagia Sophia, the young Sultan has dismounted and scatters a handful of earth over "
            "his turban as a humble gesture; his white horse stands beside him"
        ),
    },
    36: {
        "chars": ["SULTAN", "PATRIARCH"],
        "scene": "In a palace hall, the young Sultan hands a ceremonial staff to the Patriarch, who receives it with a bow",
    },
    37: {"scene": "The Eyüp mosque complex with its domed tomb on the Golden Horn at sunset; pilgrims only as tiny silhouettes"},
    38: {"style": "modern"},
    40: {
        "scene": (
            "A printing workshop in Mainz in the 1450s: a printer in a leather apron pulls a freshly printed "
            "page from a wooden screw press; candlelight, ink balls and wooden type cases"
        ),
    },
    41: {"scene": "Old printed pages with dense blackletter-style type arranged like a calendar, candlelight on the paper; the type is decorative and not readable"},
    43: {"style": "modern"},
    45: {"style": "modern"},
}
