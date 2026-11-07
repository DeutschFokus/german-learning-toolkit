NUMBER = "01"
TITLE = "Mansa Musa – Der Mann, der zu viel Gold hatte"
SCRIPT = "01-mansa-musa.md"

STYLE = (
    "Cinematic digital oil painting with visible fine brushstrokes, like a high-end historical "
    "documentary illustration. Warm palette of gold, ochre, terracotta and deep indigo, soft "
    "volumetric sunlight, gentle desert haze, rich detail. Setting: the 14th-century Mali Empire and "
    "Mamluk Egypt, with historically inspired clothing and mud-brick and stone architecture. "
    "Dignified, respectful, epic mood."
)
STYLE_ALT = {
    "modern": (
        "The same cinematic digital oil painting style with visible fine brushstrokes, but a "
        "present-day setting (Mali, 2012–2013): dusty beige streets, cooler blue-grey shadows, "
        "warm low sunlight. Dignified, quiet, tense mood."
    ),
}
RULES_EXTRA = (
    "No blood, no gore, no weapons pointed at anyone. No depiction of the Prophet Muhammad or of his "
    "companions. No rings or necklaces on men."
)
DEFAULT_CAMERA = "Cinematic wide shot, rule-of-thirds composition, atmospheric depth, warm natural light"

CHARACTERS = {
    "KING": {
        "name": "The King",
        "explain": (
            "Mansa Musa, emperor of Mali, around 45 at the time of his pilgrimage in 1324. No authentic "
            "portrait exists, so this is a fixed, dignified design. Signature: white robe with golden-yellow "
            "embroidery, tall white turban with one golden-yellow band, tall wooden staff with a small golden "
            "orb. White and gold belong to him only — nobody else in this video wears them."
        ),
        "block": (
            "The King: a West African emperor of about 45, tall and broad-shouldered, deep dark-brown skin "
            "with a warm undertone, an oval face with high cheekbones, calm dark-brown eyes, a broad straight "
            "nose, full lips and a short, neatly trimmed black beard with a few grey hairs at the chin. He "
            "wears a voluminous white cotton grand boubou robe with wide sleeves, embroidered with "
            "golden-yellow geometric patterns along the neckline, chest and hem, loose white trousers, a tall "
            "white wrapped turban with one narrow golden-yellow band, and simple brown leather sandals. He "
            "holds a tall dark wooden staff topped with a small golden orb. No rings, no necklaces. Calm, "
            "dignified, generous expression."
        ),
    },
    "OLD_KING": {
        "name": "The Old King",
        "explain": (
            "Musa's predecessor, who sailed into the Atlantic with 2,000 ships and never came back. Dressed "
            "in indigo and silver with a long white beard so he can never be confused with The King."
        ),
        "block": (
            "The Old King: a West African ruler of about 60, very dark skin, a lean weathered face, "
            "deep-set searching eyes and a long white beard. He wears a flowing indigo-blue robe with "
            "silver embroidery, an indigo wrapped turban and a dark cloak, and holds a carved black ebony "
            "staff. Restless, visionary expression."
        ),
    },
    "SULTAN": {
        "name": "The Sultan",
        "explain": (
            "The Mamluk sultan of Cairo who received Musa in 1324. Crimson and black palace colors, so the "
            "meeting reads as two different worlds at a glance."
        ),
        "block": (
            "The Sultan: a Mamluk sultan of about 40, light olive skin, a narrow face, a short black beard "
            "and sharp dark eyes. He wears a large white turban wrapped around a red cap, a long crimson "
            "wool robe with gold-colored borders and a wide black sash, and sits on a raised, carved wooden "
            "throne. Proud, watchful expression."
        ),
    },
    "ARCHITECT": {
        "name": "The Architect",
        "explain": (
            "Abu Ishaq as-Sahili, the poet-architect from Granada who joined Musa on the way home and is "
            "said to have designed the Djinguereber Mosque. Signature: cream turban, dark-blue cloak, rolled plans."
        ),
        "block": (
            "The Architect: an Andalusian poet and architect of about 50, light olive skin, a short "
            "grey-streaked beard and thoughtful hazel eyes, wearing a cream-colored turban, a dark-blue "
            "travel cloak over a beige robe, and carrying rolled-up building plans tied with a cord."
        ),
    },
    "LIBRARIAN": {
        "name": "The Librarian",
        "faceless": True,
        "sheet_style": "modern",
        "explain": (
            "Stands in for the real librarian who organized the 2012–2013 rescue of the Timbuktu "
            "manuscripts. He is a real, living person, so his face is NEVER shown — only his back, his hands "
            "or his profile in shadow. The light-blue robe, white cap and leather satchel make him recognizable."
        ),
        "block": (
            "The Librarian: a slim West African man in his late 40s, always seen from behind, from the side "
            "with his face in deep shadow, or only as hands — never a clear face. He wears a light-blue cotton "
            "boubou robe and a white embroidered kufi cap, and carries a small brown leather satchel over one shoulder."
        ),
    },
}

