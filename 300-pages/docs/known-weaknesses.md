## The five weakest things – and how to fix them

**1 · The pictures are placeholders.**
The demo proves the layout, not the look of a finished page. Nine picture slots show a calm
placeholder with the brief; the picture dictionary on page 102 teaches twelve words with a
picture that does not exist yet, and its pin positions are estimates. A course book lives from
its pictures – this is the largest gap between the demo and a product.
*Fix:* produce the pictures from `docs/image-briefs-a2.md` in the style of
`docs/illustration-style-guide.md`, starting with `k5-wohnung`; switch each one on with `src:`
and correct the pins in the content file. A full book needs about a hundred.

**2 · The print file is RGB, not PDF/X.**
`--print` adds 3 mm bleed, crop marks, TrimBox and BleedBox, and the tabs and cover really bleed.
But all colours are sRGB, black text is RGB black (on an offset press it would print in four
inks), and there is no output intent. Print-on-demand services that accept RGB will be fine;
an offset printer will send the file back.
*Fix:* add a last step to `--print` that converts to PDF/X-4 with a CMYK profile and pure-black
text (Ghostscript: `-dPDFX -sColorConversionStrategy=CMYK` with a black-preserving profile), then
run the result through a preflight tool once per level. Until then the PDF is a digital product.

**3 · The pages fit because the text was cut to fit.**
Every section has a fixed page budget and the build stops when a section is one line too long.
That is the point – nothing overflows silently – but it makes writing slow: pages 107 and 115
have half a line to spare in English, Turkish explanations run a little longer, and seventy-one
more chapters mean many rounds of trimming.
*Fix:* `tools/layout_report.py` already shows lines used per page and per block. Next step: let
the paginator squeeze before it fails (close the gaps between blocks by up to half a line,
let pictures shrink below their default height) and say in the error which block to shorten by
how many lines.

**4 · Long texts cannot run over a page, and the dense levels are only scaled.**
Every block is placed whole. That is right for A1–B1. At B2–C2 a full-page article with tasks
will not fit, and the level files only make type smaller and lines closer – there is no
two-column setting for long reading texts yet.
*Fix:* make `reading_text` breakable between paragraphs with running line numbers (the lines of
every paragraph are already measured), and add a two-column variant for B2–C2. This is needed
before the first B2 chapter, not before A1–B1.

**5 · Fillable fields and accessibility are a first step.**
In the `--forms` edition the answer circles of a multiple-choice question are independent tick
boxes (two can be ticked), nothing is checked or scored, and each PDF viewer draws typed text in
its own way. The PDF is tagged, every figure has alternative text and the language is set, but
the reading order follows the source – a margin note is read after its task – and it has not
been tested with a screen reader or a PDF/UA checker.
*Fix:* turn options into radio groups in `engine/post.py`; test the reading order with NVDA and
VoiceOver, then run PAC and fix what it reports.

**Smaller things**

- Phrase lists and chat bubbles keep their own rhythm; that is the 2–3 % of lines on the
  quarter grid instead of the half grid.
- With `design.opener: register` the side column of the opener is not on the baseline grid.
- Web address, shop link, audio links, contact and logo are placeholders; the audio itself does
  not exist. All links and QR codes are built from `series.yaml`.
- Only one chapter and one station exist. Build time and file size of a 300-page book are
  extrapolated from them.
- The word list gives page numbers only for the chapters that were built.
