# QA report · 300-pages-a2-tr-sample.pdf

Built 2026-11-11 21:18 · level A2 · language tr · flags: sample

## Summary

| Check | Result | |
| --- | --- | --- |
| Validation | 0 errors, 0 warnings | pass |
| Layout geometry | 0 problems on 11 learning pages and 7 front-matter and appendix pages | pass |
| Links | 199 internal link areas to 47 targets, 73 external to 8 URLs, 0 broken | pass |
| Fonts | 16 faces, all embedded | pass |
| Text extraction | 0 broken characters, 0 letter-spaced runs | pass |
| Tagged PDF | 105/105 figures with alt text, language de-DE | pass |
| Cover | 10 text elements, 0 duplicated or missing | pass |
| Contrast | 101 colour pairs, 0 below WCAG AA | pass |
| Baseline grid | 96% of body lines on the half-baseline grid, 100% on the quarter grid | pass |

File: 20 pages, 2066 KB · layout 1.0 s (3 rounds) · render 4.6 s · write 3.7 s

## 1 · Validation log

```
Validation: 0 error(s), 0 warning(s)
  parts: 5, Z2 · tasks: 60 · vocabulary: 118 · audio tracks: 9
```

## 2 · Overflow, clipping, collisions, empty space, footers

No block overflows its page, no two blocks overlap, every block has the height the paginator planned, nothing comes closer than 1 mm to the footer strip, and no line of text is printed over another on any page.

`natural` = how full the page is before spare room is used; `final` = after write-in areas and picture slots have grown and the gaps were opened. Pages marked `open` end with more than 20 % free space.

| Page | Section | natural | final | clearance | state |
| --- | --- | --- | --- | --- | --- |
| 101 | Auftakt | – | – | 5.5 mm to footer | ok |
| 102 | wortschatz | 92% | 92% | 22.7 mm to footer | ok |
| 103 | wortschatz | 79% | 89% | 32.0 mm to footer | ok |
| 104 | hauptteil | 87% | 100% | 4.2 mm to footer | ok |
| 105 | hauptteil | 85% | 100% | 4.2 mm to footer | ok |
| 106 | hauptteil | 84% | 100% | 4.2 mm to footer | ok |
| 107 | hauptteil | 99% | 100% | 4.2 mm to footer | ok |
| 120 | uebersicht | 89% | 89% | 30.6 mm to footer | ok |
| 121 | uebersicht | 96% | 96% | 14.8 mm to footer | ok |
| 122 | abschlusstest | 92% | 100% | 4.2 mm to footer | ok |
| 123 | abschlusstest | 96% | 100% | 4.2 mm to footer | ok |

Front matter and appendix pages are composed as whole pages; they are measured in the finished PDF (lowest text line against the folio line, at least 2 mm required).

| Page | Part | clearance | state |
| --- | --- | --- | --- |
| ii | front | 11.8 mm to folio | ok |
| iii | front | 15.7 mm to folio | ok |
| iv | front | 17.5 mm to folio | ok |
| v | front | 29.8 mm to folio | ok |
| vi | front | 57.1 mm to folio | ok |
| L 1 | answers | 14.5 mm to folio | ok |
| W 1 | wordlist | 15.3 mm to folio | ok |

## 3 · Baseline alignment on facing pages

Every block starts on a multiple of half a baseline (7.5 pt), so running text on facing pages shares the same lines. Measured in the finished PDF over 312 body-size lines (tolerance 0.35 pt): **96%** sit on the half-baseline grid, **100%** on the quarter grid. The rest is text on ruled write-in lines and in phrase lists, which follow their own ruling. `shared` = grid lines that carry text on both pages of a spread.

| Spread | body lines | on half grid | on quarter grid | shared lines |
| --- | --- | --- | --- | --- |
| 101 | 13 | 100% | 100% | – |
| 102–103 | 51 | 100% | 100% | 0 |
| 104–105 | 41 | 100% | 100% | 0 |
| 106–107 | 80 | 100% | 100% | 6 |
| 120–121 | 58 | 79% | 100% | 2 |
| 122–123 | 69 | 100% | 100% | 6 |

## 4 · Links and navigation

