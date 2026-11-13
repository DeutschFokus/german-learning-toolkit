NUMBER = "09"
TITLE = "Ibn al-Haytham – Der Mann, der den Verrückten spielte"
SCRIPT = "09-ibn-al-haytham.md"

STYLE = (
    "Cinematic semi-realistic digital painting of medieval Cairo and Basra around the year 1000, warm "
    "candlelight and golden sunlight, deep shadows, rich ochre, sand, indigo and turquoise tones, "
    "visible volumetric light beams, realistic proportions."
)
STYLE_ALT = {
    "modern": "Clean cinematic present-day photo-realistic look, natural light, shallow depth of field.",
    "manuscript": (
        "Medieval scientific drawing in brown ink on aged, slightly stained parchment, delicate fine lines, "
        "soft vignette."
    ),
}
RULES_EXTRA = (
    "No depiction of the Prophet Muhammad or his companions. No weapons, no violence. Arabic or Latin "
    "writing only as abstract decorative strokes, never readable. The Caliph's face is never shown clearly."
)
DEFAULT_CAMERA = "Cinematic medium-wide shot, warm directional light, soft shadows, shallow depth of field"

HASAN_BLOCK = (
    "Hasan: an Arab scholar of about 45 with light-brown skin, a lean face, a high forehead, deep-set dark-brown "
    "eyes and a short, neatly trimmed black beard with grey streaks, wearing a white wrapped turban, a long "
    "dark indigo-blue robe with a plain sand-colored sash and brown leather sandals, always carrying a small "
    "brown leather-bound notebook."
)

CHARACTERS = {
    "HASAN": {
        "name": "Hasan (Ibn al-Haytham)",
        "explain": (
            "The hero, a scholar who lived around 965–1040, so he gets a fixed fictional look. "
            "Signature: indigo-blue robe and the small brown leather notebook he always carries."
        ),
        "block": HASAN_BLOCK,
    },
    "HASAN_YOUNG": {
        "name": "Hasan (young, Basra)",
        "explain": "The same man at about 25 in Basra. Same indigo robe and notebook so viewers recognize him.",
        "block": (
            "Young Hasan: an Arab scholar of about 25 with light-brown skin, a lean face, a high forehead, deep-set "
            "dark-brown eyes and a short black beard without any grey, wearing a white wrapped turban, a long dark "
            "indigo-blue robe with a plain sand-colored sash and brown leather sandals, carrying a small brown "
            "leather-bound notebook."
        ),
    },
    "HASAN_OLD": {
        "name": "Hasan (old age)",
        "explain": "The same man at about 70, after his release. White beard, same robe and notebook.",
        "block": (
            "Old Hasan: the same Arab scholar at about 70 with light-brown skin, a thin lined face, a high forehead, "
            "deep-set dark-brown eyes and a short white beard, wearing a white wrapped turban, a long faded "
            "indigo-blue robe with a sand-colored sash, holding a small brown leather-bound notebook."
        ),
    },
    "CALIPH": {
        "name": "The Caliph",
        "faceless": True,
        "explain": (
            "The feared, unpredictable ruler of Cairo. Shown only from behind, as a silhouette or with his face in "
            "deep shadow — that keeps him mysterious and respectful. Signature: plain all-white robes and his small "
            "grey donkey."
        ),
        "block": (
            "The Caliph: a slim young ruler of about 26, always seen from behind, as a silhouette or with his face "
            "in deep shadow so that only a glint of his eyes is visible, wearing plain flowing white robes and a "
            "simple white turban without any jewels; when outdoors he rides a small grey donkey with a plain brown "
            "leather saddle."
        ),
    },
}

