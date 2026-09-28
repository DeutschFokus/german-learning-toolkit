"""Insert soft hyphens (U+00AD) into German prose, because headless Chrome has no
offline hyphenation dictionary. Only text between tags is touched; the visible
text is unchanged unless a line actually breaks there."""
import re

import pyphen

_dic = pyphen.Pyphen(lang="de_DE", left=3, right=3)
_WORD = re.compile(r"[A-Za-zÄÖÜäöüß]{8,}")
_SPLIT = re.compile(r"(<[^>]+>)")


SHY = chr(0xAD)


def _word(m: re.Match) -> str:
    # de_DE patterns split "-ti-o-nen"; German typesetting keeps "tio" together.
    return _dic.inserted(m.group(0), hyphen=SHY).replace("ti" + SHY + "o", "tio")


def hyphenate_html(html: str) -> str:
    parts = _SPLIT.split(html)
    return "".join(p if p.startswith("<") else _WORD.sub(_word, p) for p in parts)


_SUFFIX = re.compile(r"(?<![\w­])(-[a-zäöüß]{1,4}\b[?.,:;]?)")


def protect_suffixes(html: str) -> str:
    """Keep grammar suffixes such as "-e", "-en", "-es?" from breaking after their hyphen."""
    parts = _SPLIT.split(html)
    out = "".join(p if p.startswith("<") else _SUFFIX.sub(r'<span class="nobr">\1</span>', p) for p in parts)
    # an arrow never ends a line: bind it to what follows
    return out.replace("→ ", "→\u00a0")