- internal link areas: **199** pointing to 47 different targets, all resolved: **yes** (one link can consist of several clickable areas)
- named destinations in the file: 216
- external link areas: 73 → https://www.deutschfokus.example (69), https://www.youtube.com (3), mailto:hallo@deutschfokus.example (1)
- 8 different URLs, all well-formed: `https://www.deutschfokus.example/300`, `https://www.deutschfokus.example/audio`, `https://www.deutschfokus.example/audio/a2/5.01`, `https://www.deutschfokus.example/audio/a2/5.02`, `https://www.deutschfokus.example/audio/a2/5.03`, `https://www.deutschfokus.example/audio/a2/5.08`, `https://www.youtube.com/@DeutschFokus`, `mailto:hallo@deutschfokus.example`
- bookmarks: level 1: 9, level 2: 7, level 3: 21 (Kapitel → Teil → Aufgabe)
- page labels: Cover, ii, iii, iv, v, vi, 101, 102 … 121, 122, 123, L 1, W 1, Info
- metadata: title “300 Sayfada A2 Almanca – Türkçe açıklamalı (Ücretsiz örnek)”, author “Deutsch Fokus”, language de-DE
- tagged PDF: yes · figures with alternative text: 105 of 105

## 5 · Fonts

| Font | Type | Embedded |
| --- | --- | --- |
| BJLCUM+DF-Hand-Medium | Type0 | yes |
| BRSPYU+DF-Serif | Type0 | yes |
| CSPVMU+DF-Fraunces | Type0 | yes |
| DVHMTC+DF-Fraunces-Heavy | Type0 | yes |
| FOKVBL+DF-Sans-Bold-Italic | Type0 | yes |
| IIPPKY+DF-Sans-Ultra-Bold | Type0 | yes |
| LVCMSK+DF-Sans-Bold | Type0 | yes |
| NGBVPN+DF-Fraunces-Medium-Italic | Type0 | yes |
| NRGEVD+DF-Fraunces-Medium | Type0 | yes |
| OSRKMZ+DF-Hand-Bold | Type0 | yes |
| RQFTGW+DF-Fraunces-Bold | Type0 | yes |
| TAJBHQ+DF-Fraunces-Ultra-Bold | Type0 | yes |
| UBWAFX+DF-Fraunces-Semi-Bold | Type0 | yes |
| VAYXSQ+DF-Sans | Type0 | yes |
| YRHWMB+DF-Sans-Semi-Bold | Type0 | yes |
| ZGCQZL+DF-Sans-Italic | Type0 | yes |

Embedded font data: 78 KB (subsets).

## 6 · Text extraction

Whole file: 30,244 characters · 0 replacement characters · 0 letter-spaced runs · 375 umlauts/ß · 603 Turkish letters (ç ğ ı İ ş) · 0 soft hyphens · 0 zero-width characters.

### Page Cover

```text
ÜCRETSİZ ÖRNEK
NIVEAU
A2
300
Sayfada
A2 Almanca
Türkçe açıklamalı
CEVAP ANAHTARI
KELİME LİSTELERİ
ÜNİTE TESTLERİ
Deutsch Fokus
```

### Page ii

```text
Deutsch Fokus
300 Sayfada A2 Almanca
Türkçe açıklamalı
© 2026 Deutsch Fokus. Tüm hakları saklıdır.
Sürüm 1.0-demo · derleme tarihi 2026-11-11
Kişisel kullanım lisansı
Bu kitabı kendin için satın aldın. Dosyayı kendi cihazlarına kaydedebilir ve kendi çalışman için
yazdırabilirsin. Lütfen dosyayı paylaşma, yeniden satma, internete yükleme ve yapay zekâ
sistemlerini eğitmek için kullanma. Öğretmenler: lütfen her öğrenci için bir kopya – sınıf
lisansı için bize yazabilirsiniz.
Ses kayıtları
Dinleme alıştırmasının yanındaki QR kodu tara ya da parça numarasına dokun. Tüm kayıtlar: 
www.deutschfokus.example/audio
Yazı tipleri
Fraunces, Source Sans 3, Source Serif 4 ve Caveat yazı tipleriyle dizilmiştir; tümü SIL Open
Font License 1.1 ile yayımlanmıştır.
Fraunces © The Fraunces Project Authors · Source Sans 3 and Source Serif 4 © Adobe · Caveat
© The Caveat Project Authors
Bu kitaptaki tüm kişiler ve olaylar kurgusaldır.
Soru, düzeltme, öneri? hallo@deutschfokus.example
ii
```

