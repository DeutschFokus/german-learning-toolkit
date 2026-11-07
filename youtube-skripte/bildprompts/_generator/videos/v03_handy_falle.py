NUMBER = "03"
TITLE = "Die Handy-Falle – Warum Steve Jobs seinen Kindern das iPad verbot"
SCRIPT = "03-handy-falle.md"

STYLE = (
    "Cinematic semi-realistic digital illustration with photographic lighting, like a high-end animated "
    "documentary: deep blue and teal shadows with magenta and warm amber accents, shallow depth of field, "
    "soft bokeh, realistic proportions, modern 2010s–2020s settings, the same color grading in every image."
)
STYLE_ALT = {
    "retro": (
        "The same cinematic semi-realistic digital illustration, but set in a 1950s laboratory with warm "
        "sepia and faded green tones and soft film grain."
    ),
}
RULES_EXTRA = (
    "No app logos, no brand logos, no readable screen text or interface text. No real, identifiable "
    "person. Screens show only abstract colored shapes."
)
DEFAULT_CAMERA = "Cinematic medium shot, shallow depth of field, soft bokeh, moody blue light with warm accents"

CHARACTERS = {
    "VISIONARY": {
        "name": "The Visionary",
        "faceless": True,
        "explain": (
            "Stands in for the tech founder from the hook. He is a real person, so he is ALWAYS a silhouette "
            "or seen from behind. Signature: black mock-turtleneck, jeans, grey sneakers, round rimless glasses."
        ),
        "block": (
            "The Visionary: always a dark silhouette or seen from behind, never a clear face — a slim man in "
            "his mid-50s with short cropped grey hair and small round rimless glasses, wearing a black "
            "mock-turtleneck sweater, blue jeans and grey sneakers."
        ),
    },
    "JONAS": {
        "name": "Jonas (the viewer)",
        "explain": (
            "The everyday hero of the video — the viewer's mirror image. Every 'you' scene shows Jonas. "
            "Signature: dark-green hoodie, freckles, messy dark-brown hair, phone in a matte grey case."
        ),
        "block": (
            "Jonas: a German man of 28, slim, light skin with a few freckles across the nose, short messy "
            "dark-brown hair, light stubble and tired grey-blue eyes. He wears a dark-green hoodie over a white "
            "T-shirt, black jeans and white sneakers, and uses a black smartphone in a matte grey case."
        ),
    },
    "LENA": {
        "name": "Lena (the teenager)",
        "explain": "The teenage daughter, used for all scenes about children. Signature: lavender sweatshirt, black ponytail, clear phone case.",
        "block": (
            "Lena: a German girl of 14, slim, light-olive skin, long straight black hair in a low ponytail and "
            "large dark-brown eyes. She wears an oversized lavender sweatshirt and light-blue jeans and uses a "
            "phone in a clear transparent case."
        ),
    },
    "MARKUS": {
        "name": "Markus (Lena's father)",
        "explain": "Lena's father, used for the parent scenes. Signature: navy sweater, grey beard, rectangular glasses.",
        "block": (
            "Markus: Lena's father, a German man of 47, medium build, light skin, short receding "
            "salt-and-pepper hair, a short grey beard and rectangular dark-framed glasses. He wears a navy-blue "
            "knit sweater over a light-blue collared shirt and beige chinos."
        ),
    },
    "MAYA": {
        "name": "Maya (study participant)",
        "explain": "The student in the phone-in-the-room experiment (two scenes). Signature: mustard-yellow cardigan and scrunchie.",
        "block": (
            "Maya: a university student of 22, medium-brown skin, curly black hair tied up with a "
            "mustard-yellow scrunchie and round thin metal-rimmed glasses. She wears a mustard-yellow cardigan "
            "over a plain white top."
        ),
    },
}

