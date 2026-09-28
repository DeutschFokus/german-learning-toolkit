"""Stage 2: three front-cover concepts, a back cover and a spine/spread guide.
Usage: python3 build_covers.py OUTDIR"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
DESIGN = HERE.parent
OUT = Path(sys.argv[1])
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# Placeholders the author replaces before print.
SERIES = "DeutschFokus · Fehlerwerkstatt"
AUTHOR = "Vorname Nachname"
AUDIENCE = "Für Lernende auf Niveau B1, die den Sprung zu B2 schaffen wollen"

# Spine estimate: ~112 pages, 90 g/m² book paper, ~0.117 mm per leaf.
PAGES, LEAF_MM = 112, 0.117
SPINE = round(PAGES / 2 * LEAF_MM + 0.4, 1)   # + cover board allowance
BLEED = 3

GRAIN = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 .35  0 0 0 0 .28  0 0 0 0 .2  0 0 0 .075 0'/></filter>"
         "<rect width='100%25' height='100%25' filter='url(%23n)'/></svg>\")")
GRAIN_DARK = GRAIN.replace(".35  0 0 0 0 .28  0 0 0 0 .2  0 0 0 .075", "1  0 0 0 0 1  0 0 0 0 1  0 0 0 .06")

# Teacher's-pen marks. Strokes use non-scaling-stroke so they stay pen-width at any size.
STRIKE = ('<svg class="pen strike" viewBox="0 0 100 20" preserveAspectRatio="none">'
          '<path d="M1 13 C 22 10.5, 55 12.5, 99 7" /><path class="ghost" d="M3 14 C 30 11.5, 62 13, 97 8.5" /></svg>')
CARET = ('<svg class="pen caret" viewBox="0 0 20 24" preserveAspectRatio="none">'
         '<path d="M2 22 C 5 15, 8 8, 10 1 C 12 9, 15 15, 18 22" /></svg>')


def correction(cls=""):
    return (f'<p class="corr {cls}">Jetzt <span class="del">ich{STRIKE}</span> arbeite'
            f'<span class="ins">{CARET}<span class="insw">ich</span></span>.</p>')


def badge(color="currentColor", size="31mm"):
    return f"""<svg class="badge" style="width:{size};height:{size};color:{color}" viewBox="0 0 100 100">
  <defs><path id="ring" d="M50,50 m-38,0 a38,38 0 1,1 76,0 a38,38 0 1,1 -76,0" /></defs>
  <circle cx="50" cy="50" r="47" fill="none" stroke="currentColor" stroke-width=".6"/>
  <circle cx="50" cy="50" r="30" fill="none" stroke="currentColor" stroke-width=".35"/>
  <text font-family="B1 Sans" font-size="6.3" font-weight="600" letter-spacing="2.1" fill="currentColor">
    <textPath href="#ring" startOffset="0">DEUTSCH · NIVEAU · DEUTSCH · NIVEAU ·</textPath></text>
  <text x="50" y="47" text-anchor="middle" font-family="B1 Serif Display" font-weight="600" font-size="17" fill="currentColor">B1</text>
  <path d="M40 53 H60 M55 49 L60 53 L55 57" stroke="currentColor" stroke-width="1.1" fill="none" stroke-linecap="round"/>
  <text x="50" y="70" text-anchor="middle" font-family="B1 Serif Display" font-weight="600" font-size="17" fill="currentColor">B2</text>
</svg>"""


def css(page_w, page_h):
    return (DESIGN / "fonts.css").read_text().replace("url(fonts/", "url(../fonts/") + (DESIGN / "tokens.css").read_text() + f"""