### Page iii

```text
Inhalt
Her biri 24 sayfalık on iki ünite ve dörder sayfalık üç ara durak: tam 300 sayfa A2
Almanca.
BAŞLAMADAN ÖNCE
So funktioniert dieses Buch Bu kitap nasıl çalışır?
iv
Die Personen Kitaptaki kişiler
vi
300 SEITEN · 12 KAPITEL
Ankommen Varış – tanışma ve bugüne kadarki hikâyen
Perfekt (Wiederholung) · Präteritum: war, hatte
1
Familie und Freunde Aile ve arkadaşlar – hayatındaki insanlar
Possessivartikel im Dativ · Nebensatz mit weil
25
Essen und Einkaufen Yemek ve alışveriş – pazarda, kasada
Komparativ und Superlativ · welch-?
49
Arbeit und Beruf İş ve meslek – işler, iş arkadaşları, günlük düzen
Nebensatz mit dass · Modalverben im Präteritum
73
Zwischenstation 1 1–4. ünitelerin tekrarı ve mini sınav
97
5
Wohnen Evim evim, güzel evim – daireler, komşular, apartman kuralları
Wechselpräpositionen · wenn-Sätze · Passiv
Präsens
101
Gesundheit Sağlık – doktorda ve eczanede
Ratschläge mit sollte · Reflexive Verben
125
Unterwegs Yolda – biletler, yol tarifi, gecikmeler
Lokale Präpositionen · Verben mit Dativ
149
Feste und Freizeit Kutlamalar ve boş zaman – davetler ve planlar
Adjektive nach ein / kein · Datum und
Ordinalzahlen
173
Z2
Zwischenstation 2 5–8. ünitelerin tekrarı ve mini sınav
197
Lernen und Schule Öğrenme – kurslar, okul, anılar
Nebensätze mit als und wenn · Relativsätze im
Nominativ
201
Ämter und Dienste Resmî daireler ve hizmetler – formlar, banka,
postane
Konjunktiv II: könnte, würde, hätte · Indirekte
Fragen
225
Medien und Konsum Medya ve tüketim – internet, yorumlar,
şikâyetler
Adjektive nach der / die / das · Verben mit
Präpositionen
249
Pläne und Träume Planlar ve hayaller – sırada ne var
Futur mit werden · um … zu
273
Zwischenstation 3 9–12. ünitelerin tekrarı ve deneme sınavı
297
EKLER
Lösungen
Cevap anahtarı
L 1
Transkripte Dinleme metinleri
T 1
Wortliste A–Z
Kelime listesi A–Z
W 1
1
2
3
4
Z1
6
7
8
9
10
11
12
Z3
iii
```

### Page iv

```text
So funktioniert dieses Buch
Her ünite aynı yolu izler; böylece her zaman nerede olduğunu bilirsin. Bu iki
sayfaya ayıracağın iki dakika, sonradan sana saatler kazandırır.
24 Seiten – immer derselbe Weg
1
Auftakt
Bir resim, hedefin ve
bir kontrol listesi.
Şimdiden
yapabildiklerini
işaretle.
2
Wortschatz
Konunun kelimeleri:
resimler ve ilk
alıştırmalarla.
6
Hauptteil
Diyaloglar, metinler
ve ses kayıtları. Yeni
dil bilgisi gerçek
durumların içinde
karşına çıkar.
10
Vertiefung
Dinleme, okuma,
yazma ve konuşma
alıştırmaları.
2
Übersicht
Dil bilgisi ve kalıp
ifadeler iki sayfada.
Ekran görüntüsünü
al.
2
Abschlusstest
Sınav tarzında,
puanlı bir test.
1
Rückblick
Listeyi yeniden
işaretle ve ne kadar
ilerlediğini gör.
Jede Aufgabe hat eine Adresse
5.2 d şu demek: 5. ünite, 2. bölüm, d alıştırması. Aynı adresi cevap anahtarında, göndermelerde ve kelime listesinde de bulursun.
1
Alıştırmanın adresi
2
Hangi beceriyi çalıştığın
3
Yönerge önce Almanca,
sonra Türkçe
4
Puanın
5
Cevaba gitmek ve geri
dönmek için dokun
Sechs Symbole
Simgeler, alıştırmanın hangi beceriyi geliştirdiğini gösterir.
Hören
Lesen
Schreiben
Sprechen
Partnerarbeit
Grammatik
Artikel haben Farben
Her isim, artikeliyle birlikte sabit bir renkte görünür: der mavi, die kırmızı, das yeşil, çoğul lacivert. Rengi kelimeyle birlikte öğren.
der Flur, -e
die Küche, -n
das Bad, ¨-er
die Nebenkosten (Pl.)
Hilfe am Rand
Dört tür yardım, ait olduğu alıştırmanın hemen yanında durur.
TIPP
bir öğrenme ipucu
WORT-HILFE
tam şimdi lazım olan kelimeler
LANDESKUNDE
Almanya’da yaşam
SO GEHT’S
adım adım nasıl yapılır
5.2
d
Lies die Anzeige und ergänze die Tabelle.
/ 6
L 3
Yönerge önce Almanca, sonra Türkçe
1
2
3
4
5
iv
```