SCENES = {
    1: {
        "chars": ["KING"],
        "scene": (
            "A royal West African caravan enters a crowded medieval street in Cairo in 1324. Attendants in "
            "indigo robes scatter gold dust that glitters in the sunlight, astonished people lean from "
            "wooden balconies, and the King rides a white horse at the center of the procession"
        ),
        "camera": "Wide shot from street level, low sun behind the caravan, glittering dust in the air",
    },
    2: {
        "chars": ["KING"],
        "scene": (
            "Close-up of the King's hands and wide white sleeves with golden-yellow embroidery pouring fine "
            "gold dust into the open, cupped palms of poor people in simple clothes. Only his hands, sleeves "
            "and the edge of his robe are visible"
        ),
        "camera": "Extreme close-up, shallow depth of field, warm backlight that makes the gold dust sparkle",
    },
    3: {
        "chars": ["KING"],
        "scene": (
            "The King sits on a carved wooden throne under a canopy of white cloth, backlit by a low sun, so "
            "he appears partly as a majestic silhouette with glowing edges while his white robe and staff "
            "stay recognizable"
        ),
        "camera": "Low-angle medium-wide shot, strong golden rim light, dust floating in the air",
    },
    5: {
        "scene": (
            "An ancient parchment map in the style of a 14th-century nautical chart, with a small painted "
            "crowned African king on a throne holding a huge gold nugget, lit by flickering candlelight"
        ),
        "camera": "Top-down close-up of the map on a wooden table, candle glow at the edges",
    },
    6: {
        "chars": ["OLD_KING"],
        "scene": (
            "On a West African Atlantic beach at dawn, the Old King watches as hundreds of wooden ships with "
            "patched sails are launched into the open ocean; sailors push boats through the surf"
        ),
    },
    8: {
        "chars": ["OLD_KING"],
        "scene": (
            "The Old King boards a large wooden ship from a long wooden jetty and looks back one last time; "
            "behind him a fleet of two thousand vessels stretches to the horizon under a pale morning sky"
        ),
    },
    9: {
        "chars": ["KING"],
        "scene": (
            "The King stands alone in the courtyard of a mud-brick palace with wooden beams, holding his "
            "staff and gazing toward the horizon at golden hour; quiet, thoughtful mood"
        ),
        "camera": "Medium-wide shot in three-quarter view from behind, long golden shadows",
    },
    16: {
        "chars": ["KING"],
        "scene": (
            "A grand procession crosses the desert: attendants in indigo robes carry tall golden staffs on "
            "both sides, and in the middle the King rides a white horse under a white parasol held by an "
            "attendant; heat haze shimmers over the sand"
        ),
    },
    17: {
        "chars": ["KING"],
        "scene": (
            "In a small desert oasis town with palm trees, the King hands small cloth bags of gold to poor "
            "people and to scholars in front of a newly built, simple mud-brick mosque; people gather for "
            "Friday prayer in the background"
        ),
    },
    18: {
        "chars": ["KING"],
        "scene": (
            "The long caravan approaches Cairo: the Nile, palm groves and medieval minarets on the skyline, "
            "the pyramids faint in the distance; the King rides at the front on his white horse, seen from behind"
        ),
    },
    19: {
        "chars": ["SULTAN"],
        "scene": (
            "A grand Mamluk throne hall with ornate stone arches, colored glass lamps and a patterned marble "
            "floor; the Sultan sits on his raised throne while courtiers in turbans bow low before him"
        ),
    },
    20: {
        "chars": ["KING", "SULTAN"],
        "scene": (
            "In the Mamluk throne hall, the King stands upright and calm in the center and does not bow, "
            "while the courtiers around him whisper in shock; the Sultan watches from his raised throne in the background"
        ),
        "camera": "Medium-wide shot, the King in the foreground right, the Sultan small and high in the back",
    },
    21: {
        "chars": ["KING"],
        "scene": (
            "The King kneels in prostration on a simple prayer rug in a quiet corner of the palace hall, seen "
            "from the side; a beam of light falls from a high window onto him; serene and humble mood"
        ),
        "camera": "Side view, wide framing with lots of empty space, soft beam of light",
    },
    22: {
        "chars": ["KING"],
        "scene": (
            "A bustling medieval Cairo bazaar: the King's attendants in indigo robes hand out gold to "
            "merchants, beggars and officials, while cloth, spices and horses are being sold; in the "
            "background the King watches calmly from his white horse"
        ),
    },
    24: {
        "scene": (
            "A Cairo scholar in his 40s with a neat black beard, a white turban and a dark-green robe writes "
            "with a reed pen on parchment in a candlelit library full of books"
        ),
        "camera": "Medium close-up, warm candlelight, quiet concentration",
    },
    25: {
        "chars": ["KING"],
        "scene": (
            "At night in a tent, the King looks into an open, almost empty wooden treasure chest and raises "
            "one eyebrow with gentle, ironic humor; an oil lamp lights the scene"
        ),
        "camera": "Medium shot, warm lamplight, soft shadows",
    },
    28: {
        "chars": ["KING", "ARCHITECT"],
        "scene": (
            "At a city gate at dawn, the King welcomes a group of scholars carrying books and brass "
            "astrolabes into his caravan; the Architect stands at the front of the group with his rolled-up plans"
        ),
    },
    29: {
        "chars": ["ARCHITECT"],
        "scene": (
            "The Architect directs the building of the Djinguereber Mosque in Timbuktu: mud-brick walls with "
            "wooden beams sticking out, workers on palm-wood scaffolds, an earthen minaret rising"
        ),
    },
    33: {
        "scene": (
            "Detail of a medieval nautical map: a small painted crowned king on a throne holding a large gold "
            "nugget and a scepter, surrounded by painted desert, camels and tents"
        ),
        "camera": "Close-up of the parchment, candle glow, fine ink lines",
    },
    34: {
        "style": "modern",
        "scene": (
            "A modern smartphone lying on a dark table shows a social media post with a huge golden dollar "
            "symbol that is crossed out by a big red X"
        ),
        "camera": "Close-up, dark moody light, the screen glowing",
    },
    36: {"style": "modern"},
    37: {
        "style": "modern",
        "chars": ["LIBRARIAN"],
        "scene": (
            "The Librarian's hands, with light-blue sleeves, gently open an ancient manuscript with "
            "astronomical circles, diagrams and Arabic script on yellowed paper; dust floats in a beam of light"
        ),
        "camera": "Extreme close-up of hands and pages, soft window light",
    },
    38: {
        "style": "modern",
        "scene": (
            "A convoy of dusty pickup trucks with silhouetted men in the back drives into a sand-colored "
            "desert town, a huge dust cloud behind them, an ominous orange sky; no weapons visible, no violence"
        ),
    },
    39: {
        "style": "modern",
        "chars": ["LIBRARIAN"],
        "scene": (
            "The Librarian stands in a dim private library between tall wooden shelves full of manuscripts "
            "in leather covers, seen from behind, with a determined posture"
        ),
        "camera": "Medium shot from behind, light from a small high window",
    },
    40: {
        "style": "modern",
        "chars": ["LIBRARIAN"],
        "scene": (
            "At night in a courtyard, the Librarian and several helpers quietly pack bundles of manuscripts "
            "into dark-green metal footlockers by lantern light; the Librarian is seen from behind in the foreground"
        ),
        "camera": "Medium-wide shot, warm lantern light against deep blue night",
    },
    41: {
        "style": "modern",
        "chars": ["LIBRARIAN"],
        "scene": (
            "A donkey cart loaded with crates of mangoes, tomatoes and onions hides dark-green metal "
            "footlockers underneath; the Librarian walks beside it, seen from behind, as the cart approaches "
            "a simple roadblock made of oil drums at dusk"
        ),
    },
    42: {
        "style": "modern",
        "scene": (
            "Smoke rises from the courtyard of a sand-colored building; papers burn on the ground in a "
            "tragic orange glow; no people in the image"
        ),
    },
    43: {
        "style": "modern",
        "chars": ["LIBRARIAN"],
        "scene": (
            "Dawn in a quiet storage room in Bamako: rows of dark-green metal footlockers are stacked safely "
            "along the walls; the Librarian stands among them, seen from behind, relieved"
        ),
        "camera": "Wide shot, first morning light through a small window",
    },
    44: {
        "style": "modern",
        "scene": (
            "Restorers in white lab coats and white gloves carefully handle fragile manuscripts in a bright, "
            "clean conservation studio"
        ),
    },
    47: {
        "style": "modern",
        "scene": (
            "A girl of about ten in a long orange dress and a matching headscarf reads a book on a flat "
            "mud-brick rooftop in Timbuktu at sunrise; hopeful mood"
        ),
    },
    48: {
        "chars": ["KING"],
        "scene": (
            "Silhouette of the King on his white horse leading a long golden caravan toward a huge setting sun over the dunes"
        ),
        "camera": "Extreme wide shot, strong backlight, final cinematic frame",
    },
}
