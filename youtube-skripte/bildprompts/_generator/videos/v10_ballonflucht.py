NUMBER = "10"
TITLE = "Die Ballonflucht – 28 Minuten bis zur Freiheit"
SCRIPT = "10-ballonflucht.md"

STYLE = (
    "Cinematic semi-realistic digital illustration of East Germany in 1979, muted greys, olive greens and "
    "browns by day, cold night blues lit by warm orange burner flames and harsh white searchlights, soft film "
    "grain, realistic proportions."
)
STYLE_ALT = {
    "modern": "Clean present-day photo-realistic look, natural museum light, crisp detail.",
    "diagram": "Simple clean educational illustration on a dark-blue background, soft glow, no labels or arrows with text.",
}
RULES_EXTRA = (
    "The two families are real people: never show their faces — only from behind, as silhouettes, in deep "
    "shadow or as hands. No flags, no state emblems or national symbols, no insignia on uniforms, no weapons "
    "fired, no blood. No brand logos on cars or products."
)
DEFAULT_CAMERA = "Cinematic medium-wide shot, moody natural light, soft film grain"

CHARACTERS = {
    "PETER": {
        "name": "Peter (the burner man)",
        "faceless": True,
        "explain": (
            "Electrician and trained aircraft mechanic who built the burner. Real person, so never his face. "
            "Signature: worn brown leather jacket."
        ),
        "block": (
            "Peter: an East German man of about 37, stocky build, short dark-brown hair with a side parting, always "
            "seen from behind, as a silhouette or with his face in deep shadow — never his face; wearing a worn "
            "brown leather jacket over a beige shirt, dark-grey trousers and brown work boots."
        ),
    },
    "GUENTER": {
        "name": "Günter (the tailor)",
        "faceless": True,
        "explain": (
            "The young mason who sewed the balloons night after night. Real living person, so never his face. "
            "Signature: mustard-yellow knitted sweater."
        ),
        "block": (
            "Günter: a young East German man of about 24, tall and slim, thick wavy brown hair over the collar, "
            "always seen from behind, as a silhouette or with his face in deep shadow — never his face; wearing a "
            "mustard-yellow knitted sweater, faded blue jeans and grey canvas shoes."
        ),
    },
    "DORIS": {
        "name": "Doris (Peter's wife)",
        "faceless": True,
        "explain": "Real person, never her face. Signature: dark-green hooded parka.",
        "block": (
            "Doris: an East German woman of about 37, medium height, short dark-blonde wavy hair, always seen from "
            "behind or with her face in deep shadow — never her face; wearing a dark-green hooded parka, long dark-"
            "brown trousers and brown boots."
        ),
    },
    "PETRA": {
        "name": "Petra (Günter's wife)",
        "faceless": True,
        "explain": "Real person, never her face. Signature: red cardigan and a long single braid.",
        "block": (
            "Petra: a young East German woman of about 24, slim, long light-brown hair in a single braid down her "
            "back, always seen from behind or with her face in deep shadow — never her face; wearing a buttoned-up "
            "red knitted cardigan over a cream blouse and a long grey skirt to the ankles with dark tights."
        ),
    },
    "BOYS": {
        "name": "The two older boys",
        "faceless": True,
        "explain": "Peter and Doris's sons, about 15 and 11. Real people, faces always hidden. Signature: navy and brown anoraks.",
        "block": (
            "The two older boys: two East German brothers of about 15 and 11, the elder taller with dark-brown hair "
            "in a navy-blue anorak, the younger with lighter brown hair in a brown anorak, both in dark trousers; "
            "always seen from behind or with faces hidden."
        ),
    },
    "LITTLE_ONES": {
        "name": "The two little ones",
        "faceless": True,
        "explain": "Günter and Petra's small sons, a pre-schooler and a toddler. Faces always hidden. Signature: yellow-and-brown checked wool blanket.",
        "block": (
            "The two little ones: two small boys, about 5 and 2 years old, wrapped together in a red-and-white "
            "checked wool blanket, with knitted blue woolly hats; always seen from behind or with faces hidden in "
            "the blanket."
        ),
    },
    "BALLOON": {
        "name": "The escape balloon",
        "kind": "element",
        "explain": (
            "The third balloon that made it to the West. Its patchwork of four fabrics is the visual hook of the video "
            "— keep it identical in every image."
        ),
        "block": (
            "The escape balloon: a huge home-made hot-air balloon about 28 metres tall, its envelope sewn from many "
            "uneven vertical patchwork strips of red-and-white striped bed ticking, dark-blue umbrella fabric, olive-"
            "green tent nylon and beige taffeta with visible crooked seams; below it hangs a small square platform "
            "of thin grey steel sheet with four corner posts and a simple rope railing, with a home-made burner of "
            "four propane gas bottles and pipes in the middle."
        ),
    },
    "BALLOON_SMALL": {
        "name": "The second balloon",
        "kind": "element",
        "explain": "The smaller taffeta balloon of the failed first flight. Different colors so it is never confused with the final one.",
        "block": (
            "The second balloon: a smaller home-made hot-air balloon with an envelope of shiny beige and light-brown "
            "taffeta panels with visible seams, hanging above a small square platform of thin grey steel sheet with "
            "a simple home-made burner of two propane gas bottles."
        ),
    },
    "INVESTIGATOR": {
        "name": "The investigator",
        "explain": (
            "A fictional state-security officer who stands for the whole Stasi hunt. Not a real person, so his face "
            "may be shown. Signature: long grey trench coat and thin wire-rimmed glasses."
        ),
        "block": (
            "The investigator: a fictional East German security officer of about 50, thin and pale with receding grey "
            "hair combed back, thin wire-rimmed glasses and thin lips, wearing a grey suit, a white shirt with a "
            "narrow grey tie and a long grey trench coat."
        ),
    },
}

