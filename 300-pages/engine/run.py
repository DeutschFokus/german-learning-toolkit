"""Orchestration for the command line: validate → build → PDF → post-process → previews → QA."""
from __future__ import annotations

import time
from pathlib import Path

from weasyprint import HTML

from .config import load_config
from .loader import format_log, load_book
from .pipeline import Builder


def edition_name(cfg) -> str:
    name = f"300-pages-{cfg.level}-{cfg.lang}"
    for flag in ("sample", "print", "forms"):
        if cfg.flags.get(flag):
            name += f"-{flag}"
    return name


def run_build(args, out: Path) -> int:
    t0 = time.time()
    cfg = load_config(args.level, args.lang, print=args.print_, sample=args.sample, forms=args.forms, draft=args.draft,
                      no_cache=getattr(args, "no_cache", False))
    book = load_book(cfg, args.chapters)
    log = format_log(book)
    print(log)
    if book.errors() and not args.draft:
        print("\nBuild stopped: fix the errors above (or use --draft to look at a broken build).")
        return 2
    builder = Builder(cfg, book)
    res = builder.build()
    t1 = time.time()
    layout_errors = [i for i in book.errors()]
    name = edition_name(cfg)
    if args.keep_html:
        (out / f"{name}.html").write_text(res.html, encoding="utf-8")
    doc = HTML(string=res.html, base_url=str(cfg.root)).render(pdf_forms=bool(args.forms), pdf_tags=True)
    t2 = time.time()
    from .post import finish_pdf
    pdf_path = out / f"{name}.pdf"
    raw = doc.write_pdf(pdf_forms=bool(args.forms), pdf_tags=True, custom_metadata=True)
    t3 = time.time()
    info = finish_pdf(raw, pdf_path, cfg, res, doc)
    t4 = time.time()
    print(f"\n{pdf_path.name}: {info['pages']} pages, {info['size'] / 1024:.0f} KB  "
          f"(layout {t1 - t0:.1f}s in {res.rounds} rounds · render {t2 - t1:.1f}s · write {t3 - t2:.1f}s · post {t4 - t3:.1f}s)")
    if args.preview:
        from .preview import make_previews
        pdir = make_previews(pdf_path, out / "preview" / name, res, dpi=args.dpi)
        print(f"previews → {pdir}")
    if not args.no_qa:
        from .qa import write_report
        rep = write_report(pdf_path, out / "qa" / f"{name}-qa.md", cfg, book, res, doc, info, log, timings={
            "layout": t1 - t0, "render": t2 - t1, "write": t3 - t2, "post": t4 - t3})
        print(f"QA report → {rep}")
    if layout_errors:
        print("\n" + "\n".join(str(i) for i in layout_errors))
        return 0 if args.draft else 1
    return 0


def run_covers(out: Path, langs=None) -> None:
    from .covers import export_all
    export_all(out / "covers", langs)