### Page v

```text
Hören mit QR-Code
Kodu telefonunla tara ya da tablette parça numarasına
dokun. Her kaydın metni kitabın sonundadır.
TRACK
5.01
0:48 Min.
Typische Fehler
Pek çok öğrencinin yaptığı bir hata, doğru cümle ve nedenini
açıklayan tek satır.
TYPISCHER FEHLER
Handschrift heißt Beispiel
Mavi el yazısı, olası bir cevabı gösterir. Boş satırlar senin.
Kann ich das?
Aynı kontrol listesi her üniteyi açar ve kapatır. İşaretlerini
karşılaştır.
Das kann ich …
NOCH
NICHT
FAST
SICHER
Ich kann meine Wohnung
beschreiben.
Wörter auf dieser Seite
Her sayfanın altında: yeni kelimeler; artikeli, çoğulu ve
Türkçesiyle.
Zeilen und Seiten
Okuma metinlerinde satır numaraları vardır. Z. 5 bir satırı, S.
120 bir sayfayı gösterir – PDF’te ikisine de dokunabilirsin.
Z. 5 = Zeile 5 · S. 120 = Seite 120
Ich wohne in die Nordstadt.
Ich wohne in der Nordstadt.
Meine Wohnung hat zwei Zimmer.
WÖRTER AUF DIESER SEITE Bu sayfadaki kelimeler
der Flur, -e koridor
das Wohnzimmer, - oturma odası
das Schlafzimmer, - yatak odası
Liebe Nachbarn,
am Samstag feiere ich Geburtstag.
Es kann etwas lauter werden.
Wenn es Sie stört, klingeln Sie
einfach – oder kommen Sie vorbei!
1
5
İşe yarayan üç alışkanlık
1
Az ama sık: Günde yirmi dakika, pazar günü iki saatten daha etkilidir.
2
Yüksek sesle söyle. Her diyaloğu iki kez oku – her seferinde başka bir konuşmacı olarak.
3
Cevap anahtarına ancak denedikten sonra bak. Hatalar planın bir parçası.
v
```

## 7 · Contrast (WCAG 2.x)

