# Charakter-Bibel – alle Videos

Diese Bibel sorgt dafür, dass jede Figur in jedem Bild gleich aussieht. Das Prinzip: Jede Figur hat **eine feste Beschreibung**, die **wortgleich** in jedem Prompt steht, in dem sie vorkommt. Du musst nichts ergänzen – die Prompts in den Skript-Dateien sind komplett. Diese Datei erklärt die Figuren, zeigt, wo sie vorkommen, und gibt dir Werkzeuge, falls Copilot trotzdem einmal abweicht.

## So bleiben die Figuren in Copilot gleich

1. **Ein Chat pro Video.** Für jedes Video einen neuen Copilot-Chat öffnen und alle Bilder dieses Videos dort erstellen.
2. **Setup-Nachricht zuerst.** Jedes Skript hat oben eine Setup-Nachricht mit Stil und allen Figuren. Als Erstes einfügen – Copilot antwortet mit „Ready“.
3. **Referenzblätter erstellen.** Für jede Figur den Referenzblatt-Prompt einfügen (zeigt die Figur von vorne, seitlich und hinten). Das beste Ergebnis speichern.
4. **Referenzbild nutzen (sehr wirksam).** Wenn eine Figur in vielen Bildern vorkommt: das gespeicherte Referenzblatt in den Chat hochladen und den Prompt „Referenzbild verwenden“ (unten) davor setzen.
5. **Prompts der Reihe nach einfügen.** Jeder Prompt beginnt mit „Create an image…“, damit Copilot sofort ein Bild erstellt, und enthält die komplette Figurenbeschreibung.
6. **Kleidung ist der stärkste Anker.** Copilot hält Kleidung, Farben und Accessoires zuverlässiger konstant als Gesichtszüge. Deshalb hat jede Figur feste Erkennungszeichen (z. B. Markus' bordeauxroter Schal, Daniels navyblaue Steppjacke). Beim Prüfen der Bilder zuerst darauf achten.
7. **Gesichter der Gelehrten bleiben verborgen.** Muslimische Gelehrte und historische Frauen werden nie mit Gesicht gezeigt – aus Respekt und weil Rückenansichten automatisch einheitlicher wirken. Der Prophet wird nie dargestellt.
8. **Lieber neu erstellen als nachbessern.** Wenn ein Bild eine Figur verfälscht: einfach denselben Prompt noch einmal senden oder den Korrektur-Prompt nutzen.

## Wenn etwas schiefgeht

**Eine Figur sieht plötzlich anders aus** – diesen Text einfügen und die Beschreibung der Figur aus dieser Bibel an der markierten Stelle einsetzen:

```text
Please create the last image again with exactly the same scene and composition, but correct the character so that it matches this description exactly: [PASTE THE CHARACTER DESCRIPTION HERE]. Change nothing else.
```

**Referenzbild verwenden** – Referenzblatt hochladen, dann diesen Text plus den Bild-Prompt senden:

```text
Use the uploaded reference image as the character reference: keep this person's face, hair, facial hair, skin tone, body shape, clothing and colors exactly the same in the following image. [PASTE THE IMAGE PROMPT HERE]
```

**Copilot antwortet nur mit Text** – einfach „Please create the image now.“ senden.

**Copilot lehnt ein Bild ab** – den Prompt noch einmal senden; meistens klappt es beim zweiten Versuch. Sonst das auslösende Wort entschärfen (z. B. „soldiers“ → „uniformed men“, „burning“ → „smoke rising over“). Geldscheine sind in allen Prompts schon als „stylized, fictional designs“ markiert, damit sie nicht als echtes Geld gelten.

**Copilot liefert 3:2 statt 16:9** – im Schnittprogramm leicht reinzoomen. Bei Ken-Burns-Bewegung fällt der Unterschied nicht auf.

**Copilot erfindet Text auf Schildern** – den Prompt erneut senden oder im Schnitt mit Unschärfe oder einem Ausschnitt überdecken.

## Figuren, die in mehreren Videos vorkommen

- **Yusuf (moderner Erzähl-Charakter)** – Skript 1, Skript 10 und Skript 11
- **Heinrich Krüger – 1923/24** – Skript 2 und Skript 5
- **Elisabeth Krüger – 1923** – Skript 2 und Skript 5
- **Heinrich Krüger – 1913** – Skript 2 und Skript 5
- **Elisabeth Krüger – 1913 bis 1915** – Skript 2 und Skript 5
- **Greta und Karl Krüger – 1913** – Skript 2 und Skript 5
- **Daniel (der Einkäufer)** – Skript 3 und Skript 13
- **Markus (der Pendler)** – Skript 4 und Skript 9

Diese Figuren verbinden die Videos miteinander. Wer beide Videos sieht, erkennt sie wieder – deshalb ist ihre Beschreibung in allen Skripten exakt gleich.

## Alle Figuren nach Video

### Skript 1 – Das Haus der Weisheit

**Stil:**

```text
cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look
```

**Setup-Nachricht für den Copilot-Chat dieses Videos:**

```text
In this chat I will ask you to create the images for one video, one by one. Please apply these rules to every image in this chat:
1. Format: always 16:9 widescreen landscape.
2. Visual style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look.
3. These recurring characters must look exactly the same every time they appear:
- Yusuf, a 22-year-old man of Turkish heritage who lives in Germany, with warm light-brown skin, short dark-brown wavy hair with a neat side part, a short well-groomed black beard, dark brown eyes, thick straight eyebrows and a slim athletic build, wearing a mustard-yellow hoodie over a plain white T-shirt, dark navy jeans, white sneakers and a slim black wristwatch on his left wrist
- the Baghdad mathematician, an elderly ninth-century scholar who is always shown from behind, in silhouette or with his face hidden in deep shadow (his face is never visible), tall and slightly stooped, wearing a long deep indigo-blue robe with a thin gold-embroidered border, a round cream-white turban with a loose tail hanging down his back and a silver ring with a dark red stone on his right ring finger
- the Cairo scientist, an eleventh-century scholar in his forties who is always shown from behind, in silhouette or with his face hidden in deep shadow (his face is never visible), broad-shouldered and of medium height, wearing a sand-beige linen robe with a dark brown sash and a dark olive-green turban
- the Córdoba physician, a slim tenth-century doctor who is always shown from behind or with his face turned away (his face is never visible), wearing a crisp white robe over a pale grey under-tunic, a white turban with a light-grey band and a small brown leather pouch of instruments at his belt
- Fatima, a young ninth-century woman from Fès who is always seen from behind or from a distance (her face is never visible), wearing a long flowing deep emerald-green robe, a modest cream-colored headscarf that covers her hair and shoulders and a woven golden-brown belt
- the Córdoba flyer, an older Andalusian inventor who is always shown from behind or in silhouette (his face is never visible), wearing a rust-red tunic, brown trousers and a white turban, with large handmade wings of cream silk and brown eagle feathers on a light wooden frame strapped to his arms
- the travelling astronomer, an eleventh-century scholar in his fifties who is always shown from behind or in silhouette (his face is never visible), wearing a dark charcoal-grey travelling cloak over a white robe and a black turban, carrying a polished brass astrolabe
4. Characters described as never showing their face are always shown from behind, in silhouette or with the face in deep shadow.
5. No captions, titles, logos or watermarks.
Please do not create an image yet – just reply "Ready". My image requests follow in the next messages.
```

#### Yusuf (moderner Erzähl-Charakter)

Der moderne Erzähl-Charakter der Islam-Reihe (Skript 1 und 10): ein 22-jähriger Student mit türkischen Wurzeln, der in Deutschland lebt. Er taucht in allen Szenen von heute auf – Handy, Laptop, Hörsaal, Schreibtisch – und gibt den Zuschauern eine feste Bezugsperson. Erkennungszeichen: senfgelber Hoodie, kurzer schwarzer Bart, schwarze Armbanduhr am linken Handgelenk.

**Kommt vor in:** Thumbnail, Bild 01, Bild 03, Bild 25, Bild 45, Bild 82, Bild 89

**Feste Beschreibung:**

```text
Yusuf, a 22-year-old man of Turkish heritage who lives in Germany, with warm light-brown skin, short dark-brown wavy hair with a neat side part, a short well-groomed black beard, dark brown eyes, thick straight eyebrows and a slim athletic build, wearing a mustard-yellow hoodie over a plain white T-shirt, dark navy jeans, white sneakers and a slim black wristwatch on his left wrist
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Yusuf, a 22-year-old man of Turkish heritage who lives in Germany, with warm light-brown skin, short dark-brown wavy hair with a neat side part, a short well-groomed black beard, dark brown eyes, thick straight eyebrows and a slim athletic build, wearing a mustard-yellow hoodie over a plain white T-shirt, dark navy jeans, white sneakers and a slim black wristwatch on his left wrist. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Al-Khwarizmi – der Mathematiker aus Bagdad

Der Mathematiker aus Bagdad (Skript 1). Wird aus Respekt nie mit Gesicht gezeigt – nur von hinten, als Silhouette oder als Hände. Erkennbar an: indigoblaues Gewand mit Goldsaum, runder cremeweißer Turban, Silberring mit dunkelrotem Stein.

**Kommt vor in:** Thumbnail, Bild 02, Bild 18, Bild 26, Bild 31

**Feste Beschreibung:**

```text
the Baghdad mathematician, an elderly ninth-century scholar who is always shown from behind, in silhouette or with his face hidden in deep shadow (his face is never visible), tall and slightly stooped, wearing a long deep indigo-blue robe with a thin gold-embroidered border, a round cream-white turban with a loose tail hanging down his back and a silver ring with a dark red stone on his right ring finger
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the Baghdad mathematician, an elderly ninth-century scholar who is always shown from behind, in silhouette or with his face hidden in deep shadow (his face is never visible), tall and slightly stooped, wearing a long deep indigo-blue robe with a thin gold-embroidered border, a round cream-white turban with a loose tail hanging down his back and a silver ring with a dark red stone on his right ring finger. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Ibn al-Haytham – der Wissenschaftler aus Kairo

Der Vater der Optik und der Camera obscura (Skript 1). Nie mit Gesicht. Erkennbar an: sandbeiges Leinengewand, dunkelbraune Schärpe, olivgrüner Turban.

**Kommt vor in:** Bild 38, Bild 39, Bild 41, Bild 43

**Feste Beschreibung:**

```text
the Cairo scientist, an eleventh-century scholar in his forties who is always shown from behind, in silhouette or with his face hidden in deep shadow (his face is never visible), broad-shouldered and of medium height, wearing a sand-beige linen robe with a dark brown sash and a dark olive-green turban
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the Cairo scientist, an eleventh-century scholar in his forties who is always shown from behind, in silhouette or with his face hidden in deep shadow (his face is never visible), broad-shouldered and of medium height, wearing a sand-beige linen robe with a dark brown sash and a dark olive-green turban. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Al-Zahrawi – der Arzt aus Córdoba

Der Chirurg aus Córdoba mit über 200 Instrumenten (Skript 1). Nie mit Gesicht. Erkennbar an: strahlend weißes Gewand, weißer Turban mit hellgrauem Band, Ledertasche mit Instrumenten am Gürtel.

**Kommt vor in:** Bild 48

**Feste Beschreibung:**

```text
the Córdoba physician, a slim tenth-century doctor who is always shown from behind or with his face turned away (his face is never visible), wearing a crisp white robe over a pale grey under-tunic, a white turban with a light-grey band and a small brown leather pouch of instruments at his belt
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the Córdoba physician, a slim tenth-century doctor who is always shown from behind or with his face turned away (his face is never visible), wearing a crisp white robe over a pale grey under-tunic, a white turban with a light-grey band and a small brown leather pouch of instruments at his belt. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Fatima al-Fihri – die Gründerin aus Fès

Gründerin der ältesten noch bestehenden Universität der Welt (Skript 1). Immer von hinten oder aus der Ferne, Gesicht nie sichtbar. Erkennbar an: smaragdgrünes Gewand, cremefarbenes Kopftuch, goldbrauner geflochtener Gürtel.

**Kommt vor in:** Bild 60, Bild 61

**Feste Beschreibung:**

```text
Fatima, a young ninth-century woman from Fès who is always seen from behind or from a distance (her face is never visible), wearing a long flowing deep emerald-green robe, a modest cream-colored headscarf that covers her hair and shoulders and a woven golden-brown belt
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: Fatima, a young ninth-century woman from Fès who is always seen from behind or from a distance (her face is never visible), wearing a long flowing deep emerald-green robe, a modest cream-colored headscarf that covers her hair and shoulders and a woven golden-brown belt. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Abbas ibn Firnas – der Flieger aus Córdoba

Der Mann mit den selbstgebauten Flügeln (Skript 1). Nur von hinten oder als Silhouette. Erkennbar an: rostrote Tunika, weißer Turban, Flügel aus cremefarbener Seide und braunen Adlerfedern.

**Kommt vor in:** Bild 65, Bild 66

**Feste Beschreibung:**

```text
the Córdoba flyer, an older Andalusian inventor who is always shown from behind or in silhouette (his face is never visible), wearing a rust-red tunic, brown trousers and a white turban, with large handmade wings of cream silk and brown eagle feathers on a light wooden frame strapped to his arms
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the Córdoba flyer, an older Andalusian inventor who is always shown from behind or in silhouette (his face is never visible), wearing a rust-red tunic, brown trousers and a white turban, with large handmade wings of cream silk and brown eagle feathers on a light wooden frame strapped to his arms. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Al-Biruni – der Gelehrte, der die Erde vermaß

Der Astronom, der vom Berg aus die Größe der Erde berechnete (Skript 1). Nur von hinten oder als Silhouette. Erkennbar an: anthrazitgrauer Reisemantel, schwarzer Turban, Messing-Astrolabium.

**Kommt vor in:** Bild 70, Bild 73

**Feste Beschreibung:**

```text
the travelling astronomer, an eleventh-century scholar in his fifties who is always shown from behind or in silhouette (his face is never visible), wearing a dark charcoal-grey travelling cloak over a white robe and a black turban, carrying a polished brass astrolabe
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the travelling astronomer, an eleventh-century scholar in his fifties who is always shown from behind or in silhouette (his face is never visible), wearing a dark charcoal-grey travelling cloak over a white robe and a black turban, carrying a polished brass astrolabe. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

### Skript 2 – Warum Deutschland reich ist, aber die Deutschen nicht

**Stil:**

```text
cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed
```

**Setup-Nachricht für den Copilot-Chat dieses Videos:**

```text
In this chat I will ask you to create the images for one video, one by one. Please apply these rules to every image in this chat:
1. Format: always 16:9 widescreen landscape.
2. Visual style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed.
3. These recurring characters must look exactly the same every time they appear:
- Lea, a 31-year-old German nurse with light skin, light freckles, shoulder-length straight chestnut-brown hair tied in a low ponytail, green-grey eyes and a slim build, wearing a long-sleeved dusty-rose knit sweater, dark-blue straight jeans and small silver hoop earrings
- Giuseppe, a 74-year-old Italian grandfather with tanned olive skin, a deeply lined friendly face, thick white hair combed back, a bushy white mustache, warm brown eyes and a stocky build, wearing a light-blue short-sleeved linen shirt, beige trousers with brown suspenders and a dark grey flat cap
- Heinrich Krüger in 1923, a 64-year-old retired Berlin teacher with light skin, a long narrow lined face, short white hair parted on the left, a full white walrus mustache, grey-blue eyes and a tall but slightly hunched build, wearing round wire-rimmed glasses, a worn and patched charcoal-grey three-piece wool suit, a white collared shirt, a faded dark green tie and a silver pocket-watch chain across his waistcoat
- Elisabeth Krüger in 1923, a 60-year-old Berlin woman with light skin, an oval lined face, silver-grey hair pinned up in a neat bun, soft hazel eyes and a thin build, wearing a faded long high-necked navy-blue dress with a mended white lace collar, a grey knitted shawl and a small oval cameo brooch at her throat
- Heinrich Krüger in 1913, a 54-year-old Berlin secondary-school teacher with light skin, a long narrow face, short dark-brown hair with grey temples parted on the left, a full dark-brown walrus mustache, grey-blue eyes and a tall upright build, wearing round wire-rimmed glasses, a charcoal-grey three-piece wool suit, a white high-collared shirt, a dark green tie and a silver pocket-watch chain across his waistcoat
- Elisabeth Krüger in 1913, a 50-year-old Berlin housewife with light skin, an oval face, dark-blond hair pinned up in a neat bun, soft hazel eyes and a slim build, wearing a long high-necked navy-blue dress with a white lace collar and a small oval cameo brooch at her throat
- their two children in 1913: Greta, a 12-year-old girl with light skin and long dark-blond braids in a white pinafore dress, and Karl, a 9-year-old boy with light skin and short light-brown hair in a navy-and-white sailor suit
- Mehmet today, an 86-year-old Turkish grandfather with olive skin, a deeply lined kind face, short white hair, a thick white mustache, white eyebrows with a small scar through the left eyebrow and dark brown eyes, wearing a brown knitted cardigan over a white shirt buttoned to the top and grey trousers
- Mehmet in 1965, a 25-year-old Turkish guest worker with olive skin, a lean face, thick black hair combed back, a thick black mustache, strong dark eyebrows with a small scar through the left eyebrow, dark brown eyes and a lean build, wearing a brown wool suit jacket over a white shirt buttoned to the top, grey trousers and a dark flat cap, carrying a worn brown leather suitcase
- Mehmet in 1978, a 38-year-old Turkish man with olive skin, a fuller face, thick black hair combed back, a thick black mustache, strong dark eyebrows with a small scar through the left eyebrow and dark brown eyes, wearing a brown wool suit jacket over a white shirt buttoned to the top, grey trousers and a dark flat cap
- Thomas, a 36-year-old German father with light skin, short sandy-blond hair, a short sandy-blond beard, blue eyes and a tall build, wearing a green-and-white checked flannel shirt with rolled-up sleeves and dark-blue work trousers
- Ben, his 6-year-old son with light skin, curly red-brown hair, freckles and blue eyes, wearing a yellow T-shirt, blue dungarees and green rubber boots
- Ben thirty years later, a 36-year-old man with light skin, curly red-brown hair, freckles, a short red-brown beard and blue eyes, wearing a yellow knit sweater and dark jeans
- Thomas thirty years later, a 66-year-old German grandfather with light skin, short grey hair, a short grey beard, blue eyes and a tall, slightly stooped build, wearing a green-and-white checked flannel shirt and dark-blue trousers
4. No captions, titles, logos or watermarks.
Please do not create an image yet – just reply "Ready". My image requests follow in the next messages.
```

#### Lea (die Mieterin von heute)

Die Identifikationsfigur von heute in Skript 2: eine 31-jährige Krankenpflegerin, die zur Miete wohnt und kaum etwas sparen kann. Erkennungszeichen: kastanienbrauner tiefer Pferdeschwanz, Sommersprossen, altrosa Strickpullover, kleine silberne Creolen.

**Kommt vor in:** Thumbnail, Bild 03, Bild 50, Bild 58, Bild 65, Bild 80, Bild 83, Bild 84

**Feste Beschreibung:**

```text
Lea, a 31-year-old German nurse with light skin, light freckles, shoulder-length straight chestnut-brown hair tied in a low ponytail, green-grey eyes and a slim build, wearing a long-sleeved dusty-rose knit sweater, dark-blue straight jeans and small silver hoop earrings
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Lea, a 31-year-old German nurse with light skin, light freckles, shoulder-length straight chestnut-brown hair tied in a low ponytail, green-grey eyes and a slim build, wearing a long-sleeved dusty-rose knit sweater, dark-blue straight jeans and small silver hoop earrings. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Giuseppe (der italienische Großvater)

Der italienische Großvater in Skript 2 – er steht für Familien, deren Haus seit Generationen in der Familie bleibt. Erkennungszeichen: dichter weißer Schnurrbart, hellblaues Leinenhemd, braune Hosenträger, dunkelgraue Schiebermütze.

**Kommt vor in:** Thumbnail, Bild 04, Bild 66

**Feste Beschreibung:**

```text
Giuseppe, a 74-year-old Italian grandfather with tanned olive skin, a deeply lined friendly face, thick white hair combed back, a bushy white mustache, warm brown eyes and a stocky build, wearing a light-blue short-sleeved linen shirt, beige trousers with brown suspenders and a dark grey flat cap
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Giuseppe, a 74-year-old Italian grandfather with tanned olive skin, a deeply lined friendly face, thick white hair combed back, a bushy white mustache, warm brown eyes and a stocky build, wearing a light-blue short-sleeved linen shirt, beige trousers with brown suspenders and a dark grey flat cap. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Heinrich Krüger – 1923/24

Derselbe Heinrich zehn Jahre später: pensioniert, Ersparnisse und Pension von der Inflation aufgefressen (Skript 5 und 2). Gleiche Brille, gleicher – jetzt abgetragener und geflickter – Anzug, aber weißes Haar und weißer Schnurrbart.

**Kommt vor in:** Bild 24

**Feste Beschreibung:**

```text
Heinrich Krüger in 1923, a 64-year-old retired Berlin teacher with light skin, a long narrow lined face, short white hair parted on the left, a full white walrus mustache, grey-blue eyes and a tall but slightly hunched build, wearing round wire-rimmed glasses, a worn and patched charcoal-grey three-piece wool suit, a white collared shirt, a faded dark green tie and a silver pocket-watch chain across his waistcoat
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Heinrich Krüger in 1923, a 64-year-old retired Berlin teacher with light skin, a long narrow lined face, short white hair parted on the left, a full white walrus mustache, grey-blue eyes and a tall but slightly hunched build, wearing round wire-rimmed glasses, a worn and patched charcoal-grey three-piece wool suit, a white collared shirt, a faded dark green tie and a silver pocket-watch chain across his waistcoat. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Elisabeth Krüger – 1923

Dieselbe Elisabeth 1923 (Skript 5 und 2): silbergraues Haar, dasselbe – jetzt verblichene – marineblaue Kleid mit geflicktem Kragen, grauer Strickschal und immer noch die Kamee-Brosche.

**Kommt vor in:** Bild 24

**Feste Beschreibung:**

```text
Elisabeth Krüger in 1923, a 60-year-old Berlin woman with light skin, an oval lined face, silver-grey hair pinned up in a neat bun, soft hazel eyes and a thin build, wearing a faded long high-necked navy-blue dress with a mended white lace collar, a grey knitted shawl and a small oval cameo brooch at her throat
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Elisabeth Krüger in 1923, a 60-year-old Berlin woman with light skin, an oval lined face, silver-grey hair pinned up in a neat bun, soft hazel eyes and a thin build, wearing a faded long high-necked navy-blue dress with a mended white lace collar, a grey knitted shawl and a small oval cameo brooch at her throat. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Heinrich Krüger – 1913

Familienvater der Berliner Familie Krüger, Gymnasiallehrer, 1913 auf dem Höhepunkt seines bürgerlichen Lebens (Skript 5, als altes Foto auch in Skript 2). Erkennungszeichen: dunkler Walross-Schnurrbart, runde Nickelbrille, anthrazitfarbener Dreiteiler, silberne Taschenuhrkette.

**Kommt vor in:** Bild 30

**Feste Beschreibung:**

```text
Heinrich Krüger in 1913, a 54-year-old Berlin secondary-school teacher with light skin, a long narrow face, short dark-brown hair with grey temples parted on the left, a full dark-brown walrus mustache, grey-blue eyes and a tall upright build, wearing round wire-rimmed glasses, a charcoal-grey three-piece wool suit, a white high-collared shirt, a dark green tie and a silver pocket-watch chain across his waistcoat
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Heinrich Krüger in 1913, a 54-year-old Berlin secondary-school teacher with light skin, a long narrow face, short dark-brown hair with grey temples parted on the left, a full dark-brown walrus mustache, grey-blue eyes and a tall upright build, wearing round wire-rimmed glasses, a charcoal-grey three-piece wool suit, a white high-collared shirt, a dark green tie and a silver pocket-watch chain across his waistcoat. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Elisabeth Krüger – 1913 bis 1915

Heinrichs Ehefrau (Skript 5, als altes Foto in Skript 2). 1915 gibt sie ihren goldenen Ehering für den Krieg ab. Erkennungszeichen: dunkelblondes Haar im Dutt, marineblaues hochgeschlossenes Kleid mit weißem Spitzenkragen, ovale Kamee-Brosche.

**Kommt vor in:** Bild 30

**Feste Beschreibung:**

```text
Elisabeth Krüger in 1913, a 50-year-old Berlin housewife with light skin, an oval face, dark-blond hair pinned up in a neat bun, soft hazel eyes and a slim build, wearing a long high-necked navy-blue dress with a white lace collar and a small oval cameo brooch at her throat
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Elisabeth Krüger in 1913, a 50-year-old Berlin housewife with light skin, an oval face, dark-blond hair pinned up in a neat bun, soft hazel eyes and a slim build, wearing a long high-necked navy-blue dress with a white lace collar and a small oval cameo brooch at her throat. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Greta und Karl Krüger – 1913

Die Kinder der Krügers im Jahr 1913: Greta (12) mit langen dunkelblonden Zöpfen und Karl (9) im Matrosenanzug. Nur auf dem Familienbild von 1913 (Skript 5, als altes Foto in Skript 2).

**Kommt vor in:** Bild 30

**Feste Beschreibung:**

```text
their two children in 1913: Greta, a 12-year-old girl with light skin and long dark-blond braids in a white pinafore dress, and Karl, a 9-year-old boy with light skin and short light-brown hair in a navy-and-white sailor suit
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of these children standing side by side on a plain light-grey studio background, shown once from the front and once from behind, full body, even soft lighting: their two children in 1913: Greta, a 12-year-old girl with light skin and long dark-blond braids in a white pinafore dress, and Karl, a 9-year-old boy with light skin and short light-brown hair in a navy-and-white sailor suit. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Mehmet – heute

Derselbe Mehmet heute als Großvater mit Kindern und Enkeln in Deutschland (Skript 2). Weißer Schnurrbart, gleiche Narbe in der linken Augenbraue.

**Kommt vor in:** Bild 68

**Feste Beschreibung:**

```text
Mehmet today, an 86-year-old Turkish grandfather with olive skin, a deeply lined kind face, short white hair, a thick white mustache, white eyebrows with a small scar through the left eyebrow and dark brown eyes, wearing a brown knitted cardigan over a white shirt buttoned to the top and grey trousers
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Mehmet today, an 86-year-old Turkish grandfather with olive skin, a deeply lined kind face, short white hair, a thick white mustache, white eyebrows with a small scar through the left eyebrow and dark brown eyes, wearing a brown knitted cardigan over a white shirt buttoned to the top and grey trousers. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Mehmet – 1965

Mehmet als junger Gastarbeiter bei der Ankunft in Deutschland 1965 (Skript 2). Erkennungszeichen über alle Altersstufen: dichter Schnurrbart, kräftige Augenbrauen mit kleiner Narbe in der linken Augenbraue, bis oben zugeknöpftes weißes Hemd.

**Kommt vor in:** Bild 69

**Feste Beschreibung:**

```text
Mehmet in 1965, a 25-year-old Turkish guest worker with olive skin, a lean face, thick black hair combed back, a thick black mustache, strong dark eyebrows with a small scar through the left eyebrow, dark brown eyes and a lean build, wearing a brown wool suit jacket over a white shirt buttoned to the top, grey trousers and a dark flat cap, carrying a worn brown leather suitcase
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Mehmet in 1965, a 25-year-old Turkish guest worker with olive skin, a lean face, thick black hair combed back, a thick black mustache, strong dark eyebrows with a small scar through the left eyebrow, dark brown eyes and a lean build, wearing a brown wool suit jacket over a white shirt buttoned to the top, grey trousers and a dark flat cap, carrying a worn brown leather suitcase. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Mehmet – 1978

Derselbe Mehmet 1978 vor dem Haus, das er sich mit seinem Ersparten in der Heimat gebaut hat (Skript 2).

**Kommt vor in:** Bild 70

**Feste Beschreibung:**

```text
Mehmet in 1978, a 38-year-old Turkish man with olive skin, a fuller face, thick black hair combed back, a thick black mustache, strong dark eyebrows with a small scar through the left eyebrow and dark brown eyes, wearing a brown wool suit jacket over a white shirt buttoned to the top, grey trousers and a dark flat cap
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Mehmet in 1978, a 38-year-old Turkish man with olive skin, a fuller face, thick black hair combed back, a thick black mustache, strong dark eyebrows with a small scar through the left eyebrow and dark brown eyes, wearing a brown wool suit jacket over a white shirt buttoned to the top, grey trousers and a dark flat cap. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Thomas – jung

Der Vater im Baum-Sprichwort (Skript 2). Erkennungszeichen: sandblonder Bart, grün-weiß kariertes Flanellhemd. Der Baum steht vor einem bescheidenen Haus mit roter Haustür.

**Kommt vor in:** Bild 77

**Feste Beschreibung:**

```text
Thomas, a 36-year-old German father with light skin, short sandy-blond hair, a short sandy-blond beard, blue eyes and a tall build, wearing a green-and-white checked flannel shirt with rolled-up sleeves and dark-blue work trousers
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Thomas, a 36-year-old German father with light skin, short sandy-blond hair, a short sandy-blond beard, blue eyes and a tall build, wearing a green-and-white checked flannel shirt with rolled-up sleeves and dark-blue work trousers. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Ben – als Kind

Thomas' Sohn Ben beim Baumpflanzen (Skript 2): rotbraune Locken, Sommersprossen, gelbes T-Shirt, blaue Latzhose, grüne Gummistiefel.

**Kommt vor in:** Bild 77

**Feste Beschreibung:**

```text
Ben, his 6-year-old son with light skin, curly red-brown hair, freckles and blue eyes, wearing a yellow T-shirt, blue dungarees and green rubber boots
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Ben, his 6-year-old son with light skin, curly red-brown hair, freckles and blue eyes, wearing a yellow T-shirt, blue dungarees and green rubber boots. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Ben – erwachsen

Ben 30 Jahre später (Skript 2): dieselben rotbraunen Locken und Sommersprossen, jetzt mit Bart und gelbem Pullover.

**Kommt vor in:** Bild 78

**Feste Beschreibung:**

```text
Ben thirty years later, a 36-year-old man with light skin, curly red-brown hair, freckles, a short red-brown beard and blue eyes, wearing a yellow knit sweater and dark jeans
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Ben thirty years later, a 36-year-old man with light skin, curly red-brown hair, freckles, a short red-brown beard and blue eyes, wearing a yellow knit sweater and dark jeans. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Thomas – 30 Jahre später

Thomas 30 Jahre später unter demselben, jetzt großen Baum (Skript 2): graues Haar, grauer Bart, wieder das grün-weiß karierte Hemd.

**Kommt vor in:** Bild 78

**Feste Beschreibung:**

```text
Thomas thirty years later, a 66-year-old German grandfather with light skin, short grey hair, a short grey beard, blue eyes and a tall, slightly stooped build, wearing a green-and-white checked flannel shirt and dark-blue trousers
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Thomas thirty years later, a 66-year-old German grandfather with light skin, short grey hair, a short grey beard, blue eyes and a tall, slightly stooped build, wearing a green-and-white checked flannel shirt and dark-blue trousers. Style: cinematic documentary style, photorealistic, dramatic natural lighting, shallow depth of field, highly detailed. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

### Skript 3 – Wie der Supermarkt dein Gehirn hackt

**Stil:**

```text
hyperrealistic photograph, cinematic lighting, vivid colors, sharp detail, shallow depth of field
```

**Setup-Nachricht für den Copilot-Chat dieses Videos:**

```text
In this chat I will ask you to create the images for one video, one by one. Please apply these rules to every image in this chat:
1. Format: always 16:9 widescreen landscape.
2. Visual style: hyperrealistic photograph, cinematic lighting, vivid colors, sharp detail, shallow depth of field.
3. These recurring characters must look exactly the same every time they appear:
- Daniel, a 38-year-old German office worker with light skin, short dark-blond hair with slightly receding temples, a neatly trimmed short ash-blond beard, blue eyes and a medium build, wearing a navy-blue quilted jacket over a light-grey hoodie, dark jeans and brown leather sneakers, carrying a small olive-green canvas tote bag
- Mia, Daniel's 5-year-old daughter with light skin, curly blond hair in two small pigtails with red hair ties and blue eyes, wearing a yellow raincoat over a red-and-white striped top, blue jeans and red sneakers
4. No captions, titles, logos or watermarks.
Please do not create an image yet – just reply "Ready". My image requests follow in the next messages.
```

#### Daniel (der Einkäufer)

Der Einkäufer aus Skript 3, der nur Milch kaufen wollte. Er führt die Zuschauer durch alle neun Tricks. Erkennungszeichen: dunkelblonde Haare mit leichten Geheimratsecken, kurzer aschblonder Bart, navyblaue Steppjacke, olivgrüner Stoffbeutel.

**Kommt vor in:** Thumbnail, Bild 01, Bild 02, Bild 06, Bild 09, Bild 12, Bild 15, Bild 16, Bild 19, Bild 21, Bild 22, Bild 27, Bild 36, Bild 38, Bild 42, Bild 46, Bild 47, Bild 49, Bild 51, Bild 59, Bild 67, Bild 68, Bild 77, Bild 79, Bild 81, Bild 82, Bild 85

**Feste Beschreibung:**

```text
Daniel, a 38-year-old German office worker with light skin, short dark-blond hair with slightly receding temples, a neatly trimmed short ash-blond beard, blue eyes and a medium build, wearing a navy-blue quilted jacket over a light-grey hoodie, dark jeans and brown leather sneakers, carrying a small olive-green canvas tote bag
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Daniel, a 38-year-old German office worker with light skin, short dark-blond hair with slightly receding temples, a neatly trimmed short ash-blond beard, blue eyes and a medium build, wearing a navy-blue quilted jacket over a light-grey hoodie, dark jeans and brown leather sneakers, carrying a small olive-green canvas tote bag. Style: hyperrealistic photograph, cinematic lighting, vivid colors, sharp detail, shallow depth of field. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Mia (Daniels Tochter)

Daniels 5-jährige Tochter (Skript 3) – die Hauptperson in der Quengelzone. Erkennungszeichen: blonde Locken mit zwei Zöpfchen und roten Haargummis, gelbe Regenjacke, rote Sneaker.

**Kommt vor in:** Bild 26, Bild 67, Bild 85

**Feste Beschreibung:**

```text
Mia, Daniel's 5-year-old daughter with light skin, curly blond hair in two small pigtails with red hair ties and blue eyes, wearing a yellow raincoat over a red-and-white striped top, blue jeans and red sneakers
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Mia, Daniel's 5-year-old daughter with light skin, curly blond hair in two small pigtails with red hair ties and blue eyes, wearing a yellow raincoat over a red-and-white striped top, blue jeans and red sneakers. Style: hyperrealistic photograph, cinematic lighting, vivid colors, sharp detail, shallow depth of field. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

### Skript 4 – Warum die Deutsche Bahn nie pünktlich ist

**Stil:**

```text
cinematic photorealistic, dramatic lighting, rich detail, documentary style
```

**Setup-Nachricht für den Copilot-Chat dieses Videos:**

```text
In this chat I will ask you to create the images for one video, one by one. Please apply these rules to every image in this chat:
1. Format: always 16:9 widescreen landscape.
2. Visual style: cinematic photorealistic, dramatic lighting, rich detail, documentary style.
3. These recurring characters must look exactly the same every time they appear:
- Markus, a 41-year-old German commuter with light skin, short dark-brown hair greying at the temples, a clean-shaven face with a strong jaw, brown eyes behind rectangular black-framed glasses and a tall, lean build, wearing a charcoal-grey wool coat over a light-blue shirt, dark trousers, black leather shoes, a burgundy-red knitted scarf and a black laptop backpack
- Werner, a 63-year-old German railway signalman with light skin, a round friendly face, thinning grey hair, a thick grey mustache and kind blue eyes, wearing a dark-blue work jacket over a red-and-black checked flannel shirt, with reading glasses hanging on a cord around his neck
- Sabine, a 45-year-old German train attendant with light skin, a short practical light-brown bob haircut, a calm friendly face and hazel eyes, wearing a plain dark-blue uniform jacket with thin red piping and no logos, a red-and-white patterned neck scarf, dark-blue trousers and a small black ticket scanner on a strap
4. No captions, titles, logos or watermarks.
Please do not create an image yet – just reply "Ready". My image requests follow in the next messages.
```

#### Markus (der Pendler)

Der Pendler aus Skript 4 – derselbe Mann reist in Skript 9 nach Japan. Er ist die Identifikationsfigur für alle, die sich über die Bahn ärgern. Erkennungszeichen: anthrazitfarbener Wollmantel, bordeauxroter Strickschal, eckige schwarze Brille, schwarzer Laptop-Rucksack.

**Kommt vor in:** Thumbnail, Bild 01, Bild 05, Bild 13, Bild 15, Bild 16, Bild 52, Bild 67, Bild 79, Bild 80, Bild 81, Bild 83

**Feste Beschreibung:**

```text
Markus, a 41-year-old German commuter with light skin, short dark-brown hair greying at the temples, a clean-shaven face with a strong jaw, brown eyes behind rectangular black-framed glasses and a tall, lean build, wearing a charcoal-grey wool coat over a light-blue shirt, dark trousers, black leather shoes, a burgundy-red knitted scarf and a black laptop backpack
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Markus, a 41-year-old German commuter with light skin, short dark-brown hair greying at the temples, a clean-shaven face with a strong jaw, brown eyes behind rectangular black-framed glasses and a tall, lean build, wearing a charcoal-grey wool coat over a light-blue shirt, dark trousers, black leather shoes, a burgundy-red knitted scarf and a black laptop backpack. Style: cinematic photorealistic, dramatic lighting, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Werner (der Fahrdienstleiter)

Der Fahrdienstleiter im alten mechanischen Stellwerk (Skript 4). Erkennungszeichen: dicker grauer Schnurrbart, rot-schwarz kariertes Flanellhemd, Lesebrille an einer Kordel um den Hals.

**Kommt vor in:** Bild 33, Bild 35, Bild 59

**Feste Beschreibung:**

```text
Werner, a 63-year-old German railway signalman with light skin, a round friendly face, thinning grey hair, a thick grey mustache and kind blue eyes, wearing a dark-blue work jacket over a red-and-black checked flannel shirt, with reading glasses hanging on a cord around his neck
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Werner, a 63-year-old German railway signalman with light skin, a round friendly face, thinning grey hair, a thick grey mustache and kind blue eyes, wearing a dark-blue work jacket over a red-and-black checked flannel shirt, with reading glasses hanging on a cord around his neck. Style: cinematic photorealistic, dramatic lighting, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Sabine (die Zugbegleiterin)

Die Zugbegleiterin in Skript 4, die den ganzen Frust der Fahrgäste abbekommt. Erkennungszeichen: hellbrauner Bob, dunkelblaue Uniformjacke mit roter Paspel (ohne Logo), rot-weißes Halstuch.

**Kommt vor in:** Bild 57, Bild 60

**Feste Beschreibung:**

```text
Sabine, a 45-year-old German train attendant with light skin, a short practical light-brown bob haircut, a calm friendly face and hazel eyes, wearing a plain dark-blue uniform jacket with thin red piping and no logos, a red-and-white patterned neck scarf, dark-blue trousers and a small black ticket scanner on a strap
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Sabine, a 45-year-old German train attendant with light skin, a short practical light-brown bob haircut, a calm friendly face and hazel eyes, wearing a plain dark-blue uniform jacket with thin red piping and no logos, a red-and-white patterned neck scarf, dark-blue trousers and a small black ticket scanner on a strap. Style: cinematic photorealistic, dramatic lighting, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

### Skript 5 – Als Geld wertlos wurde: Die Hyperinflation 1923

**Stil:**

```text
cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style
```

**Setup-Nachricht für den Copilot-Chat dieses Videos:**

```text
In this chat I will ask you to create the images for one video, one by one. Please apply these rules to every image in this chat:
1. Format: always 16:9 widescreen landscape.
2. Visual style: cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style.
3. These recurring characters must look exactly the same every time they appear:
- Heinrich Krüger in 1923, a 64-year-old retired Berlin teacher with light skin, a long narrow lined face, short white hair parted on the left, a full white walrus mustache, grey-blue eyes and a tall but slightly hunched build, wearing round wire-rimmed glasses, a worn and patched charcoal-grey three-piece wool suit, a white collared shirt, a faded dark green tie and a silver pocket-watch chain across his waistcoat
- Elisabeth Krüger in 1923, a 60-year-old Berlin woman with light skin, an oval lined face, silver-grey hair pinned up in a neat bun, soft hazel eyes and a thin build, wearing a faded long high-necked navy-blue dress with a mended white lace collar, a grey knitted shawl and a small oval cameo brooch at her throat
- Heinrich Krüger in 1913, a 54-year-old Berlin secondary-school teacher with light skin, a long narrow face, short dark-brown hair with grey temples parted on the left, a full dark-brown walrus mustache, grey-blue eyes and a tall upright build, wearing round wire-rimmed glasses, a charcoal-grey three-piece wool suit, a white high-collared shirt, a dark green tie and a silver pocket-watch chain across his waistcoat
- Elisabeth Krüger in 1913, a 50-year-old Berlin housewife with light skin, an oval face, dark-blond hair pinned up in a neat bun, soft hazel eyes and a slim build, wearing a long high-necked navy-blue dress with a white lace collar and a small oval cameo brooch at her throat
- their two children in 1913: Greta, a 12-year-old girl with light skin and long dark-blond braids in a white pinafore dress, and Karl, a 9-year-old boy with light skin and short light-brown hair in a navy-and-white sailor suit
4. No captions, titles, logos or watermarks.
Please do not create an image yet – just reply "Ready". My image requests follow in the next messages.
```

#### Heinrich Krüger – 1923/24

Derselbe Heinrich zehn Jahre später: pensioniert, Ersparnisse und Pension von der Inflation aufgefressen (Skript 5 und 2). Gleiche Brille, gleicher – jetzt abgetragener und geflickter – Anzug, aber weißes Haar und weißer Schnurrbart.

**Kommt vor in:** Thumbnail, Bild 42, Bild 43, Bild 46, Bild 68

**Feste Beschreibung:**

```text
Heinrich Krüger in 1923, a 64-year-old retired Berlin teacher with light skin, a long narrow lined face, short white hair parted on the left, a full white walrus mustache, grey-blue eyes and a tall but slightly hunched build, wearing round wire-rimmed glasses, a worn and patched charcoal-grey three-piece wool suit, a white collared shirt, a faded dark green tie and a silver pocket-watch chain across his waistcoat
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Heinrich Krüger in 1923, a 64-year-old retired Berlin teacher with light skin, a long narrow lined face, short white hair parted on the left, a full white walrus mustache, grey-blue eyes and a tall but slightly hunched build, wearing round wire-rimmed glasses, a worn and patched charcoal-grey three-piece wool suit, a white collared shirt, a faded dark green tie and a silver pocket-watch chain across his waistcoat. Style: cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Elisabeth Krüger – 1923

Dieselbe Elisabeth 1923 (Skript 5 und 2): silbergraues Haar, dasselbe – jetzt verblichene – marineblaue Kleid mit geflicktem Kragen, grauer Strickschal und immer noch die Kamee-Brosche.

**Kommt vor in:** Bild 01, Bild 05, Bild 42, Bild 44

**Feste Beschreibung:**

```text
Elisabeth Krüger in 1923, a 60-year-old Berlin woman with light skin, an oval lined face, silver-grey hair pinned up in a neat bun, soft hazel eyes and a thin build, wearing a faded long high-necked navy-blue dress with a mended white lace collar, a grey knitted shawl and a small oval cameo brooch at her throat
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Elisabeth Krüger in 1923, a 60-year-old Berlin woman with light skin, an oval lined face, silver-grey hair pinned up in a neat bun, soft hazel eyes and a thin build, wearing a faded long high-necked navy-blue dress with a mended white lace collar, a grey knitted shawl and a small oval cameo brooch at her throat. Style: cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Heinrich Krüger – 1913

Familienvater der Berliner Familie Krüger, Gymnasiallehrer, 1913 auf dem Höhepunkt seines bürgerlichen Lebens (Skript 5, als altes Foto auch in Skript 2). Erkennungszeichen: dunkler Walross-Schnurrbart, runde Nickelbrille, anthrazitfarbener Dreiteiler, silberne Taschenuhrkette.

**Kommt vor in:** Bild 11, Bild 12, Bild 16

**Feste Beschreibung:**

```text
Heinrich Krüger in 1913, a 54-year-old Berlin secondary-school teacher with light skin, a long narrow face, short dark-brown hair with grey temples parted on the left, a full dark-brown walrus mustache, grey-blue eyes and a tall upright build, wearing round wire-rimmed glasses, a charcoal-grey three-piece wool suit, a white high-collared shirt, a dark green tie and a silver pocket-watch chain across his waistcoat
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Heinrich Krüger in 1913, a 54-year-old Berlin secondary-school teacher with light skin, a long narrow face, short dark-brown hair with grey temples parted on the left, a full dark-brown walrus mustache, grey-blue eyes and a tall upright build, wearing round wire-rimmed glasses, a charcoal-grey three-piece wool suit, a white high-collared shirt, a dark green tie and a silver pocket-watch chain across his waistcoat. Style: cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Elisabeth Krüger – 1913 bis 1915

Heinrichs Ehefrau (Skript 5, als altes Foto in Skript 2). 1915 gibt sie ihren goldenen Ehering für den Krieg ab. Erkennungszeichen: dunkelblondes Haar im Dutt, marineblaues hochgeschlossenes Kleid mit weißem Spitzenkragen, ovale Kamee-Brosche.

**Kommt vor in:** Bild 11, Bild 15, Bild 16

**Feste Beschreibung:**

```text
Elisabeth Krüger in 1913, a 50-year-old Berlin housewife with light skin, an oval face, dark-blond hair pinned up in a neat bun, soft hazel eyes and a slim build, wearing a long high-necked navy-blue dress with a white lace collar and a small oval cameo brooch at her throat
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Elisabeth Krüger in 1913, a 50-year-old Berlin housewife with light skin, an oval face, dark-blond hair pinned up in a neat bun, soft hazel eyes and a slim build, wearing a long high-necked navy-blue dress with a white lace collar and a small oval cameo brooch at her throat. Style: cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Greta und Karl Krüger – 1913

Die Kinder der Krügers im Jahr 1913: Greta (12) mit langen dunkelblonden Zöpfen und Karl (9) im Matrosenanzug. Nur auf dem Familienbild von 1913 (Skript 5, als altes Foto in Skript 2).

**Kommt vor in:** Bild 11

**Feste Beschreibung:**

```text
their two children in 1913: Greta, a 12-year-old girl with light skin and long dark-blond braids in a white pinafore dress, and Karl, a 9-year-old boy with light skin and short light-brown hair in a navy-and-white sailor suit
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of these children standing side by side on a plain light-grey studio background, shown once from the front and once from behind, full body, even soft lighting: their two children in 1913: Greta, a 12-year-old girl with light skin and long dark-blond braids in a white pinafore dress, and Karl, a 9-year-old boy with light skin and short light-brown hair in a navy-and-white sailor suit. Style: cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

### Skript 6 – Die schlimmste Inflation der Geschichte: Ungarn 1946

**Stil:**

```text
cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style
```

**Setup-Nachricht für den Copilot-Chat dieses Videos:**

```text
In this chat I will ask you to create the images for one video, one by one. Please apply these rules to every image in this chat:
1. Format: always 16:9 widescreen landscape.
2. Visual style: cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style.
3. These recurring characters must look exactly the same every time they appear:
- László Kovács in 1946, a 38-year-old Hungarian factory worker with fair skin, a thin tired face with high cheekbones, short black hair combed back, a thick black mustache, dark brown eyes and a lean build, wearing a dark brown flat cap, a patched brown wool work jacket over a collarless grey shirt, dark trousers and worn boots
- László Kovács in 1938, a 30-year-old Hungarian man with fair skin, high cheekbones, short black hair combed back, a neat black mustache and dark brown eyes, wearing his Sunday brown wool suit with a white shirt and a dark tie
- Ilona Kovács in 1938, a 27-year-old Hungarian woman with fair skin, an oval face, dark-brown hair in a neat bun tied with a red-and-white patterned ribbon and grey eyes, wearing a cream blouse, a dark-green skirt and a thin gold wedding ring
- Ilona Kovács in 1946, a 35-year-old Hungarian woman with fair skin, an oval face, dark-brown hair under a faded red-and-white patterned headscarf tied at the nape, grey eyes and a slim build, wearing a long dark-green wool coat over a grey dress and a thin gold wedding ring
- Anna Kovács in 1946, an 8-year-old Hungarian girl with fair skin, a round face, two long dark-brown braids tied with red ribbons and brown eyes, wearing a too-large mustard-yellow knitted cardigan over a dark-blue dress, thick grey socks and worn brown shoes
- Anna Kovács today, an 88-year-old Hungarian woman with fair, deeply lined skin, silver hair in a short neat bob and warm brown eyes, wearing a dark-red wool coat, a cream-colored scarf and a thin gold ring, holding a wooden walking cane
4. No captions, titles, logos or watermarks.
Please do not create an image yet – just reply "Ready". My image requests follow in the next messages.
```

#### László Kovács – 1946

Fabrikarbeiter in Budapest 1946 (Skript 6) – der Mann aus dem Hook, der morgens zur Arbeit geht und abends alles dreimal so teuer vorfindet. Erkennungszeichen: dunkelbraune Schiebermütze, geflickte braune Arbeitsjacke, dichter schwarzer Schnurrbart.

**Kommt vor in:** Bild 01, Bild 02, Bild 33, Bild 36, Bild 37, Bild 41, Bild 44, Bild 48, Bild 58

**Feste Beschreibung:**

```text
László Kovács in 1946, a 38-year-old Hungarian factory worker with fair skin, a thin tired face with high cheekbones, short black hair combed back, a thick black mustache, dark brown eyes and a lean build, wearing a dark brown flat cap, a patched brown wool work jacket over a collarless grey shirt, dark trousers and worn boots
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: László Kovács in 1946, a 38-year-old Hungarian factory worker with fair skin, a thin tired face with high cheekbones, short black hair combed back, a thick black mustache, dark brown eyes and a lean build, wearing a dark brown flat cap, a patched brown wool work jacket over a collarless grey shirt, dark trousers and worn boots. Style: cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### László Kovács – 1938

László 1938 beim Sonntagsessen, vor dem Krieg (Skript 6). Gleiche Gesichtszüge wie 1946: hohe Wangenknochen, schwarzer Schnurrbart.

**Kommt vor in:** Bild 13

**Feste Beschreibung:**

```text
László Kovács in 1938, a 30-year-old Hungarian man with fair skin, high cheekbones, short black hair combed back, a neat black mustache and dark brown eyes, wearing his Sunday brown wool suit with a white shirt and a dark tie
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: László Kovács in 1938, a 30-year-old Hungarian man with fair skin, high cheekbones, short black hair combed back, a neat black mustache and dark brown eyes, wearing his Sunday brown wool suit with a white shirt and a dark tie. Style: cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Ilona Kovács – 1938

Ilona 1938 (Skript 6). Erkennungszeichen über alle Szenen: das rot-weiß gemusterte Band bzw. Kopftuch und der schmale goldene Ehering.

**Kommt vor in:** Bild 13

**Feste Beschreibung:**

```text
Ilona Kovács in 1938, a 27-year-old Hungarian woman with fair skin, an oval face, dark-brown hair in a neat bun tied with a red-and-white patterned ribbon and grey eyes, wearing a cream blouse, a dark-green skirt and a thin gold wedding ring
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Ilona Kovács in 1938, a 27-year-old Hungarian woman with fair skin, an oval face, dark-brown hair in a neat bun tied with a red-and-white patterned ribbon and grey eyes, wearing a cream blouse, a dark-green skirt and a thin gold wedding ring. Style: cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Ilona Kovács – 1946

Ilona 1946 (Skript 6): rot-weiß gemustertes Kopftuch, langer dunkelgrüner Wollmantel, schmaler goldener Ehering.

**Kommt vor in:** Bild 19, Bild 45, Bild 48, Bild 49, Bild 62

**Feste Beschreibung:**

```text
Ilona Kovács in 1946, a 35-year-old Hungarian woman with fair skin, an oval face, dark-brown hair under a faded red-and-white patterned headscarf tied at the nape, grey eyes and a slim build, wearing a long dark-green wool coat over a grey dress and a thin gold wedding ring
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Ilona Kovács in 1946, a 35-year-old Hungarian woman with fair skin, an oval face, dark-brown hair under a faded red-and-white patterned headscarf tied at the nape, grey eyes and a slim build, wearing a long dark-green wool coat over a grey dress and a thin gold wedding ring. Style: cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Anna Kovács – 1946 (8 Jahre)

Die Tochter von László und Ilona (Skript 6). Erkennungszeichen: zwei lange dunkelbraune Zöpfe mit roten Schleifen, zu große senfgelbe Strickjacke.

**Kommt vor in:** Bild 19, Bild 48, Bild 52

**Feste Beschreibung:**

```text
Anna Kovács in 1946, an 8-year-old Hungarian girl with fair skin, a round face, two long dark-brown braids tied with red ribbons and brown eyes, wearing a too-large mustard-yellow knitted cardigan over a dark-blue dress, thick grey socks and worn brown shoes
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Anna Kovács in 1946, an 8-year-old Hungarian girl with fair skin, a round face, two long dark-brown braids tied with red ribbons and brown eyes, wearing a too-large mustard-yellow knitted cardigan over a dark-blue dress, thick grey socks and worn brown shoes. Style: cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Anna Kovács – heute (88 Jahre)

Dieselbe Anna heute am Donauufer (Skript 6) – sie hat die Inflation als Kind erlebt. Silberner Bob, dunkelroter Wollmantel, der goldene Ring ihrer Mutter.

**Kommt vor in:** Bild 67

**Feste Beschreibung:**

```text
Anna Kovács today, an 88-year-old Hungarian woman with fair, deeply lined skin, silver hair in a short neat bob and warm brown eyes, wearing a dark-red wool coat, a cream-colored scarf and a thin gold ring, holding a wooden walking cane
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Anna Kovács today, an 88-year-old Hungarian woman with fair, deeply lined skin, silver hair in a short neat bob and warm brown eyes, wearing a dark-red wool coat, a cream-colored scarf and a thin gold ring, holding a wooden walking cane. Style: cinematic photorealistic, dramatic lighting, subtle film grain, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

### Skript 7 – 100 Billionen Dollar und trotzdem pleite: Simbabwe

**Stil:**

```text
cinematic documentary photograph, natural light, rich detail, shallow depth of field, photorealistic
```

**Setup-Nachricht für den Copilot-Chat dieses Videos:**

```text
In this chat I will ask you to create the images for one video, one by one. Please apply these rules to every image in this chat:
1. Format: always 16:9 widescreen landscape.
2. Visual style: cinematic documentary photograph, natural light, rich detail, shallow depth of field, photorealistic.
3. These recurring characters must look exactly the same every time they appear:
- Tendai Moyo, a 34-year-old Zimbabwean schoolteacher with dark brown skin, a friendly round face, short closely cropped black hair, a thin black mustache, warm dark eyes and a medium build, wearing a light-blue short-sleeved button-up shirt, a dark-blue tie, grey trousers, black shoes and a brown leather satchel over his shoulder
- Rutendo Ncube, a 40-year-old Zimbabwean market vendor with dark brown skin, high cheekbones, a warm smile and dark eyes, her hair wrapped in a bright orange-and-green patterned headwrap, wearing a long sky-blue dress with a white apron
4. No captions, titles, logos or watermarks.
Please do not create an image yet – just reply "Ready". My image requests follow in the next messages.
```

#### Tendai Moyo (der Lehrer aus Harare)

Lehrer aus Harare (Skript 7). Er steht für die Mittelschicht, deren Gehalt 2008 nicht mal mehr für die Busfahrt reicht. Erkennungszeichen: hellblaues Kurzarmhemd, dunkelblaue Krawatte, braune Ledertasche.

**Kommt vor in:** Thumbnail, Bild 01, Bild 03, Bild 50, Bild 51, Bild 54

**Feste Beschreibung:**

```text
Tendai Moyo, a 34-year-old Zimbabwean schoolteacher with dark brown skin, a friendly round face, short closely cropped black hair, a thin black mustache, warm dark eyes and a medium build, wearing a light-blue short-sleeved button-up shirt, a dark-blue tie, grey trousers, black shoes and a brown leather satchel over his shoulder
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Tendai Moyo, a 34-year-old Zimbabwean schoolteacher with dark brown skin, a friendly round face, short closely cropped black hair, a thin black mustache, warm dark eyes and a medium build, wearing a light-blue short-sleeved button-up shirt, a dark-blue tie, grey trousers, black shoes and a brown leather satchel over his shoulder. Style: cinematic documentary photograph, natural light, rich detail, shallow depth of field, photorealistic. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Rutendo Ncube (die Marktfrau)

Marktfrau in Harare (Skript 7) – vom Schleppen der Geldziegel 2008 bis zur Handyzahlung heute. Erkennungszeichen: orange-grün gemustertes Kopftuch, himmelblaues Kleid, weiße Schürze.

**Kommt vor in:** Bild 52, Bild 67, Bild 75

**Feste Beschreibung:**

```text
Rutendo Ncube, a 40-year-old Zimbabwean market vendor with dark brown skin, high cheekbones, a warm smile and dark eyes, her hair wrapped in a bright orange-and-green patterned headwrap, wearing a long sky-blue dress with a white apron
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Rutendo Ncube, a 40-year-old Zimbabwean market vendor with dark brown skin, high cheekbones, a warm smile and dark eyes, her hair wrapped in a bright orange-and-green patterned headwrap, wearing a long sky-blue dress with a white apron. Style: cinematic documentary photograph, natural light, rich detail, shallow depth of field, photorealistic. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

### Skript 8 – Mehr Öl als Saudi-Arabien und trotzdem pleite: Venezuela

**Stil:**

```text
cinematic documentary photograph, natural light, rich detail, shallow depth of field, photorealistic
```

**Setup-Nachricht für den Copilot-Chat dieses Videos:**

```text
In this chat I will ask you to create the images for one video, one by one. Please apply these rules to every image in this chat:
1. Format: always 16:9 widescreen landscape.
2. Visual style: cinematic documentary photograph, natural light, rich detail, shallow depth of field, photorealistic.
3. These recurring characters must look exactly the same every time they appear:
- Carlos Rodríguez, a 27-year-old Venezuelan engineer with light-brown skin, short black curly hair, a short black beard, dark brown eyes and a slim build, wearing a faded red baseball cap without any logo, a white T-shirt under an open dark-green overshirt, blue jeans and a large grey backpack
- Rosa Rodríguez, Carlos's 58-year-old mother with warm medium-brown skin, a round kind face, shoulder-length wavy black hair streaked with grey and brown eyes, wearing a yellow floral blouse, a light-grey cardigan and small gold earrings
4. No captions, titles, logos or watermarks.
Please do not create an image yet – just reply "Ready". My image requests follow in the next messages.
```

#### Carlos Rodríguez (der Auswanderer)

Junger Ingenieur aus Caracas (Skript 8), der zu Fuß nach Kolumbien auswandert. Erkennungszeichen: verblasste rote Baseballkappe ohne Logo, offenes dunkelgrünes Hemd, großer grauer Rucksack.

**Kommt vor in:** Bild 04, Bild 47, Bild 56, Bild 58, Bild 68, Bild 69, Bild 71, Bild 76

**Feste Beschreibung:**

```text
Carlos Rodríguez, a 27-year-old Venezuelan engineer with light-brown skin, short black curly hair, a short black beard, dark brown eyes and a slim build, wearing a faded red baseball cap without any logo, a white T-shirt under an open dark-green overshirt, blue jeans and a large grey backpack
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Carlos Rodríguez, a 27-year-old Venezuelan engineer with light-brown skin, short black curly hair, a short black beard, dark brown eyes and a slim build, wearing a faded red baseball cap without any logo, a white T-shirt under an open dark-green overshirt, blue jeans and a large grey backpack. Style: cinematic documentary photograph, natural light, rich detail, shallow depth of field, photorealistic. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Rosa Rodríguez (Carlos' Mutter)

Carlos' Mutter, die in Caracas bleibt (Skript 8). Erkennungszeichen: welliges schwarzes Haar mit grauen Strähnen, gelbe geblümte Bluse, hellgraue Strickjacke.

**Kommt vor in:** Bild 53, Bild 59, Bild 61, Bild 74, Bild 76

**Feste Beschreibung:**

```text
Rosa Rodríguez, Carlos's 58-year-old mother with warm medium-brown skin, a round kind face, shoulder-length wavy black hair streaked with grey and brown eyes, wearing a yellow floral blouse, a light-grey cardigan and small gold earrings
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Rosa Rodríguez, Carlos's 58-year-old mother with warm medium-brown skin, a round kind face, shoulder-length wavy black hair streaked with grey and brown eyes, wearing a yellow floral blouse, a light-grey cardigan and small gold earrings. Style: cinematic documentary photograph, natural light, rich detail, shallow depth of field, photorealistic. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

### Skript 9 – Warum Züge in Japan nie zu spät kommen

**Stil:**

```text
cinematic photorealistic, clean natural light, rich detail, documentary style
```

**Setup-Nachricht für den Copilot-Chat dieses Videos:**

```text
In this chat I will ask you to create the images for one video, one by one. Please apply these rules to every image in this chat:
1. Format: always 16:9 widescreen landscape.
2. Visual style: cinematic photorealistic, clean natural light, rich detail, documentary style.
3. These recurring characters must look exactly the same every time they appear:
- Markus, a 41-year-old German commuter with light skin, short dark-brown hair greying at the temples, a clean-shaven face with a strong jaw, brown eyes behind rectangular black-framed glasses and a tall, lean build, wearing a charcoal-grey wool coat over a light-blue shirt, dark trousers, black leather shoes, a burgundy-red knitted scarf and a black laptop backpack
- Mr. Tanaka, a 52-year-old Japanese train conductor with neat short black hair greying at the temples, a clean-shaven calm face, dark brown eyes and a slim upright build, wearing a navy-blue conductor uniform with gold buttons and no logos, a navy cap with a gold band and spotless white gloves
- Yuki, a 46-year-old Japanese cleaning-crew leader with a friendly round face, dark eyes and short black hair under a bright red cap, wearing a bright red crew jacket without logos over a white shirt, black trousers and white sneakers, with a small cleaning pouch at her waist
4. No captions, titles, logos or watermarks.
Please do not create an image yet – just reply "Ready". My image requests follow in the next messages.
```

#### Markus (der Pendler)

Der Pendler aus Skript 4 – derselbe Mann reist in Skript 9 nach Japan. Er ist die Identifikationsfigur für alle, die sich über die Bahn ärgern. Erkennungszeichen: anthrazitfarbener Wollmantel, bordeauxroter Strickschal, eckige schwarze Brille, schwarzer Laptop-Rucksack.

**Kommt vor in:** Thumbnail, Bild 01, Bild 02, Bild 03, Bild 08, Bild 15, Bild 22, Bild 27, Bild 34, Bild 39, Bild 47, Bild 48, Bild 54, Bild 71, Bild 77, Bild 83, Bild 85, Bild 86

**Feste Beschreibung:**

```text
Markus, a 41-year-old German commuter with light skin, short dark-brown hair greying at the temples, a clean-shaven face with a strong jaw, brown eyes behind rectangular black-framed glasses and a tall, lean build, wearing a charcoal-grey wool coat over a light-blue shirt, dark trousers, black leather shoes, a burgundy-red knitted scarf and a black laptop backpack
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Markus, a 41-year-old German commuter with light skin, short dark-brown hair greying at the temples, a clean-shaven face with a strong jaw, brown eyes behind rectangular black-framed glasses and a tall, lean build, wearing a charcoal-grey wool coat over a light-blue shirt, dark trousers, black leather shoes, a burgundy-red knitted scarf and a black laptop backpack. Style: cinematic photorealistic, clean natural light, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Herr Tanaka (Zugbegleiter in Japan)

Zugbegleiter in Japan (Skript 9). Er zeigt das „Zeigen und Rufen“ und verbeugt sich vor dem Zug. Erkennungszeichen: marineblaue Uniform mit Goldknöpfen (ohne Logo), Mütze mit Goldband, weiße Handschuhe.

**Kommt vor in:** Bild 07, Bild 35, Bild 36, Bild 37, Bild 39, Bild 41, Bild 50, Bild 61, Bild 83

**Feste Beschreibung:**

```text
Mr. Tanaka, a 52-year-old Japanese train conductor with neat short black hair greying at the temples, a clean-shaven calm face, dark brown eyes and a slim upright build, wearing a navy-blue conductor uniform with gold buttons and no logos, a navy cap with a gold band and spotless white gloves
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Mr. Tanaka, a 52-year-old Japanese train conductor with neat short black hair greying at the temples, a clean-shaven calm face, dark brown eyes and a slim upright build, wearing a navy-blue conductor uniform with gold buttons and no logos, a navy cap with a gold band and spotless white gloves. Style: cinematic photorealistic, clean natural light, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Yuki (Leiterin des Putzteams)

Leiterin des Putzteams am Bahnhof Tokio (Skript 9) – das Sieben-Minuten-Wunder. Erkennungszeichen: knallrote Jacke, rote Kappe, weiße Sneaker.

**Kommt vor in:** Bild 42, Bild 43, Bild 44, Bild 46, Bild 48

**Feste Beschreibung:**

```text
Yuki, a 46-year-old Japanese cleaning-crew leader with a friendly round face, dark eyes and short black hair under a bright red cap, wearing a bright red crew jacket without logos over a white shirt, black trousers and white sneakers, with a small cleaning pouch at her waist
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Yuki, a 46-year-old Japanese cleaning-crew leader with a friendly round face, dark eyes and short black hair under a bright red cap, wearing a bright red crew jacket without logos over a white shirt, black trousers and white sneakers, with a small cleaning pouch at her waist. Style: cinematic photorealistic, clean natural light, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

### Skript 10 – Das Haus der Weisheit, Teil 2: Codes, Karten und das Herz

**Stil:**

```text
cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look
```

**Setup-Nachricht für den Copilot-Chat dieses Videos:**

```text
In this chat I will ask you to create the images for one video, one by one. Please apply these rules to every image in this chat:
1. Format: always 16:9 widescreen landscape.
2. Visual style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look.
3. These recurring characters must look exactly the same every time they appear:
- Yusuf, a 22-year-old man of Turkish heritage who lives in Germany, with warm light-brown skin, short dark-brown wavy hair with a neat side part, a short well-groomed black beard, dark brown eyes, thick straight eyebrows and a slim athletic build, wearing a mustard-yellow hoodie over a plain white T-shirt, dark navy jeans, white sneakers and a slim black wristwatch on his left wrist
- the Baghdad codebreaker, a ninth-century scholar in his sixties who is always shown from behind, in silhouette or with his face hidden in deep shadow (his face is never visible), of medium build, wearing a long dark burgundy robe with black trim, a black turban and a small brass inkwell hanging from his belt
- the Damascus physician, a thirteenth-century doctor in his thirties who is always shown from behind or with his face hidden in deep shadow (his face is never visible), of medium build, wearing a pale-blue robe with a deep red sash and a white turban with a red band
- Mariam, a tenth-century astrolabe maker from Aleppo who is always seen from behind or with her face out of view (her face is never visible), wearing a long saffron-orange robe, a modest dark-brown headscarf covering her hair and shoulders and a brown leather work apron, with fine brass tools in her hands
- the Palermo mapmaker, a twelfth-century scholar in his fifties who is always shown from behind or with his face turned away (his face is never visible), tall and thin, wearing a light-grey robe with a silver-embroidered collar and a sky-blue turban, holding a long brass measuring compass
- the great traveller, a fourteenth-century scholar from Tangier who is always shown from behind or in silhouette (his face is never visible), of strong build, wearing a dusty sand-colored hooded travelling cloak, a white turban, sturdy brown leather boots and a worn leather satchel, holding a wooden walking staff
- the Tunis scholar, a fourteenth-century historian in his forties who is always shown from behind or with his face hidden in deep shadow (his face is never visible), wearing an elegant black robe with gold trim and a white turban, often writing with a reed pen
4. Characters described as never showing their face are always shown from behind, in silhouette or with the face in deep shadow.
5. No captions, titles, logos or watermarks.
Please do not create an image yet – just reply "Ready". My image requests follow in the next messages.
```

#### Yusuf (moderner Erzähl-Charakter)

Der moderne Erzähl-Charakter der Islam-Reihe (Skript 1 und 10): ein 22-jähriger Student mit türkischen Wurzeln, der in Deutschland lebt. Er taucht in allen Szenen von heute auf – Handy, Laptop, Hörsaal, Schreibtisch – und gibt den Zuschauern eine feste Bezugsperson. Erkennungszeichen: senfgelber Hoodie, kurzer schwarzer Bart, schwarze Armbanduhr am linken Handgelenk.

**Kommt vor in:** Thumbnail, Bild 01, Bild 03, Bild 05, Bild 08, Bild 17, Bild 19, Bild 24, Bild 27, Bild 44, Bild 50, Bild 53, Bild 71, Bild 81, Bild 83, Bild 85

**Feste Beschreibung:**

```text
Yusuf, a 22-year-old man of Turkish heritage who lives in Germany, with warm light-brown skin, short dark-brown wavy hair with a neat side part, a short well-groomed black beard, dark brown eyes, thick straight eyebrows and a slim athletic build, wearing a mustard-yellow hoodie over a plain white T-shirt, dark navy jeans, white sneakers and a slim black wristwatch on his left wrist
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Yusuf, a 22-year-old man of Turkish heritage who lives in Germany, with warm light-brown skin, short dark-brown wavy hair with a neat side part, a short well-groomed black beard, dark brown eyes, thick straight eyebrows and a slim athletic build, wearing a mustard-yellow hoodie over a plain white T-shirt, dark navy jeans, white sneakers and a slim black wristwatch on his left wrist. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Al-Kindi – der Codeknacker aus Bagdad

Der Gelehrte, der als Erster eine Methode zum Knacken von Geheimschriften aufschrieb (Skript 10). Nie mit Gesicht. Erkennbar an: dunkles burgunderrotes Gewand mit schwarzem Saum, schwarzer Turban, Tintenfass aus Messing am Gürtel.

**Kommt vor in:** Thumbnail, Bild 02, Bild 10, Bild 13, Bild 15

**Feste Beschreibung:**

```text
the Baghdad codebreaker, a ninth-century scholar in his sixties who is always shown from behind, in silhouette or with his face hidden in deep shadow (his face is never visible), of medium build, wearing a long dark burgundy robe with black trim, a black turban and a small brass inkwell hanging from his belt
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the Baghdad codebreaker, a ninth-century scholar in his sixties who is always shown from behind, in silhouette or with his face hidden in deep shadow (his face is never visible), of medium build, wearing a long dark burgundy robe with black trim, a black turban and a small brass inkwell hanging from his belt. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Ibn al-Nafis – der Arzt aus Damaskus

Der Arzt, der den Lungenkreislauf beschrieb (Skript 10). Nie mit Gesicht. Erkennbar an: hellblaues Gewand, tiefrote Schärpe, weißer Turban mit rotem Band.

**Kommt vor in:** Bild 29, Bild 31

**Feste Beschreibung:**

```text
the Damascus physician, a thirteenth-century doctor in his thirties who is always shown from behind or with his face hidden in deep shadow (his face is never visible), of medium build, wearing a pale-blue robe with a deep red sash and a white turban with a red band
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the Damascus physician, a thirteenth-century doctor in his thirties who is always shown from behind or with his face hidden in deep shadow (his face is never visible), of medium build, wearing a pale-blue robe with a deep red sash and a white turban with a red band. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Mariam al-Asturlabi – die Astrolabienmacherin

Astrolabienmacherin aus Aleppo, nach der ein Asteroid benannt ist (Skript 10). Immer von hinten, Gesicht nie sichtbar. Erkennbar an: safranoranges Gewand, dunkelbraunes Kopftuch, Lederschürze, feine Messingwerkzeuge.

**Kommt vor in:** Bild 38, Bild 42

**Feste Beschreibung:**

```text
Mariam, a tenth-century astrolabe maker from Aleppo who is always seen from behind or with her face out of view (her face is never visible), wearing a long saffron-orange robe, a modest dark-brown headscarf covering her hair and shoulders and a brown leather work apron, with fine brass tools in her hands
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: Mariam, a tenth-century astrolabe maker from Aleppo who is always seen from behind or with her face out of view (her face is never visible), wearing a long saffron-orange robe, a modest dark-brown headscarf covering her hair and shoulders and a brown leather work apron, with fine brass tools in her hands. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Al-Idrisi – der Kartograf aus Palermo

Der Kartograf am Hof von König Roger II. (Skript 10). Nie mit Gesicht. Erkennbar an: hellgraues Gewand mit silbern besticktem Kragen, himmelblauer Turban, langer Messingzirkel.

**Kommt vor in:** Bild 46, Bild 47

**Feste Beschreibung:**

```text
the Palermo mapmaker, a twelfth-century scholar in his fifties who is always shown from behind or with his face turned away (his face is never visible), tall and thin, wearing a light-grey robe with a silver-embroidered collar and a sky-blue turban, holding a long brass measuring compass
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the Palermo mapmaker, a twelfth-century scholar in his fifties who is always shown from behind or with his face turned away (his face is never visible), tall and thin, wearing a light-grey robe with a silver-embroidered collar and a sky-blue turban, holding a long brass measuring compass. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Ibn Battuta – der größte Reisende

Der größte Reisende des Mittelalters (Skript 10). Nur von hinten oder als Silhouette. Erkennbar an: staubiger sandfarbener Kapuzenmantel, weißer Turban, Wanderstab, abgenutzte Ledertasche.

**Kommt vor in:** Bild 55, Bild 56, Bild 57, Bild 58, Bild 61

**Feste Beschreibung:**

```text
the great traveller, a fourteenth-century scholar from Tangier who is always shown from behind or in silhouette (his face is never visible), of strong build, wearing a dusty sand-colored hooded travelling cloak, a white turban, sturdy brown leather boots and a worn leather satchel, holding a wooden walking staff
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the great traveller, a fourteenth-century scholar from Tangier who is always shown from behind or in silhouette (his face is never visible), of strong build, wearing a dusty sand-colored hooded travelling cloak, a white turban, sturdy brown leather boots and a worn leather satchel, holding a wooden walking staff. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Ibn Khaldun – der Gelehrte aus Tunis

Der Historiker, der erklärte, warum zu hohe Steuern dem Staat schaden (Skript 10). Nie mit Gesicht. Erkennbar an: elegantes schwarzes Gewand mit Goldsaum, weißer Turban, Schreibrohr.

**Kommt vor in:** Bild 64, Bild 69

**Feste Beschreibung:**

```text
the Tunis scholar, a fourteenth-century historian in his forties who is always shown from behind or with his face hidden in deep shadow (his face is never visible), wearing an elegant black robe with gold trim and a white turban, often writing with a reed pen
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the Tunis scholar, a fourteenth-century historian in his forties who is always shown from behind or with his face hidden in deep shadow (his face is never visible), wearing an elegant black robe with gold trim and a white turban, often writing with a reed pen. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

### Skript 11 – Mansa Musa: Der reichste Mensch der Geschichte

**Stil:**

```text
cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look
```

**Setup-Nachricht für den Copilot-Chat dieses Videos:**

```text
In this chat I will ask you to create the images for one video, one by one. Please apply these rules to every image in this chat:
1. Format: always 16:9 widescreen landscape.
2. Visual style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look.
3. These recurring characters must look exactly the same every time they appear:
- Mansa Musa, the king of Mali in the 1320s, a tall, broad-shouldered West African ruler with dark brown skin who is always shown from behind, in silhouette or with his face hidden in deep shadow (his face is never visible), wearing a flowing white robe richly embroidered with gold thread, a high white turban with a thin gold band, heavy gold rings on both hands and a gold-handled walking staff
- Hassan, a 30-year-old Cairo money changer in 1324 with light-brown skin, a short black beard, dark eyes and a lean build, wearing a blue-and-white striped robe, a small red felt cap and a leather money pouch at his belt, usually sitting behind a polished brass scale at his market stall
- Yusuf, a 22-year-old man of Turkish heritage who lives in Germany, with warm light-brown skin, short dark-brown wavy hair with a neat side part, a short well-groomed black beard, dark brown eyes, thick straight eyebrows and a slim athletic build, wearing a mustard-yellow hoodie over a plain white T-shirt, dark navy jeans, white sneakers and a slim black wristwatch on his left wrist
- Hassan in 1336, a 42-year-old Cairo money changer with light-brown skin, a short black beard streaked with grey, dark eyes and a lean build, wearing a blue-and-white striped robe, a small red felt cap and a leather money pouch at his belt, sitting behind a polished brass scale at his market stall
- Aïssata, a 40-year-old librarian in Timbuktu in 2012 with dark brown skin, a calm, determined face and dark eyes, wearing a long indigo-blue boubou dress with white embroidery, a matching indigo headwrap and small silver earrings
4. Characters described as never showing their face are always shown from behind, in silhouette or with the face in deep shadow.
5. No captions, titles, logos or watermarks.
Please do not create an image yet – just reply "Ready". My image requests follow in the next messages.
```

#### Mansa Musa – König von Mali

Der König von Mali, der 1324 nach Mekka pilgerte (Skript 11). Aus Respekt und weil niemand weiß, wie er aussah, nie mit Gesicht – nur von hinten, als Silhouette oder im Schatten. Erkennbar an: weißes Gewand mit Goldstickerei, hoher weißer Turban mit Goldband, schwere Goldringe, Stab mit goldenem Griff.

**Kommt vor in:** Thumbnail, Bild 05, Bild 23, Bild 25, Bild 27, Bild 33, Bild 37, Bild 38, Bild 43, Bild 51, Bild 53, Bild 77

**Feste Beschreibung:**

```text
Mansa Musa, the king of Mali in the 1320s, a tall, broad-shouldered West African ruler with dark brown skin who is always shown from behind, in silhouette or with his face hidden in deep shadow (his face is never visible), wearing a flowing white robe richly embroidered with gold thread, a high white turban with a thin gold band, heavy gold rings on both hands and a gold-handled walking staff
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: Mansa Musa, the king of Mali in the 1320s, a tall, broad-shouldered West African ruler with dark brown skin who is always shown from behind, in silhouette or with his face hidden in deep shadow (his face is never visible), wearing a flowing white robe richly embroidered with gold thread, a high white turban with a thin gold band, heavy gold rings on both hands and a gold-handled walking staff. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Hassan – Geldwechsler in Kairo, 1324

Erfundener Geldwechsler auf dem Markt von Kairo (Skript 11). Durch seine Augen erleben die Zuschauer, wie das Gold seinen Wert verliert – im Sprechtext wird er als erfunden vorgestellt. Erkennungszeichen: blau-weiß gestreiftes Gewand, rote Filzkappe, Geldbeutel aus Leder, Messingwaage.

**Kommt vor in:** Bild 04, Bild 06, Bild 44, Bild 52

**Feste Beschreibung:**

```text
Hassan, a 30-year-old Cairo money changer in 1324 with light-brown skin, a short black beard, dark eyes and a lean build, wearing a blue-and-white striped robe, a small red felt cap and a leather money pouch at his belt, usually sitting behind a polished brass scale at his market stall
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Hassan, a 30-year-old Cairo money changer in 1324 with light-brown skin, a short black beard, dark eyes and a lean build, wearing a blue-and-white striped robe, a small red felt cap and a leather money pouch at his belt, usually sitting behind a polished brass scale at his market stall. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Yusuf (moderner Erzähl-Charakter)

Der moderne Erzähl-Charakter der Islam-Reihe (Skript 1 und 10): ein 22-jähriger Student mit türkischen Wurzeln, der in Deutschland lebt. Er taucht in allen Szenen von heute auf – Handy, Laptop, Hörsaal, Schreibtisch – und gibt den Zuschauern eine feste Bezugsperson. Erkennungszeichen: senfgelber Hoodie, kurzer schwarzer Bart, schwarze Armbanduhr am linken Handgelenk.

**Kommt vor in:** Bild 08, Bild 41, Bild 61, Bild 62, Bild 74, Bild 79

**Feste Beschreibung:**

```text
Yusuf, a 22-year-old man of Turkish heritage who lives in Germany, with warm light-brown skin, short dark-brown wavy hair with a neat side part, a short well-groomed black beard, dark brown eyes, thick straight eyebrows and a slim athletic build, wearing a mustard-yellow hoodie over a plain white T-shirt, dark navy jeans, white sneakers and a slim black wristwatch on his left wrist
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Yusuf, a 22-year-old man of Turkish heritage who lives in Germany, with warm light-brown skin, short dark-brown wavy hair with a neat side part, a short well-groomed black beard, dark brown eyes, thick straight eyebrows and a slim athletic build, wearing a mustard-yellow hoodie over a plain white T-shirt, dark navy jeans, white sneakers and a slim black wristwatch on his left wrist. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Hassan – zwölf Jahre später

Derselbe Hassan zwölf Jahre später (Skript 11): graue Strähnen im Bart, sonst dieselbe Kleidung und dieselbe Messingwaage.

**Kommt vor in:** Bild 48

**Feste Beschreibung:**

```text
Hassan in 1336, a 42-year-old Cairo money changer with light-brown skin, a short black beard streaked with grey, dark eyes and a lean build, wearing a blue-and-white striped robe, a small red felt cap and a leather money pouch at his belt, sitting behind a polished brass scale at his market stall
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Hassan in 1336, a 42-year-old Cairo money changer with light-brown skin, a short black beard streaked with grey, dark eyes and a lean build, wearing a blue-and-white striped robe, a small red felt cap and a leather money pouch at his belt, sitting behind a polished brass scale at his market stall. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Aïssata – Bibliothekarin in Timbuktu

Erfundene Bibliothekarin (Skript 11), stellvertretend für die echten Bibliothekare und Familien, die 2012 die Handschriften von Timbuktu retteten – im Sprechtext wird das so gesagt. Erkennungszeichen: indigoblaues Gewand mit weißer Stickerei und passendes indigoblaues Kopftuch.

**Kommt vor in:** Bild 68, Bild 69, Bild 72

**Feste Beschreibung:**

```text
Aïssata, a 40-year-old librarian in Timbuktu in 2012 with dark brown skin, a calm, determined face and dark eyes, wearing a long indigo-blue boubou dress with white embroidery, a matching indigo headwrap and small silver earrings
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Aïssata, a 40-year-old librarian in Timbuktu in 2012 with dark brown skin, a calm, determined face and dark eyes, wearing a long indigo-blue boubou dress with white embroidery, a matching indigo headwrap and small silver earrings. Style: cinematic digital painting, dramatic lighting, rich deep colors, highly detailed, atmospheric, epic documentary look. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

### Skript 12 – Wirecard: 1,9 Milliarden, die es nie gab

**Stil:**

```text
cinematic photorealistic, moody low-key lighting, cool blue and amber tones, rich detail, thriller documentary style
```

**Setup-Nachricht für den Copilot-Chat dieses Videos:**

```text
In this chat I will ask you to create the images for one video, one by one. Please apply these rules to every image in this chat:
1. Format: always 16:9 widescreen landscape.
2. Visual style: cinematic photorealistic, moody low-key lighting, cool blue and amber tones, rich detail, thriller documentary style.
3. These recurring characters must look exactly the same every time they appear:
- the CEO, a tall man in his fifties who is always shown as a silhouette, from behind or with his face completely in shadow (his face is never visible), with a shaved head, wearing a black turtleneck sweater under a dark grey suit jacket
- the COO, a slim man in his forties who is always shown as a silhouette, from behind or with his face completely in shadow (his face is never visible), with short slicked-back dark hair, wearing a navy-blue suit with an open-collared white shirt and carrying a black leather briefcase
- Sophie, a 34-year-old German IT project manager from Munich with light skin, straight shoulder-length platinum-blond hair with a side part, blue-green eyes, thin gold-rimmed round glasses and a slim build, wearing a camel-colored wool blazer over a white turtleneck sweater, dark jeans and a small silver pendant necklace
- the London reporter, a British investigative journalist in his forties who is always shown from behind or in profile in low light (his face is never clearly visible), with short sandy-brown hair, wearing a dark green waxed jacket over a grey sweater and carrying a worn brown leather notebook
4. Characters described as never showing their face are always shown from behind, in silhouette or with the face in deep shadow.
5. No captions, titles, logos or watermarks.
Please do not create an image yet – just reply "Ready". My image requests follow in the next messages.
```

#### Der Konzernchef (nur Silhouette)

Der Wirecard-Chef (Skript 12). Weil es um eine echte Person und ein Strafverfahren geht, wird er nie mit Gesicht gezeigt – nur als Silhouette oder von hinten. Erkennbar an: schwarzer Rollkragenpullover unter dunkelgrauem Sakko, kahler Kopf.

**Kommt vor in:** Thumbnail, Bild 13, Bild 19, Bild 38, Bild 52, Bild 68

**Feste Beschreibung:**

```text
the CEO, a tall man in his fifties who is always shown as a silhouette, from behind or with his face completely in shadow (his face is never visible), with a shaved head, wearing a black turtleneck sweater under a dark grey suit jacket
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the CEO, a tall man in his fifties who is always shown as a silhouette, from behind or with his face completely in shadow (his face is never visible), with a shaved head, wearing a black turtleneck sweater under a dark grey suit jacket. Style: cinematic photorealistic, moody low-key lighting, cool blue and amber tones, rich detail, thriller documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Der verschwundene Vorstand (nur Silhouette)

Der Asien-Vorstand, der 2020 verschwand (Skript 12). Echte Person – deshalb nie mit Gesicht. Erkennbar an: marineblauer Anzug, offener weißer Hemdkragen, schwarze Aktentasche, nach hinten gekämmtes dunkles Haar.

**Kommt vor in:** Bild 06, Bild 17, Bild 45, Bild 46, Bild 60, Bild 61

**Feste Beschreibung:**

```text
the COO, a slim man in his forties who is always shown as a silhouette, from behind or with his face completely in shadow (his face is never visible), with short slicked-back dark hair, wearing a navy-blue suit with an open-collared white shirt and carrying a black leather briefcase
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the COO, a slim man in his forties who is always shown as a silhouette, from behind or with his face completely in shadow (his face is never visible), with short slicked-back dark hair, wearing a navy-blue suit with an open-collared white shirt and carrying a black leather briefcase. Style: cinematic photorealistic, moody low-key lighting, cool blue and amber tones, rich detail, thriller documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Sophie (die Kleinanlegerin)

Erfundene Kleinanlegerin aus München (Skript 12). Sie steht für die Zehntausenden, die mit Wirecard-Aktien ihr Erspartes verloren – das wird im Video auch so gesagt. Erkennungszeichen: platinblonder Bob, runde goldene Brille, kamelfarbener Blazer über weißem Rollkragenpullover.

**Kommt vor in:** Bild 08, Bild 22, Bild 23, Bild 24, Bild 25, Bild 43, Bild 58, Bild 82

**Feste Beschreibung:**

```text
Sophie, a 34-year-old German IT project manager from Munich with light skin, straight shoulder-length platinum-blond hair with a side part, blue-green eyes, thin gold-rimmed round glasses and a slim build, wearing a camel-colored wool blazer over a white turtleneck sweater, dark jeans and a small silver pendant necklace
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Sophie, a 34-year-old German IT project manager from Munich with light skin, straight shoulder-length platinum-blond hair with a side part, blue-green eyes, thin gold-rimmed round glasses and a slim build, wearing a camel-colored wool blazer over a white turtleneck sweater, dark jeans and a small silver pendant necklace. Style: cinematic photorealistic, moody low-key lighting, cool blue and amber tones, rich detail, thriller documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Der Journalist in London (ohne Gesicht)

Der Journalist der Financial Times, der jahrelang hartnäckig nachfragte (Skript 12). Echte Person – deshalb nur von hinten oder im Halbdunkel. Erkennbar an: dunkelgrüne Wachsjacke, grauer Pullover, abgegriffenes braunes Notizbuch.

**Kommt vor in:** Bild 32, Bild 33, Bild 37, Bild 41, Bild 80

**Feste Beschreibung:**

```text
the London reporter, a British investigative journalist in his forties who is always shown from behind or in profile in low light (his face is never clearly visible), with short sandy-brown hair, wearing a dark green waxed jacket over a grey sweater and carrying a worn brown leather notebook
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the London reporter, a British investigative journalist in his forties who is always shown from behind or in profile in low light (his face is never clearly visible), with short sandy-brown hair, wearing a dark green waxed jacket over a grey sweater and carrying a worn brown leather notebook. Style: cinematic photorealistic, moody low-key lighting, cool blue and amber tones, rich detail, thriller documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

### Skript 13 – Aldi: Die geheimste Familie Deutschlands

**Stil:**

```text
cinematic photorealistic, warm nostalgic film look, natural light, rich detail, documentary style
```

**Setup-Nachricht für den Copilot-Chat dieses Videos:**

```text
In this chat I will ask you to create the images for one video, one by one. Please apply these rules to every image in this chat:
1. Format: always 16:9 widescreen landscape.
2. Visual style: cinematic photorealistic, warm nostalgic film look, natural light, rich detail, documentary style.
3. These recurring characters must look exactly the same every time they appear:
- the elder brother in 1946, a tall, slim man in his mid-twenties who is always shown from behind or with his face in shadow (his face is never visible), with short dark-blond hair, wearing a grey shopkeeper's apron over a white shirt with rolled-up sleeves and dark trousers
- the younger brother in 1946, a stocky man in his early twenties who is always shown from behind or with his face in shadow (his face is never visible), with short dark-brown hair, wearing a dark-brown shopkeeper's coat over a white shirt and a thin black tie
- the younger brother in 1971, a stocky man in his late forties who is always shown from behind or with his face in deep shadow (his face is never visible), with short greying dark hair, wearing a dark charcoal suit, a white shirt, a narrow dark tie and a beige trench coat
- Daniel, a 38-year-old German office worker with light skin, short dark-blond hair with slightly receding temples, a neatly trimmed short ash-blond beard, blue eyes and a medium build, wearing a navy-blue quilted jacket over a light-grey hoodie, dark jeans and brown leather sneakers, carrying a small olive-green canvas tote bag
- Anna, a hardworking shopkeeper in her early thirties in 1913 who is always shown from behind or in profile with her face in shadow (her face is never visible), with dark hair pinned up in a bun, wearing a long dark-blue work dress and a white apron
- the elder brother in 1960, a tall, slim man of forty who is always shown from behind or with his face in shadow (his face is never visible), with short dark-blond hair greying at the temples, wearing a grey-blue three-piece suit
- the younger brother in 1960, a stocky man of thirty-eight who is always shown from behind or with his face in shadow (his face is never visible), with short dark-brown hair, wearing a dark-brown suit with a thin black tie
- Helga, a cashier in the 1960s and 1970s in her late twenties with light skin, short curled blond hair, bright blue eyes and a friendly smile, wearing a light-blue work smock with a white collar and a small blank name badge
4. Characters described as never showing their face are always shown from behind, in silhouette or with the face in deep shadow.
5. No captions, titles, logos or watermarks.
Please do not create an image yet – just reply "Ready". My image requests follow in the next messages.
```

#### Karl Albrecht – 1946

Der ältere Bruder nach dem Krieg (Skript 13). Die Brüder werden bewusst nie von vorne gezeigt – passend zu ihrer berühmten Verschwiegenheit. Erkennbar an: groß und schlank, dunkelblondes Haar, graue Ladenschürze.

**Kommt vor in:** Thumbnail, Bild 09, Bild 24, Bild 32, Bild 35

**Feste Beschreibung:**

```text
the elder brother in 1946, a tall, slim man in his mid-twenties who is always shown from behind or with his face in shadow (his face is never visible), with short dark-blond hair, wearing a grey shopkeeper's apron over a white shirt with rolled-up sleeves and dark trousers
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the elder brother in 1946, a tall, slim man in his mid-twenties who is always shown from behind or with his face in shadow (his face is never visible), with short dark-blond hair, wearing a grey shopkeeper's apron over a white shirt with rolled-up sleeves and dark trousers. Style: cinematic photorealistic, warm nostalgic film look, natural light, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Theo Albrecht – 1946

Der jüngere Bruder nach dem Krieg (Skript 13). Nie von vorne. Erkennbar an: kräftig, dunkelbraunes Haar, dunkelbrauner Ladenkittel, schmale schwarze Krawatte.

**Kommt vor in:** Thumbnail, Bild 09, Bild 24, Bild 32, Bild 35

**Feste Beschreibung:**

```text
the younger brother in 1946, a stocky man in his early twenties who is always shown from behind or with his face in shadow (his face is never visible), with short dark-brown hair, wearing a dark-brown shopkeeper's coat over a white shirt and a thin black tie
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the younger brother in 1946, a stocky man in his early twenties who is always shown from behind or with his face in shadow (his face is never visible), with short dark-brown hair, wearing a dark-brown shopkeeper's coat over a white shirt and a thin black tie. Style: cinematic photorealistic, warm nostalgic film look, natural light, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Theo Albrecht – 1971

Theo in der Nacht der Entführung (Skript 13). Nie von vorne. Erkennbar an: beiger Trenchcoat über anthrazitfarbenem Anzug, ergrautes dunkles Haar.

**Kommt vor in:** Bild 02, Bild 66

**Feste Beschreibung:**

```text
the younger brother in 1971, a stocky man in his late forties who is always shown from behind or with his face in deep shadow (his face is never visible), with short greying dark hair, wearing a dark charcoal suit, a white shirt, a narrow dark tie and a beige trench coat
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the younger brother in 1971, a stocky man in his late forties who is always shown from behind or with his face in deep shadow (his face is never visible), with short greying dark hair, wearing a dark charcoal suit, a white shirt, a narrow dark tie and a beige trench coat. Style: cinematic photorealistic, warm nostalgic film look, natural light, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Daniel (der Einkäufer)

Der Einkäufer aus Skript 3, der nur Milch kaufen wollte. Er führt die Zuschauer durch alle neun Tricks. Erkennungszeichen: dunkelblonde Haare mit leichten Geheimratsecken, kurzer aschblonder Bart, navyblaue Steppjacke, olivgrüner Stoffbeutel.

**Kommt vor in:** Bild 07, Bild 48, Bild 58, Bild 89, Bild 90

**Feste Beschreibung:**

```text
Daniel, a 38-year-old German office worker with light skin, short dark-blond hair with slightly receding temples, a neatly trimmed short ash-blond beard, blue eyes and a medium build, wearing a navy-blue quilted jacket over a light-grey hoodie, dark jeans and brown leather sneakers, carrying a small olive-green canvas tote bag
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Daniel, a 38-year-old German office worker with light skin, short dark-blond hair with slightly receding temples, a neatly trimmed short ash-blond beard, blue eyes and a medium build, wearing a navy-blue quilted jacket over a light-grey hoodie, dark jeans and brown leather sneakers, carrying a small olive-green canvas tote bag. Style: cinematic photorealistic, warm nostalgic film look, natural light, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Anna Albrecht – die Mutter, 1913

Die Mutter der Aldi-Gründer, die 1913 den ersten kleinen Laden eröffnete (Skript 13). Echte Person, von der kaum Bilder existieren – deshalb nie mit Gesicht. Erkennbar an: dunkles Haar im Dutt, langes dunkelblaues Arbeitskleid, weiße Schürze.

**Kommt vor in:** Bild 13, Bild 14, Bild 18

**Feste Beschreibung:**

```text
Anna, a hardworking shopkeeper in her early thirties in 1913 who is always shown from behind or in profile with her face in shadow (her face is never visible), with dark hair pinned up in a bun, wearing a long dark-blue work dress and a white apron
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: Anna, a hardworking shopkeeper in her early thirties in 1913 who is always shown from behind or in profile with her face in shadow (her face is never visible), with dark hair pinned up in a bun, wearing a long dark-blue work dress and a white apron. Style: cinematic photorealistic, warm nostalgic film look, natural light, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Karl Albrecht – 1960

Karl zur Zeit der Trennung in Nord und Süd (Skript 13). Nie von vorne. Erkennbar an: groß und schlank, graublauer Dreiteiler, Haar an den Schläfen ergraut.

**Kommt vor in:** Bild 36, Bild 38, Bild 39, Bild 41

**Feste Beschreibung:**

```text
the elder brother in 1960, a tall, slim man of forty who is always shown from behind or with his face in shadow (his face is never visible), with short dark-blond hair greying at the temples, wearing a grey-blue three-piece suit
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the elder brother in 1960, a tall, slim man of forty who is always shown from behind or with his face in shadow (his face is never visible), with short dark-blond hair greying at the temples, wearing a grey-blue three-piece suit. Style: cinematic photorealistic, warm nostalgic film look, natural light, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Theo Albrecht – 1960

Theo zur Zeit der Trennung (Skript 13). Nie von vorne. Erkennbar an: kräftig, dunkelbrauner Anzug, schmale schwarze Krawatte.

**Kommt vor in:** Bild 36, Bild 38, Bild 39, Bild 41

**Feste Beschreibung:**

```text
the younger brother in 1960, a stocky man of thirty-eight who is always shown from behind or with his face in shadow (his face is never visible), with short dark-brown hair, wearing a dark-brown suit with a thin black tie
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single historical figure, shown three times side by side on a plain light-grey studio background: a full-body back view, a full-body side view as a silhouette with the face completely hidden in shadow, and a close-up of the hands and clothing details. The figure: the younger brother in 1960, a stocky man of thirty-eight who is always shown from behind or with his face in shadow (his face is never visible), with short dark-brown hair, wearing a dark-brown suit with a thin black tie. Style: cinematic photorealistic, warm nostalgic film look, natural light, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```

#### Helga (die Kassiererin)

Erfundene Kassiererin (Skript 13) – sie steht für die Tausenden Kassiererinnen, die alle Preise auswendig kannten. Im Sprechtext wird sie so vorgestellt. Erkennungszeichen: kurze blonde Locken, hellblauer Kittel mit weißem Kragen, leeres Namensschild.

**Kommt vor in:** Bild 45, Bild 46, Bild 47, Bild 54

**Feste Beschreibung:**

```text
Helga, a cashier in the 1960s and 1970s in her late twenties with light skin, short curled blond hair, bright blue eyes and a friendly smile, wearing a light-blue work smock with a white collar and a small blank name badge
```

**Referenzblatt-Prompt:**

```text
Create an image in 16:9 widescreen landscape format. A character reference sheet of one single person, shown four times side by side on a plain light-grey studio background: front view, three-quarter view, side profile and back view, full body, neutral standing pose, even soft lighting. The person: Helga, a cashier in the 1960s and 1970s in her late twenties with light skin, short curled blond hair, bright blue eyes and a friendly smile, wearing a light-blue work smock with a white collar and a small blank name badge. Style: cinematic photorealistic, warm nostalgic film look, natural light, rich detail, documentary style. Keep exactly the same face, hair, clothing and colors in all views. No captions, titles, logos or watermarks.
```
