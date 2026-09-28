"""Compare the words of two PDFs, ignoring layout (line breaks, hyphenation, spacing).
Prints every word run that was deleted or replaced from OLD, and a summary of insertions."""
import collections
import difflib
import re
import subprocess
import sys


def words(pdf):
    t = subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, "-"], capture_output=True, text=True).stdout
    t = t.replace("­", "").replace(" ", " ")
    t = re.sub(r"-\s*\n\s*", "", t)          # hyphenated line ends (soft or hard)
    t = t.replace("-", "")                    # remaining hyphens: wrap-position dependent
    return t.split()


old, new = words(sys.argv[1]), words(sys.argv[2])
sm = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
deleted, inserted = [], collections.Counter()
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op in ("delete", "replace"):
        deleted.append((" ".join(old[i1:i2]), " ".join(new[j1:j2])))
    if op in ("insert", "replace"):
        inserted.update(new[j1:j2])
print(f"old words: {len(old)}  new words: {len(new)}  matched: {sum(b.size for b in sm.get_matching_blocks())}")
print(f"runs removed/replaced from old: {len(deleted)}")
for a, b in deleted:
    print(f"  - {a[:90]!r}  ->  {b[:90]!r}")