| Pair | Foreground | Background | Ratio | Needs | |
| --- | --- | --- | --- | --- | --- |
| article der on paper | `#005DCA` | `#FFFFFF` | 6.14 | 4.5 | pass |
| article der on its tint | `#005DCA` | `#E7F1FF` | 5.39 | 4.5 | pass |
| article die on paper | `#BF1070` | `#FFFFFF` | 5.96 | 4.5 | pass |
| article die on its tint | `#BF1070` | `#FFEAF1` | 5.19 | 4.5 | pass |
| article das on paper | `#007835` | `#FFFFFF` | 5.62 | 4.5 | pass |
| article das on its tint | `#007835` | `#E3F6E6` | 4.97 | 4.5 | pass |
| article pl on paper | `#1C2967` | `#FFFFFF` | 13.44 | 4.5 | pass |
| article pl on its tint | `#1C2967` | `#EAF0FF` | 11.78 | 4.5 | pass |
| note tipp label on paper | `#7B5100` | `#FFFFFF` | 6.96 | 4.5 | pass |
| note wort label on paper | `#693996` | `#FFFFFF` | 8.00 | 4.5 | pass |
| note landeskunde label on paper | `#006169` | `#FFFFFF` | 7.21 | 4.5 | pass |
| note sogehts label on paper | `#404E63` | `#FFFFFF` | 8.44 | 4.5 | pass |
| body ink on paper | `#1B1E2F` | `#FFFFFF` | 16.49 | 4.5 | pass |
| muted text on paper | `#5A5F73` | `#FFFFFF` | 6.33 | 4.5 | pass |
| handwriting ink on paper | `#2A3F9D` | `#FFFFFF` | 9.15 | 4.5 | pass |
| chapter 1: ink on mid (tab, chips) | `#1B1E2F` | `#EAAA00` | 8.05 | 4.5 | pass |
| chapter 1: ink on wash (boxes) | `#1B1E2F` | `#FEF5E6` | 15.25 | 4.5 | pass |
| chapter 1: muted on wash | `#5A5F73` | `#FEF5E6` | 5.85 | 4.5 | pass |
| chapter 1: ink on highlight | `#1B1E2F` | `#FAD18A` | 11.43 | 4.5 | pass |
| chapter 1: deep on paper (labels) | `#5E4200` | `#FFFFFF` | 9.31 | 4.5 | pass |
| chapter 1: deep on soft (pointer) | `#5E4200` | `#FBE7C5` | 7.69 | 4.5 | pass |
| chapter 2: ink on mid (tab, chips) | `#1B1E2F` | `#F0A600` | 7.98 | 4.5 | pass |
| chapter 2: ink on wash (boxes) | `#1B1E2F` | `#FEF4E6` | 15.15 | 4.5 | pass |
| chapter 2: muted on wash | `#5A5F73` | `#FEF4E6` | 5.81 | 4.5 | pass |
| chapter 2: ink on highlight | `#1B1E2F` | `#FDCF8B` | 11.37 | 4.5 | pass |
| chapter 2: deep on paper (labels) | `#614000` | `#FFFFFF` | 9.37 | 4.5 | pass |
| chapter 2: deep on soft (pointer) | `#614000` | `#FDE6C5` | 7.72 | 4.5 | pass |
| chapter 3: ink on mid (tab, chips) | `#1B1E2F` | `#F4A100` | 7.81 | 4.5 | pass |
| chapter 3: ink on wash (boxes) | `#1B1E2F` | `#FFF4E7` | 15.19 | 4.5 | pass |
| chapter 3: muted on wash | `#5A5F73` | `#FFF4E7` | 5.83 | 4.5 | pass |
| chapter 3: ink on highlight | `#1B1E2F` | `#FFCE90` | 11.37 | 4.5 | pass |
| chapter 3: deep on paper (labels) | `#633F00` | `#FFFFFF` | 9.37 | 4.5 | pass |
| chapter 3: deep on soft (pointer) | `#633F00` | `#FFE5C6` | 7.71 | 4.5 | pass |
| chapter 4: ink on mid (tab, chips) | `#1B1E2F` | `#F99D00` | 7.74 | 4.5 | pass |
| chapter 4: ink on wash (boxes) | `#1B1E2F` | `#FFF4E8` | 15.20 | 4.5 | pass |
| chapter 4: muted on wash | `#5A5F73` | `#FFF4E8` | 5.83 | 4.5 | pass |
| chapter 4: ink on highlight | `#1B1E2F` | `#FFCD97` | 11.33 | 4.5 | pass |
| chapter 4: deep on paper (labels) | `#663D00` | `#FFFFFF` | 9.41 | 4.5 | pass |
| chapter 4: deep on soft (pointer) | `#663D00` | `#FFE5C9` | 7.75 | 4.5 | pass |
| chapter 5: ink on mid (tab, chips) | `#1B1E2F` | `#FD9913` | 7.65 | 4.5 | pass |
| chapter 5: ink on wash (boxes) | `#1B1E2F` | `#FFF4E9` | 15.21 | 4.5 | pass |
| chapter 5: muted on wash | `#5A5F73` | `#FFF4E9` | 5.84 | 4.5 | pass |
| chapter 5: ink on highlight | `#1B1E2F` | `#FFCC9E` | 11.30 | 4.5 | pass |
| chapter 5: deep on paper (labels) | `#693B00` | `#FFFFFF` | 9.43 | 4.5 | pass |
| chapter 5: deep on soft (pointer) | `#693B00` | `#FFE4CC` | 7.74 | 4.5 | pass |
| chapter 6: ink on mid (tab, chips) | `#1B1E2F` | `#FF9524` | 7.52 | 4.5 | pass |
| chapter 6: ink on wash (boxes) | `#1B1E2F` | `#FFF3EA` | 15.13 | 4.5 | pass |
| chapter 6: muted on wash | `#5A5F73` | `#FFF3EA` | 5.80 | 4.5 | pass |
| chapter 6: ink on highlight | `#1B1E2F` | `#FFCCA3` | 11.32 | 4.5 | pass |
| chapter 6: deep on paper (labels) | `#6B3900` | `#FFFFFF` | 9.50 | 4.5 | pass |
| chapter 6: deep on soft (pointer) | `#6B3900` | `#FFE4CF` | 7.80 | 4.5 | pass |
| chapter 7: ink on mid (tab, chips) | `#1B1E2F` | `#FF9236` | 7.40 | 4.5 | pass |
| chapter 7: ink on wash (boxes) | `#1B1E2F` | `#FFF3EC` | 15.14 | 4.5 | pass |
| chapter 7: muted on wash | `#5A5F73` | `#FFF3EC` | 5.81 | 4.5 | pass |
| chapter 7: ink on highlight | `#1B1E2F` | `#FFCBA8` | 11.28 | 4.5 | pass |
| chapter 7: deep on paper (labels) | `#6E3700` | `#FFFFFF` | 9.50 | 4.5 | pass |
| chapter 7: deep on soft (pointer) | `#6E3700` | `#FFE4D1` | 7.82 | 4.5 | pass |
| chapter 8: ink on mid (tab, chips) | `#1B1E2F` | `#FF8F43` | 7.27 | 4.5 | pass |
| chapter 8: ink on wash (boxes) | `#1B1E2F` | `#FFF3EC` | 15.14 | 4.5 | pass |
| chapter 8: muted on wash | `#5A5F73` | `#FFF3EC` | 5.81 | 4.5 | pass |
| chapter 8: ink on highlight | `#1B1E2F` | `#FFCBAC` | 11.30 | 4.5 | pass |
| chapter 8: deep on paper (labels) | `#703505` | `#FFFFFF` | 9.54 | 4.5 | pass |
| chapter 8: deep on soft (pointer) | `#703505` | `#FFE3D3` | 7.81 | 4.5 | pass |
| chapter 9: ink on mid (tab, chips) | `#1B1E2F` | `#FF8C4C` | 7.15 | 4.5 | pass |
| chapter 9: ink on wash (boxes) | `#1B1E2F` | `#FFF3ED` | 15.15 | 4.5 | pass |
| chapter 9: muted on wash | `#5A5F73` | `#FFF3ED` | 5.81 | 4.5 | pass |
| chapter 9: ink on highlight | `#1B1E2F` | `#FFCAB0` | 11.25 | 4.5 | pass |
| chapter 9: deep on paper (labels) | `#71330D` | `#FFFFFF` | 9.63 | 4.5 | pass |
| chapter 9: deep on soft (pointer) | `#71330D` | `#FFE3D5` | 7.88 | 4.5 | pass |
| chapter 10: ink on mid (tab, chips) | `#1B1E2F` | `#FF8854` | 6.99 | 4.5 | pass |
| chapter 10: ink on wash (boxes) | `#1B1E2F` | `#FFF3EE` | 15.16 | 4.5 | pass |
| chapter 10: muted on wash | `#5A5F73` | `#FFF3EE` | 5.82 | 4.5 | pass |
| chapter 10: ink on highlight | `#1B1E2F` | `#FFCAB4` | 11.28 | 4.5 | pass |
| chapter 10: deep on paper (labels) | `#723214` | `#FFFFFF` | 9.62 | 4.5 | pass |
| chapter 10: deep on soft (pointer) | `#723214` | `#FFE3D7` | 7.89 | 4.5 | pass |
| chapter 11: ink on mid (tab, chips) | `#1B1E2F` | `#FF855B` | 6.88 | 4.5 | pass |
| chapter 11: ink on wash (boxes) | `#1B1E2F` | `#FFF3EF` | 15.17 | 4.5 | pass |
| chapter 11: muted on wash | `#5A5F73` | `#FFF3EF` | 5.82 | 4.5 | pass |
| chapter 11: ink on highlight | `#1B1E2F` | `#FFC9B8` | 11.23 | 4.5 | pass |
| chapter 11: deep on paper (labels) | `#73311A` | `#FFFFFF` | 9.62 | 4.5 | pass |
| chapter 11: deep on soft (pointer) | `#73311A` | `#FFE2D9` | 7.85 | 4.5 | pass |
| chapter 12: ink on mid (tab, chips) | `#1B1E2F` | `#FF8161` | 6.73 | 4.5 | pass |
| chapter 12: ink on wash (boxes) | `#1B1E2F` | `#FFF3EF` | 15.17 | 4.5 | pass |
| chapter 12: muted on wash | `#5A5F73` | `#FFF3EF` | 5.82 | 4.5 | pass |
| chapter 12: ink on highlight | `#1B1E2F` | `#FFC9BB` | 11.25 | 4.5 | pass |
| chapter 12: deep on paper (labels) | `#74301F` | `#FFFFFF` | 9.61 | 4.5 | pass |
| chapter 12: deep on soft (pointer) | `#74301F` | `#FFE2DB` | 7.85 | 4.5 | pass |
| cover A1: cream on level field (large type) | `#FBF4E6` | `#00926E` | 3.59 | 3.0 | pass |
| cover A1: cream 300 on the lighter circle | `#FBF4E6` | `#00A17A` | 3.01 | 3.0 | pass |
| cover A2: cream on level field (large type) | `#FBF4E6` | `#D75B00` | 3.56 | 3.0 | pass |
| cover A2: cream 300 on the lighter circle | `#FBF4E6` | `#EB6400` | 3.02 | 3.0 | pass |
| cover B1: cream on level field (large type) | `#FBF4E6` | `#D32C4D` | 4.53 | 3.0 | pass |
| cover B1: cream 300 on the lighter circle | `#FBF4E6` | `#E5405C` | 3.68 | 3.0 | pass |
| cover B2: cream on level field (large type) | `#FBF4E6` | `#963AA5` | 5.57 | 3.0 | pass |
| cover B2: cream 300 on the lighter circle | `#FBF4E6` | `#A64AB5` | 4.49 | 3.0 | pass |
| cover C1: cream on level field (large type) | `#FBF4E6` | `#3641BC` | 7.27 | 3.0 | pass |
| cover C1: cream 300 on the lighter circle | `#FBF4E6` | `#4252CD` | 5.78 | 3.0 | pass |
| cover C2: cream on level field (large type) | `#FBF4E6` | `#006483` | 6.09 | 3.0 | pass |
| cover C2: cream 300 on the lighter circle | `#FBF4E6` | `#007397` | 4.92 | 3.0 | pass |
| cover: navy on cream band | `#161B36` | `#FBF4E6` | 15.42 | 4.5 | pass |
| cover: cream on navy badge | `#FBF4E6` | `#161B36` | 15.42 | 4.5 | pass |

## 8 · Cover

Every text element of the cover exists exactly once in the PDF (the level appears twice by design: in the badge and in the title).

| Element | expected | found | |
| --- | --- | --- | --- |
| 300 | 1 | 1 | pass |
| Niveau | 1 | 1 | pass |
| A2 (badge and title) | 2 | 2 | pass |
| Sayfada | 1 | 1 | pass |
| Almanca | 1 | 1 | pass |
| Türkçe açıklamalı | 1 | 1 | pass |
| Cevap anahtarı | 1 | 1 | pass |
| Kelime listeleri | 1 | 1 | pass |
| Ünite testleri | 1 | 1 | pass |
| Deutsch Fokus (logo) | 1 | 1 | pass |

## 9 · File size

- this build: 2066 KB for 20 pages (11 learning pages, 9 others); 99.4 KB per page without fonts
- full book, vector artwork only: about **35.3 MB** for roughly 362 pages
- full book with final illustrations: about 109 picture slots; at 150 KB each (JPEG, 150 dpi) that adds 16 MB → about **51 MB** (target: under 40 MB)