ALL_ADULTS = ["PETER", "GUENTER", "DORIS", "PETRA"]

SCENES = {
    1: {
        "chars": ["BALLOON"],
        "scene": "The escape balloon rises above a dark Thuringian forest at night, the small burner flame glowing beneath it",
        "camera": "Wide low-angle shot from the forest floor, starry sky, warm flame against cold night",
    },
    2: {
        "chars": ["BALLOON", *ALL_ADULTS, "BOYS", "LITTLE_ONES"],
        "scene": (
            "Close view of the thin steel platform under the escape balloon at night: four adults and four children "
            "cling to the ropes, all seen from behind or with faces in deep shadow"
        ),
        "camera": "Close shot from behind and below the platform, burner glow from above",
    },
    6: {
        "chars": ["PETER", "GUENTER"],
        "scene": "On a plastics factory floor, Peter and Günter talk quietly during a break, seen from behind, machines around them",
    },
    7: {
        "chars": ["PETER", "DORIS"],
        "scene": "Peter and Doris sit on a sofa in a small living room with drawn curtains, seen from behind, lit by the blue glow of a television",
    },
    10: {
        "chars": ["PETER", "GUENTER"],
        "scene": "Peter and Günter stand in a backyard at night, seen from behind; Peter points up at the starry sky",
    },
    11: {
        "chars": ["PETER"],
        "scene": "Peter secretly reads a technical book at a kitchen table at night, curtains closed, a pencil and sketches beside him",
        "camera": "Over-the-shoulder shot from behind, single warm lamp",
    },
    12: {"style": "diagram"},
    13: {
        "chars": ["GUENTER"],
        "scene": "Günter sews long fabric panels on an old black mechanical sewing machine in a small attic room late at night",
        "camera": "Shot from behind and the side, single bare bulb",
    },
    14: {
        "chars": ["PETER", "GUENTER"],
        "scene": "A limp home-made cotton balloon envelope lies flat on a forest clearing at night; Peter and Günter look at it in disappointment",
    },
    15: {
        "chars": ["PETER"],
        "scene": "In a large department store in Leipzig, Peter, seen from behind, buys big rolls of shiny beige taffeta at a fabric counter",
    },
    16: {
        "chars": ["GUENTER", "PETRA"],
        "scene": "Günter and Petra sit at a kitchen table holding hands, seen from behind; two pairs of small children's shoes stand by the door",
    },
    17: {
        "chars": ["BALLOON_SMALL", "PETER", "DORIS", "BOYS"],
        "scene": "On a July night in 1979, the second balloon lifts off from a forest clearing with Peter, Doris and the two older boys on its platform",
        "camera": "Wide shot from behind, burner glow, mist",
    },
    18: {
        "chars": ["BALLOON_SMALL"],
        "scene": "The second balloon sinks through cold mist toward the dark treetops of a forest",
    },
    19: {
        "chars": ["PETER", "DORIS", "BOYS"],
        "scene": "Peter, Doris and the two boys creep through a dark forest, seen from behind; a fence and warning signs far in the distance",
    },
    20: {
        "chars": ["BALLOON_SMALL"],
        "scene": "The abandoned second balloon hangs draped over trees in a forest at dawn; a gas bottle lies on the ground",
    },
    21: {"scene": "A hunter in green clothing discovers a huge pile of shiny beige taffeta and ropes in the forest in morning fog"},
    22: {
        "chars": ["INVESTIGATOR"],
        "scene": "In a grey office, the investigator examines pieces of beige taffeta and a home-made burner spread out on a table",
        "camera": "Medium shot, cold fluorescent light",
    },
    25: {
        "chars": ["PETER"],
        "scene": "Peter, seen from behind, looks nervously through a gap in the curtains at a grey car parked on the street at night",
    },
    26: {
        "chars": ["PETER", "GUENTER"],
        "scene": "Peter and Günter shake hands firmly in a dim garage, seen from the side with faces in shadow; a new roll of fabric between them",
    },
    28: {
        "scene": (
            "A montage of small fabric shop counters in different towns: hands buying single rolls of red-and-white "
            "striped bed ticking, dark-blue umbrella fabric, olive-green nylon and beige taffeta"
        ),
    },
    29: {
        "chars": ["GUENTER"],
        "scene": (
            "Günter sits at an old sewing machine at night, surrounded by a sea of patchwork panels in red-and-white "
            "ticking, dark blue, olive green and beige"
        ),
        "camera": "Shot from behind, single lamp, fabric everywhere",
    },
    30: {
        "chars": ["GUENTER", "PETER"],
        "scene": "In a cramped attic at night, Günter sews while Peter checks the seams of a huge patchwork panel with a flashlight",
    },
    31: {
        "chars": ["PETER"],
        "scene": "Peter welds a home-made propane burner in a garage, sparks flying, gas bottles on the floor, face hidden behind a welding mask",
    },
    32: {
        "chars": ["PETER", "GUENTER"],
        "scene": "Peter and Günter sit at a table listening intently to an old radio, seen from behind; a calendar page hangs on the wall",
    },
    33: {
        "chars": ["PETER", "DORIS", "BOYS"],
        "scene": "In a dark apartment at night, Peter, Doris and the two boys slip out of the door with one small bag, glancing back at their home",
    },
    34: {
        "chars": [*ALL_ADULTS, "BOYS", "LITTLE_ONES"],
        "scene": "In a night forest clearing, the two families quietly unload equipment from a small car; the children are wrapped up warmly",
        "camera": "Wide shot from behind, only moonlight, everyone in silhouette",
    },
    35: {
        "chars": ["BALLOON", "PETER"],
        "scene": "Peter fires the burner; a roaring flame blasts into the opening of the huge patchwork envelope lying on the ground at night",
        "camera": "Low shot from behind Peter, bright orange flame, fabric glowing",
    },
    36: {
        "chars": ["BALLOON"],
        "scene": "The escape balloon floats high over dark forests and tiny village lights, the people on the platform as small silhouettes",
        "camera": "Wide aerial shot, cold blue night, small warm flame",
    },
    37: {
        "chars": ["LITTLE_ONES", "BOYS", "PETRA", "DORIS"],
        "scene": "On the thin steel platform, the children cling to the legs of the two women, frozen breath in the dark, all seen from behind",
        "camera": "Close shot from behind, burner glow from above",
    },
    38: {
        "chars": ["BALLOON"],
        "scene": "Far below the escape balloon, white searchlight beams from watchtowers sweep the night sky",
        "camera": "High angle from beside the balloon looking down",
    },
    39: {
        "chars": ["PETER"],
        "scene": "The burner flame flickers weakly; Peter shakes an almost empty gas bottle, his face in shadow",
        "camera": "Close-up of hands and bottle, weak orange light",
    },
    40: {
        "chars": ["DORIS", "PETRA", "BOYS", "LITTLE_ONES"],
        "scene": "The women and children hide wrapped in blankets at the edge of a dark forest, seen from behind, the first grey light of dawn",
    },
    41: {
        "chars": ["PETER", "GUENTER"],
        "scene": "Peter and Günter walk along a dark country road, seen from behind; the headlights of a police car approach",
    },
    42: {
        "chars": ["PETER", "GUENTER"],
        "scene": "Two West German police officers in plain green uniforms without insignia stand by their patrol car at night, talking to Peter and Günter, who are seen from behind",
    },
    43: {
        "chars": ["BALLOON", *ALL_ADULTS],
        "scene": "Dawn over a Bavarian field: the deflated escape balloon lies spread on the grass while the adults embrace, seen from behind",
        "camera": "Wide shot, soft pink dawn light",
    },
    44: {
        "chars": ["INVESTIGATOR"],
        "scene": "In a grey security office, the investigator and two colleagues read files and a newspaper without readable text, angry faces",
    },
    45: {
        "chars": ["INVESTIGATOR"],
        "scene": "The investigator knocks at an apartment door in an East German block of flats; a woman stands in the doorway in shadow",
    },
    47: {
        "chars": ["BALLOON"],
        "style": "modern",
        "scene": "A museum hall with the huge patchwork envelope of the escape balloon hanging on display; visitors look up, seen from behind",
    },
    50: {
        "chars": ["BALLOON"],
        "scene": "The escape balloon drifts away into a soft sunrise sky; calm end frame with empty space for end-screen elements",
        "camera": "Wide shot, warm sunrise, lots of empty sky",
    },
}
