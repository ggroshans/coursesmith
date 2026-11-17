"""Sentence splitting over cleaned page text, unchanged from the chronicle's extract.py so sentence ids match.

iter_sentences yields (section, sentence_with_markers, is_table_row); clean_sentence strips footnote
markers and maintenance tags and returns them separately.
"""
import re

TAGS = (r"citation needed|clarification needed|update|failed verification|when\?|dubious – discuss|"
        r"according to whom\?|needs update\?|further explanation needed|disputed – discuss|by whom\?|"
        r"better source needed|who\?|verification needed|vague|specify|self-published source|quantify|"
        r"page needed|unreliable source\?|original research\?|non-primary source needed|which\?|where\?|"
        r"full citation needed|irrelevant citation|year needed|dubious|disputed|contradictory")
TAG_RE = re.compile(rf"\[(?:{TAGS})\]")
MARK_RE = re.compile(r"\[\^(\d+)\]")
SPLIT_RE = re.compile(r"(?<=[.!?])((?:\s*\[\^\d+\])*)\s+(?=[A-Z0-9\"“(\[])")
ABBREV_END = re.compile(r"(?:\b(?:St|Mt|Dr|Mr|Mrs|Jr|Sr|al|ca|c|cf|vs|approx|Fig|figs?|No|nos|Vol|pp?|ed|eds|"
                        r"Bros|Inc|Co|Ltd|Prof|Gen|Lt|Col|Capt|Sgt|Ave|U\.S|e\.g|i\.e|etc|var|sp|spp|"
                        r"[A-Z])\.)$")

# Later sentences of a list item carry this prefix, so a bullet's leading context can be inherited.
CONT_MARK = "⁣"


def iter_sentences(text):
    """Yield (section, sentence_with_markers, is_table_row)."""
    stack = []
    for line in text.splitlines():
        if not line.strip():
            continue
        h = re.match(r"^(#+)\s+(.*)$", line)
        if h:
            lvl = len(h.group(1))
            stack = [s for s in stack if s[0] < lvl] + [(lvl, h.group(2).strip())]
            continue
        section = " > ".join(s[1] for s in stack if s[0] > 1) or "(lead)"
        if " | " in line or "Temporal range:" in line:
            yield ("infobox" if "Temporal range:" in line else section), line.strip(), " | " in line
            continue
        parts = SPLIT_RE.split(line)
        sents = []
        for i in range(0, len(parts), 2):
            s = parts[i] + (parts[i + 1] if i + 1 < len(parts) else "")
            s = s.strip()
            if not s:
                continue
            if sents and (TAG_RE.match(s) and TAG_RE.sub("", s).strip() == "" or ABBREV_END.search(sents[-1])):
                sents[-1] = sents[-1] + " " + s
            else:
                sents.append(s)
        bullet = line.lstrip().startswith("- ")
        for i, s in enumerate(sents):
            yield section, (s if not (bullet and i) else CONT_MARK + s), False


def clean_sentence(s):
    """(sentence without markers/tags, footnote numbers, tags)."""
    s = s.replace(CONT_MARK, "")
    cites = [int(n) for n in MARK_RE.findall(s)]
    tags = [t.strip("[]") for t in TAG_RE.findall(s)]
    plain = re.sub(r"\s+", " ", TAG_RE.sub("", MARK_RE.sub("", s))).strip()
    plain = re.sub(r"\s+([.,;:])", r"\1", plain)
    return plain, cites, tags