SCENES = {
    1: {
        "chars": ["HASAN", "CALIPH"],
        "scene": (
            "A dim palace hall in Cairo in the year 1011 with carved wooden screens and oil lamps: Hasan stands "
            "tense before the Caliph, who sits on a low cushioned throne; heavy silence"
        ),
        "camera": "Wide shot from behind the Caliph's shoulder, Hasan facing the camera in warm lamplight",
    },
    2: {
        "chars": ["HASAN"],
        "scene": (
            "Hasan sits alone on the floor of a dark room, staring wide-eyed; a single thin beam of light falls "
            "through a tiny hole in the wooden shutter and lights his face"
        ),
        "camera": "Low-key lighting, strong beam of light, deep shadows",
    },
    3: {
        "scene": (
            "A dark room with one tiny hole in the shutter: on the opposite white wall appears an upside-down, "
            "colorful image of a sunlit medieval city with palm trees and domes"
        ),
    },
    4: {"style": "modern", "camera": "Extreme macro close-up, reflection in the glass lens"},
    6: {
        "chars": ["HASAN_YOUNG"],
        "scene": "Young Hasan reads by an oil lamp in a library in Basra, surrounded by stacks of manuscripts and scrolls",
    },
    8: {
        "chars": ["HASAN"],
        "scene": (
            "In a shaded courtyard in Basra, Hasan speaks confidently to a small group of men and points at a "
            "hand-drawn map of a winding river spread on a low table"
        ),
    },
    10: {
        "chars": ["CALIPH"],
        "scene": "The Caliph rides his small grey donkey alone through the dark, narrow streets of Cairo at night",
        "camera": "Wide shot from behind, moonlight and a few lanterns, long shadows",
    },
    12: {
        "chars": ["HASAN", "CALIPH"],
        "scene": (
            "At the gate of a village outside Cairo, the Caliph on his grey donkey, with a small procession behind "
            "him, greets the arriving Hasan, who bows his head respectfully"
        ),
        "camera": "Wide shot from behind the Caliph, golden afternoon light, dust in the air",
    },
    13: {
        "chars": ["HASAN"],
        "scene": "Hasan leads a group of engineers and workers south along the Nile with sailing boats and camels",
    },
    14: {
        "chars": ["HASAN"],
        "scene": (
            "Ancient Egyptian temples and colossal stone statues along the Nile at sunset; Hasan stands small in the "
            "foreground, looking up in awe"
        ),
        "camera": "Epic wide shot, low angle, warm sunset light",
    },
    15: {
        "chars": ["HASAN"],
        "scene": "Hasan stands on dark granite rocks at the roaring Nile cataracts near Aswan, doubt in his face",
    },
    16: {"style": "modern", "camera": "Aerial drone view, golden hour"},
    17: {
        "chars": ["HASAN"],
        "scene": "Hasan sits on a wooden boat sailing north on the Nile, head in his hands; storm clouds gather over distant Cairo",
    },
    18: {
        "chars": ["HASAN", "CALIPH"],
        "scene": "Hasan bows deeply before the Caliph in the palace hall; the Caliph's shadowed figure looms over him",
        "camera": "Side view, dramatic lamplight, long shadows",
    },
    19: {
        "chars": ["HASAN"],
        "scene": (
            "In a busy government office with low desks, Hasan suddenly scatters papers into the air and acts "
            "strangely; the clerks step back in alarm"
        ),
    },
    20: {
        "chars": ["HASAN"],
        "scene": (
            "Guards in plain robes carry crates of books out of a house in Cairo while Hasan watches silently from "
            "the doorway as they close the heavy wooden door"
        ),
    },
    21: {
        "chars": ["HASAN"],
        "scene": "A dark room with shuttered windows and a few thin beams of light; Hasan sits on the floor, deep in thought, his notebook open",
        "camera": "Low-key lighting, light beams, dust particles",
    },
    22: {
        "scene": (
            "Ancient Greek philosophers in long togas in a marble hall; thin glowing lines shoot out of one man's "
            "eyes toward objects, illustrating the old theory of sight"
        ),
    },
    23: {
        "chars": ["HASAN"],
        "scene": "In a sunny courtyard, Hasan shields his eyes from the bright sun; a soft glowing afterimage floats in the air",
    },
    24: {
        "chars": ["HASAN"],
        "scene": "Hasan carefully bores a tiny hole into a wooden shutter; a thin beam of light enters the dark room",
        "camera": "Close-up on his hands and face, strong light beam",
    },
    25: {
        "chars": ["HASAN"],
        "scene": (
            "On the white wall of a dark room appears an upside-down, colorful image of a street with people and "
            "palm trees; Hasan watches it in amazement"
        ),
    },
    28: {"style": "manuscript"},
    29: {
        "chars": ["HASAN"],
        "scene": "Hasan writes at a low wooden desk by candlelight, surrounded by stacks of notes, lenses and a small mirror",
    },
    31: {
        "scene": (
            "Split image: on the left a bright modern laboratory with researchers at microscopes, on the right a "
            "medieval scholar's desk with an oil lamp, lenses and manuscripts"
        ),
    },
    33: {
        "scene": (
            "The rocky hills outside Cairo at night under a full moon; a small grey donkey with a plain brown leather "
            "saddle stands alone on an empty path"
        ),
        "camera": "Wide shot, cold moonlight, lonely mood",
    },
    34: {
        "chars": ["HASAN"],
        "scene": "Hasan opens his front door to bright daylight; guards bring back his crates of books; relief in his face",
        "camera": "Backlit doorway, bright warm daylight streaming in",
    },
    35: {
        "chars": ["HASAN_OLD"],
        "scene": "Old Hasan copies a manuscript at a desk in the arcade of a mosque courtyard in Cairo; a few students watch",
    },
    36: {"camera": "Medium shot, candlelight, monks seen from the side and behind"},
    37: {"scene": "A 16th-century printing shop in Basel: a German scholar in a black coat holds up a freshly printed thick book next to a wooden press"},
    39: {"style": "modern", "camera": "Close-up of the hand and chalkboard, soft classroom light"},
    40: {"style": "modern", "camera": "Space view, sharp lunar detail, black sky"},
    41: {"style": "modern"},
    42: {"style": "modern"},
    43: {
        "chars": ["HASAN_OLD"],
        "scene": "Old Hasan stands at an open window, warm sunlight on his face, peaceful",
        "camera": "Medium close-up, golden light, gentle mood",
    },
}
