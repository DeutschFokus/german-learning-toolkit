#!/usr/bin/env python3
"""300 Pages of German — build a book.

    python build.py --level a2 --lang en --chapters 5,Z2 --preview
    python build.py --level a2 --lang tr --chapters 5,Z2 --preview
    python build.py --level a2 --lang en --print          # 3 mm bleed + crop marks
    python build.py --level a2 --lang en --sample         # free sample + sales page
    python build.py --level a2 --lang en --forms          # fillable fields for tablets
    python build.py --covers                              # cover PNGs for all levels
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--level", default="a2", help="a1 … c2")
    ap.add_argument("--lang", default="en", help="explanation language (en, tr)")
    ap.add_argument("--chapters", default=None, help="what to build, e.g. 5 or 1-4,Z1 or 5,Z2 (default: everything that has content)")
    ap.add_argument("--print", dest="print_", action="store_true", help="print edition: 3 mm bleed and crop marks")
    ap.add_argument("--sample", action="store_true", help="free-sample edition (selected pages + sales page)")
    ap.add_argument("--forms", action="store_true", help="fillable form fields on write-in lines and tick boxes")
    ap.add_argument("--preview", action="store_true", help="PNG preview of every page + contact sheets")
    ap.add_argument("--dpi", type=int, default=110, help="preview resolution")
    ap.add_argument("--no-qa", action="store_true", help="skip the QA report")
    ap.add_argument("--covers", action="store_true", help="export cover PNGs (store + social) and the six-level line-up")
    ap.add_argument("--promo", action="store_true", help="store-preview images (1920x1080) from the built PDF of --level/--lang")
    ap.add_argument("--draft", action="store_true", help="build even if validation reports errors")
    ap.add_argument("--out", default=str(ROOT / "dist"), help="output folder")
    ap.add_argument("--keep-html", action="store_true", help="also write the intermediate HTML")
    ap.add_argument("--no-cache", action="store_true", help="measure every block again (ignore .cache/)")
    args = ap.parse_args(argv)

    from engine.run import run_build, run_covers
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if args.promo:
        from engine.promo import export
        pdf = out / f"300-pages-{args.level}-{args.lang}.pdf"
        if not pdf.exists():
            raise SystemExit(f"Build the book first: {pdf.name} is missing.")
        for f in export(out / "promo", args.level, args.lang, pdf):
            print(f"  {f.name}")
        return 0
    if args.covers:
        run_covers(out, langs=[args.lang] if "--lang" in (argv or sys.argv) else None)
        print(f"covers done in {time.time() - t0:.1f}s → {out / 'covers'}")
        return 0
    return run_build(args, out)


if __name__ == "__main__":
    raise SystemExit(main())