@page {{ size: {page_w}mm {page_h}mm; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; }}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; font-kerning: normal; text-rendering: geometricPrecision; font-synthesis: none; }}
body {{ font-family: var(--font-text); color: var(--ink); }}
.page {{ width: {page_w}mm; height: {page_h}mm; position: relative; overflow: hidden; break-after: page; }}
.sans {{ font-family: var(--font-sans); }}
.tracked {{ font-family: var(--font-sans); font-size: 7.6pt; font-weight: 600; letter-spacing: .22em; text-transform: uppercase; }}
:root {{ --pen: #B8322A; --cream: #F4EDDF; --cream-2: #EFE6D3; }}

/* pen marks */
.corr {{ font-family: var(--font-display); font-weight: 400; white-space: nowrap; }}
.del {{ position: relative; }}
.pen {{ position: absolute; overflow: visible; fill: none; stroke: var(--pen); stroke-linecap: round; stroke-linejoin: round; }}
.pen path {{ vector-effect: non-scaling-stroke; stroke-width: 2.6px; }}
.pen .ghost {{ stroke-width: 1.2px; opacity: .55; }}
.strike {{ left: -12%; width: 124%; top: 30%; height: .32em; }}
.ins {{ position: relative; display: inline-block; width: .16em; }}
.caret {{ left: -.06em; top: -.08em; width: .28em; height: .36em; }}
.caret path {{ stroke-width: 2.2px; }}
.insw {{ position: absolute; left: -.42em; top: -1.4em; line-height: 1; font-family: var(--font-display); font-style: italic; color: var(--pen);
         transform: rotate(-6deg); transform-origin: left bottom; font-size: .92em; }}
"""


# ---------------------------------------------------------------------------
# Concept A — "Rotstift": cream editorial, cropped petrol 100, pen correction.
# ---------------------------------------------------------------------------
A = f"""
<section class="page A">
  <div class="a-top"><span class="tracked">{SERIES}</span></div>
  <div class="a-100">100</div>
  <div class="a-title">
    <h1>B1-Fehler</h1>
    <p class="a-sub">Korrigiere sie vor B2</p>
  </div>
  <div class="a-card">
    <div class="a-card-label tracked">Fehler Nr. 001 · Satzbau</div>
    {correction("a-corr")}
  </div>
  {badge("#095255")}
  <div class="a-foot">
    <p class="a-aud">{AUDIENCE}</p>
    <p class="a-author tracked">{AUTHOR}</p>
  </div>
</section>"""
A_CSS = f"""
.A {{ background: var(--cream); background-image: {GRAIN}; }}
.A::before {{ content: ""; position: absolute; left: 16mm; right: 16mm; top: 26mm; border-top: .5pt solid #8C7F66; }}
.A::after {{ content: ""; position: absolute; left: 16mm; right: 16mm; bottom: 30mm; border-top: .5pt solid #8C7F66; }}
.a-top {{ position: absolute; left: 16mm; top: 16mm; color: #5E5443; }}
.a-100 {{ position: absolute; left: -9mm; top: 23mm; font-family: var(--font-display); font-weight: 900; font-size: 318pt; line-height: .8;
          letter-spacing: -.055em; color: var(--primary); font-feature-settings: "lnum" 1; }}
.a-title {{ position: absolute; left: 16mm; top: 146mm; }}
.a-title h1 {{ font-family: var(--font-display); font-weight: 600; font-size: 64pt; line-height: 1; letter-spacing: -.012em; color: var(--ink); }}
.a-sub {{ font-family: var(--font-display); font-style: italic; font-size: 25pt; margin-top: 4mm; color: #3F4A4C; }}
.a-card {{ position: absolute; left: 16mm; top: 196mm; width: 178mm; padding-top: 5mm; border-top: 1.5pt solid var(--ink); }}
.a-card-label {{ color: #6E6450; font-size: 6.8pt; }}
.a-corr {{ font-size: 40pt; margin-top: 17mm; color: var(--ink); }}
.A .badge {{ position: absolute; right: 16mm; top: 150mm; }}
.a-foot {{ position: absolute; left: 16mm; right: 16mm; bottom: 12mm; display: flex; justify-content: space-between; align-items: baseline; }}
.a-aud {{ font-family: var(--font-sans); font-size: 8.4pt; color: #4E4636; }}
.a-author {{ color: var(--ink); font-size: 8pt; }}
"""

# ---------------------------------------------------------------------------
# Concept B — "Karteikarte": deep petrol, outlined 100, school index card.
# ---------------------------------------------------------------------------
B = f"""
<section class="page B">
  <div class="b-frame"></div>
  <div class="b-top tracked">{SERIES}</div>
  <div class="b-100">100</div>
  <div class="b-card">
    <div class="b-rule-red"></div>
    <div class="b-card-head tracked">Fehler Nr. 001 · Satzbau</div>
    {correction("b-corr")}
    <div class="b-card-foot sans">Verb auf Position 2 → <em>Jetzt arbeite ich.</em></div>
  </div>
  <div class="b-title">
    <h1>B1-Fehler</h1>
    <p class="b-sub">Korrigiere sie vor B2</p>
  </div>
  <div class="b-foot"><span class="sans b-aud">{AUDIENCE}</span><span class="tracked">{AUTHOR}</span></div>
  {badge("#D9A55B", "27mm")}
</section>"""
B_CSS = f"""
.B {{ background: #0B4A4F; background-image: {GRAIN_DARK}; color: #F4EDDF; }}
.b-frame {{ position: absolute; inset: 11mm; border: .6pt solid rgba(217,165,91,.75); }}
.b-top {{ position: absolute; left: 20mm; top: 19mm; color: #D9A55B; }}
.b-100 {{ position: absolute; right: -14mm; top: 8mm; font-family: var(--font-display); font-weight: 900; font-size: 300pt; line-height: .8;
          letter-spacing: -.05em; color: transparent; -webkit-text-stroke: 1.1pt rgba(244,237,223,.85); font-feature-settings: "lnum" 1; }}
.b-card {{ position: absolute; left: 20mm; top: 118mm; width: 150mm; height: 70mm; background: #FBF7EE; color: var(--ink);
           transform: rotate(-2.2deg); box-shadow: 0 1.2mm 3mm rgba(0,0,0,.28), 0 .2mm .6mm rgba(0,0,0,.25);
           background-image: repeating-linear-gradient(to bottom, transparent 0, transparent 8.6mm, rgba(70,120,160,.28) 8.6mm, rgba(70,120,160,.28) 8.85mm);
           background-position: 0 14mm; padding: 6mm 9mm 0 22mm; }}
.b-rule-red {{ position: absolute; left: 15mm; top: 0; bottom: 0; border-left: .9pt solid rgba(184,50,42,.75); }}
.b-card-head {{ font-size: 6.6pt; color: #6E6450; }}
.b-corr {{ font-size: 28pt; margin-top: 15.5mm; }}
.b-card-foot {{ position: absolute; left: 22mm; bottom: 6mm; font-size: 8.6pt; color: #4F575B; }}
.b-title {{ position: absolute; left: 20mm; top: 206mm; }}
.b-title h1 {{ font-family: var(--font-display); font-weight: 600; font-size: 60pt; line-height: 1; color: #FBF7EE; }}
.b-sub {{ font-family: var(--font-display); font-style: italic; font-size: 24pt; margin-top: 3mm; color: #D9A55B; }}
.b-foot {{ position: absolute; left: 20mm; right: 20mm; bottom: 19mm; display: flex; justify-content: space-between; align-items: baseline; color: #F4EDDF; }}
.b-aud {{ font-size: 8.2pt; opacity: .85; }}
.B .badge {{ position: absolute; right: 20mm; top: 214mm; }}
"""

# ---------------------------------------------------------------------------
# Concept C — "Korrekturrand": exercise-book lineature, red margin, margin marks.
# ---------------------------------------------------------------------------
C = f"""
<section class="page C">
  <div class="c-lines"></div>
  <div class="c-margin"></div>
  <div class="c-marks"><span style="top:62mm">Sb</span><span style="top:131mm">Gr</span><span style="top:209mm">St</span></div>
  <div class="c-top tracked">{SERIES}</div>
  <div class="c-100"><span>1</span><span class="c-zero">0</span><span>0</span>
    <svg class="c-circle" viewBox="0 0 100 100"><path d="M60 7 C 30 1, 6 24, 8 54 C 10 83, 36 97, 60 93 C 87 88, 98 60, 91 34 C 85 14, 66 4, 38 11" /></svg></div>
  <div class="c-title"><h1><span class="c-wave">B1-Fehler</span></h1><p class="c-sub">Korrigiere sie vor B2</p></div>
  {correction("c-corr")}
  <div class="c-band">
    <div><p class="c-aud">{AUDIENCE}</p><p class="tracked c-author">{AUTHOR}</p></div>
    {badge("#F4EDDF", "26mm")}
  </div>
</section>"""
C_CSS = f"""
.C {{ background: #F7F2E6; background-image: {GRAIN}; }}
.c-lines {{ position: absolute; inset: 0 0 52mm 0; background-image: repeating-linear-gradient(to bottom, transparent 0, transparent 9.3mm, rgba(80,120,150,.22) 9.3mm, rgba(80,120,150,.22) 9.55mm); background-position: 0 3mm; }}
.c-margin {{ position: absolute; top: 0; bottom: 52mm; left: 34mm; border-left: 1pt solid rgba(184,50,42,.7); }}
.c-marks span {{ position: absolute; left: 14mm; font-family: var(--font-display); font-style: italic; font-size: 19pt; color: var(--pen); transform: rotate(-8deg); }}
.c-top {{ position: absolute; left: 42mm; top: 15mm; color: #5E5443; }}
.c-100 {{ position: absolute; left: 40mm; top: 28mm; font-family: var(--font-display); font-weight: 700; font-size: 176pt; line-height: 1; letter-spacing: -.03em; color: var(--ink); font-feature-settings: "lnum" 1; }}
.c-zero {{ position: relative; }}
.c-circle {{ position: absolute; left: 34.5%; top: 6%; width: 36%; height: 86%; overflow: visible; fill: none; stroke: var(--pen); stroke-linecap: round; }}
.c-circle path {{ vector-effect: non-scaling-stroke; stroke-width: 3px; }}
.c-title {{ position: absolute; left: 42mm; top: 113mm; }}
.c-title h1 {{ font-family: var(--font-display); font-weight: 600; font-size: 56pt; line-height: 1.1; }}
.c-wave {{ text-decoration: underline wavy var(--pen); text-decoration-thickness: 1.6pt; text-underline-offset: 9pt; }}
.c-sub {{ font-family: var(--font-display); font-style: italic; font-size: 24pt; margin-top: 7mm; color: #3F4A4C; }}
.c-corr {{ position: absolute; left: 42mm; top: 196mm; font-size: 30pt; }}
.c-band {{ position: absolute; left: 0; right: 0; bottom: 0; height: 52mm; background: var(--primary); color: #F4EDDF; display: flex; justify-content: space-between; align-items: center; padding: 0 18mm 0 42mm; }}
.c-aud {{ font-family: var(--font-display); font-size: 13pt; line-height: 1.35; max-width: 105mm; }}
.c-author {{ margin-top: 5mm; font-size: 7.6pt; color: #D9A55B; }}
"""

# ---------------------------------------------------------------------------
# Back cover (for the recommended concept A) and spread/spine guide.
# ---------------------------------------------------------------------------
BACK = f"""
<section class="page A back">
  <div class="a-top"><span class="tracked">{SERIES}</span></div>
  <h2 class="bk-head">Du sprichst schon Deutsch.<br>Jetzt wird es richtig.</h2>
  <p class="bk-blurb">Du verstehst viel und kommst im Alltag gut zurecht – und trotzdem kommen dieselben Fehler immer wieder?
  Dieses Buch sammelt 100 Fehlermuster, die im Deutschunterricht immer wieder auftauchen, und zeigt dir, wie du sie
  ein für alle Mal korrigierst: kurz, klar und mit Beispielen aus dem echten Leben.</p>
  <ul class="bk-list">
    <li><b>Jeder Fehler auf einen Blick:</b> falsch, richtig, eine Regel – keine Theorieberge.</li>
    <li><b>Teste dich selbst:</b> Einstufungstest, 100 Mini-Tests und ein Abschlusstest zeigen dir, wo du stehst.</li>
    <li><b>Mit B2-Upgrades:</b> So klingt dein Deutsch natürlich statt übersetzt.</li>
  </ul>
  {correction("bk-corr")}
  <div class="bk-bottom">
    {badge("#095255", "24mm")}
    <div class="bk-imprint"><p class="tracked">{SERIES.split(" · ")[0]}</p><p class="sans">Niveau B1 → B2 · Deutsch als Fremdsprache</p></div>
    <div class="bk-isbn"><div class="bk-bars"></div><p class="sans">ISBN 978-3-XXXX-XXXX-X</p><p class="sans bk-ph">Platzhalter · EAN-13-Strichcode 50 × 30 mm</p></div>
  </div>
</section>"""
BACK_CSS = """
.back::before { top: 26mm; } .back::after { display: none; }
.bk-head { position: absolute; left: 24mm; top: 40mm; width: 150mm; font-family: var(--font-display); font-weight: 600; font-size: 30pt; line-height: 1.12; color: var(--primary); }
.bk-blurb { position: absolute; left: 24mm; top: 82mm; width: 138mm; font-size: 12pt; line-height: 1.55; color: var(--ink); hyphens: manual; }
.bk-list { position: absolute; left: 24mm; top: 132mm; width: 138mm; list-style: none; padding: 0; font-size: 11pt; line-height: 1.5; }
.bk-list li { position: relative; padding-left: 8mm; margin-bottom: 4mm; }
.bk-list li::before { content: ""; position: absolute; left: 0; top: .7em; width: 4.5mm; border-top: 1.4pt solid var(--pen); }
.bk-list b { font-weight: 600; }
.bk-corr { position: absolute; left: 24mm; top: 196mm; font-size: 24pt; }
.back .badge { position: static; flex: none; }
.bk-bottom { position: absolute; left: 24mm; right: 16mm; bottom: 16mm; display: flex; align-items: flex-end; gap: 8mm; }
.bk-imprint { flex: 1; color: #4E4636; font-size: 8pt; line-height: 1.6; }
.bk-isbn { width: 50mm; background: #fff; padding: 3mm; text-align: center; font-size: 6.6pt; color: #333; border: .4pt solid #bbb; }
.bk-bars { height: 18mm; background: repeating-linear-gradient(90deg, #222 0 .5mm, transparent .5mm .9mm, #222 .9mm 1.1mm, transparent 1.1mm 1.8mm); opacity: .25; margin-bottom: 1.5mm; }
.bk-ph { color: #999; margin-top: .5mm; }
"""


def spread_html():
    w = BLEED + 210 + SPINE + 210 + BLEED
    h = BLEED + 297 + BLEED
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><style>{css(w, h)}
.sp {{ width: {w}mm; height: {h}mm; position: relative; background: var(--cream); background-image: {GRAIN}; }}
.g {{ position: absolute; }}
.trim {{ border: .5pt solid #1A73E8; }}
.safe {{ border: .5pt dashed #E8711A; }}
.spine {{ background: var(--primary); }}
.lab {{ position: absolute; font-family: var(--font-sans); font-size: 7pt; color: #1A73E8; background: rgba(255,255,255,.85); padding: .6mm 1.2mm; }}
.spine-t {{ position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(90deg); white-space: nowrap; color: #F4EDDF; display: flex; gap: 8mm; align-items: baseline; }}
.spine-t b {{ font-family: var(--font-display); font-weight: 600; font-size: 13pt; }}
.spine-t i {{ font-family: var(--font-display); font-size: 9.5pt; color: #D9A55B; }}
.spine-t span {{ font-family: var(--font-sans); font-size: 6.5pt; letter-spacing: .2em; text-transform: uppercase; }}
.ghost-panel {{ position: absolute; font-family: var(--font-display); color: rgba(9,82,85,.15); font-size: 120pt; font-weight: 900; }}
.tbl {{ position: absolute; right: {BLEED + 12}mm; bottom: {BLEED + 12}mm; background: #fff; padding: 4mm 5mm; font-family: var(--font-sans); font-size: 7.5pt; border: .5pt solid #1A73E8; line-height: 1.5; }}
.tbl table {{ border-collapse: collapse; }} .tbl td, .tbl th {{ padding: .5mm 3mm .5mm 0; text-align: left; }}
</style></head><body><div class="sp">
  <div class="g trim" style="left:{BLEED}mm;top:{BLEED}mm;width:{210 + SPINE + 210}mm;height:297mm"></div>
  <div class="g safe" style="left:{BLEED + 6}mm;top:{BLEED + 6}mm;width:198mm;height:285mm"></div>
  <div class="g safe" style="left:{BLEED + 210 + SPINE + 6}mm;top:{BLEED + 6}mm;width:198mm;height:285mm"></div>
  <div class="g spine" style="left:{BLEED + 210}mm;top:0;width:{SPINE}mm;height:{h}mm">
    <div class="spine-t"><span>{AUTHOR}</span><b>100 B1-Fehler</b><i>Korrigiere sie vor B2</i><span>DeutschFokus</span></div></div>
  <div class="ghost-panel" style="left:{BLEED + 60}mm;top:110mm">Rücken-<br>seite</div>
  <div class="ghost-panel" style="left:{BLEED + 210 + SPINE + 40}mm;top:110mm">Vorder-<br>seite</div>
  <div class="lab" style="left:{BLEED + 2}mm;top:{BLEED + 1}mm">Beschnitt (Trim) · blau</div>
  <div class="lab" style="left:{BLEED + 8}mm;top:{BLEED + 8}mm;color:#E8711A">Sicherheitsabstand 6 mm · orange</div>
  <div class="lab" style="left:{BLEED + 210 - 30}mm;top:{h / 2 - 3}mm">Rücken {SPINE} mm →</div>
  <div class="lab" style="left:0;top:{h - 8}mm">Anschnitt (Bleed) 3 mm rundum</div>
  <div class="tbl"><b>Rückenstärke (Schätzung)</b><br>= Seiten ÷ 2 × Blattstärke + 0,4 mm<br>
    <table><tr><th>Seiten</th><th>80 g Offset (0,100 mm)</th><th>90 g Werkdruck (0,117 mm)</th></tr>
    {''.join(f'<tr><td>{p}</td><td>{p / 2 * 0.100 + 0.4:.1f} mm</td><td>{p / 2 * 0.117 + 0.4:.1f} mm</td></tr>' for p in (96, 112, 128, 144))}
    </table>Endwert immer mit dem Rechner der Druckerei prüfen.<br>Rückentext läuft von oben nach unten (ISO/DIN-Empfehlung).</div>
</div></body></html>"""


def render(name, html):
    src = HERE / f"{name}.html"
    src.write_text(html, encoding="utf-8")
    pdf = OUT / f"{name}.pdf"
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", "--virtual-time-budget=10000", src.as_uri()], check=True, capture_output=True)
    return pdf


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    base = css(210, 297) + A_CSS + B_CSS + C_CSS + BACK_CSS
    doc = lambda body: f'<!doctype html><html lang="de"><head><meta charset="utf-8"><style>{base}</style></head><body>{body}</body></html>'
    render("covers", doc(A + B + C + BACK))
    render("spread", spread_html())
    print("spine", SPINE, "mm")


if __name__ == "__main__":
    main()