SCENES = {
    1: {
        "chars": ["VISIONARY"],
        "scene": (
            "The Visionary stands on a dark stage, seen as a silhouette from slightly behind, holding up a "
            "glowing tablet in one hand; a single spotlight from above, the audience only dark shapes"
        ),
        "camera": "Wide shot from the back of the hall, strong spotlight, glowing tablet as the brightest point",
    },
    2: {
        "scene": (
            "A luxurious modern home at night: a family of four eats dinner at a long wooden table, no phones "
            "or screens anywhere, warm candlelight, faces softly out of focus"
        ),
    },
    3: {
        "chars": ["JONAS"],
        "scene": (
            "Extreme close-up of Jonas's grey-blue eye reflecting a glowing phone screen; at the bottom of the "
            "frame his thumb hovers over the glass"
        ),
        "camera": "Macro close-up, blue screen glow on the skin, everything else dark",
    },
    4: {
        "scene": (
            "A newsroom-style office at night in 2010: a journalist in a white shirt, seen from behind, writes "
            "on a notepad at his desk; city lights through the window"
        ),
    },
    5: {
        "chars": ["VISIONARY"],
        "scene": (
            "The Visionary, seen from behind as a silhouette with soft rim light, turns his head away from a "
            "glowing tablet lying on a table in front of him"
        ),
        "camera": "Medium shot from behind, soft rim light, dark background",
    },
    6: {
        "chars": ["LENA", "MARKUS"],
        "scene": (
            "Lena sits at the kitchen table on her 14th birthday and unwraps a small box with her first "
            "smartphone; a birthday cake with lit candles stands in front of her; Markus watches from the side "
            "with a careful smile"
        ),
        "camera": "Medium shot, warm candlelight mixed with the cool phone glow",
    },
    8: {
        "scene": (
            "A man in a grey hoodie speaks into a microphone on a dark conference stage, lit by a single "
            "spotlight and seen from the side with his face in shadow; an uneasy audience in the dark"
        ),
    },
    10: {
        "scene": (
            "A man in a dark suit stands alone on a balcony high above glittering city lights at night, seen "
            "from behind, head bowed in regret"
        ),
    },
    11: {
        "chars": ["JONAS"],
        "scene": (
            "Close-up of Jonas's thumb, with the sleeve of his dark-green hoodie visible, pulling down on a "
            "phone screen; a spinning refresh circle and a glowing motion trail"
        ),
        "camera": "Close-up from above, glowing screen, motion blur on the thumb",
    },
    13: {
        "chars": ["JONAS"],
        "scene": (
            "A giant glowing hand made of light holds a tiny Jonas on strings made of notification bubbles, "
            "like a marionette, against a dark background"
        ),
        "camera": "Wide surreal composition, Jonas small in the center, dramatic light from above",
    },
    14: {
        "style": "retro",
        "scene": (
            "A 1950s psychology laboratory: a pigeon stands in a wooden box with a small key and a grain "
            "dispenser; a scientist in a white lab coat, seen from behind, takes notes on a clipboard"
        ),
    },
    15: {"style": "retro"},
    16: {"style": "retro"},
    17: {"scene": "A smartphone morphing into a slot machine lever, mirrored composition, neon glow, no symbols or numbers on the machine"},
    21: {
        "chars": ["JONAS"],
        "scene": (
            "Jonas sits at a kitchen table late at night, staring at his phone lying face up in front of him, "
            "waiting; a faint notification glow lights his face"
        ),
    },
    22: {
        "chars": ["JONAS"],
        "scene": "Close-up of Jonas's hand, dark-green hoodie sleeve visible, placing his phone face down on a wooden table with a determined gesture",
        "camera": "Close-up, warm side light, decisive moment",
    },
    23: {
        "chars": ["JONAS"],
        "scene": (
            "A four-panel montage of one day in Jonas's life: the alarm clock in the morning, breakfast, a ride "
            "on the bus, his office desk — in every panel he is holding his phone"
        ),
        "camera": "Four equal panels side by side, consistent lighting, Jonas identical in every panel",
    },
    24: {
        "chars": ["JONAS"],
        "scene": (
            "Jonas sits at an office desk surrounded by several glowing screens and his phone; his attention "
            "visually shatters like fragments of broken glass floating around his head"
        ),
    },
    26: {
        "chars": ["MAYA"],
        "scene": (
            "A bright university exam room with students at single desks; in the foreground Maya writes her "
            "test while her phone lies face down beside her paper, surrounded by a faint glow of distraction"
        ),
    },
    27: {
        "chars": ["MAYA"],
        "scene": "The same exam room, brighter and warmer: Maya writes with clear focus, and no phone is anywhere in sight",
        "camera": "Medium shot, warm bright light, calm atmosphere",
    },
    28: {
        "chars": ["JONAS"],
        "scene": (
            "Jonas stands in a quiet living room touching his empty jeans pocket, startled; a ghostly ripple of "
            "vibration waves floats in the air beside his leg"
        ),
    },
    29: {
        "chars": ["LENA"],
        "scene": (
            "Lena lies in bed in a dark bedroom at night, her face lit blue by her phone, exhausted eyes; an "
            "analog wall clock without numbers shows its hands near two o'clock"
        ),
        "camera": "Medium close-up, only the cold phone light, deep shadows",
    },
    31: {
        "chars": ["MARKUS", "LENA"],
        "scene": (
            "Markus and Lena sit at opposite ends of a living-room sofa, both looking at their own phones; "
            "cold blue light and visible emotional distance between them"
        ),
        "camera": "Wide shot, symmetrical, lots of empty sofa between them",
    },
    33: {
        "chars": ["JONAS"],
        "scene": (
            "Close-up of Jonas's hands switching off notification toggles on his phone; notification bubbles "
            "fly away from the screen like a flock of birds"
        ),
    },
    34: {
        "chars": ["JONAS"],
        "scene": "Jonas holds his phone; its screen fades from vivid colors on one side to calm grayscale on the other",
        "camera": "Close-up over the shoulder, calm soft light",
    },
    35: {
        "chars": ["JONAS"],
        "scene": (
            "Jonas sleeps peacefully in a dim bedroom; an analog alarm clock stands on the nightstand; through "
            "the open bedroom door his phone charges on a hallway shelf outside"
        ),
        "camera": "Wide shot, calm night-blue light, the phone glow small in the background",
    },
    36: {
        "chars": ["JONAS"],
        "scene": (
            "Jonas works with full focus at a desk with a laptop and books; through an open door behind him "
            "his phone lies on a shelf in the next room"
        ),
    },
    37: {
        "chars": ["JONAS"],
        "scene": "Over-the-shoulder view of Jonas holding his phone; the home screen shows only a few simple, plain tool icons on a calm background",
    },
    38: {
        "chars": ["JONAS"],
        "scene": "Jonas pauses before unlocking his phone, his thumb hovering, with a thoughtful expression by a window in soft morning light",
    },
    39: {
        "chars": ["MARKUS", "LENA"],
        "scene": (
            "Markus and Lena sit together at the kitchen table building a wooden model house and laughing; "
            "golden afternoon light; no phones anywhere"
        ),
        "camera": "Medium shot, warm golden light, happy atmosphere",
    },
    40: {
        "chars": ["JONAS"],
        "scene": "Jonas walks away across a sunny park, seen from behind, leaving his phone lying in the grass in the foreground",
        "camera": "Low angle from the grass, phone sharp in the foreground, Jonas walking into the sunlight",
    },
}
