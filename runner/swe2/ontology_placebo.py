"""Placebo graph: briefs/PLACEBO.md (generic style rules, irrelevant to the bug families) cast into
the same ontology, so the PLACEBO arm gets an identically formatted, similar-sized graph."""
import os
import re

_SRC = os.path.join(os.path.dirname(__file__), "..", "..", "briefs", "PLACEBO.md")
_STOP = {"and", "the", "of", "for", "with", "to", "a", "in", "on"}


def _build():
    text = open(_SRC, encoding="utf-8").read()
    nodes, triples = {}, []
    for m in re.finditer(r"### Rule (P\d+): (.+?)\n(.+?)(?=\n### |\n## |\Z)", text, re.DOTALL):
        rid, title, body = m.group(1), m.group(2).strip(), m.group(3).strip()
        words = [w.lower() for w in re.findall(r"[A-Za-z]+", title) if w.lower() not in _STOP]
        nodes[rid] = {"class": "Convention", "label": title.lower(), "value": None, "aliases": words}
        sents = [s.strip() for s in re.split(r"(?<=\.)\s+", body.replace("\n", " ")) if s.strip()]
        for i, s in enumerate(sents, 1):
            nid = f"{rid}.b{i}"
            nodes[nid] = {"class": "Behavior", "label": s.rstrip("."), "value": None, "aliases": []}
            triples.append([rid, "requires", nid])
        for lit in re.findall(r"`([^`]+)`", body):
            nid = f"{rid}.l{len([t for t in triples if t[0] == rid]) + 1}"
            nodes[nid] = {"class": "Literal", "label": "identifier", "value": lit, "aliases": []}
            triples.append([rid, "uses_literal", nid])
    return nodes, triples


NODES, TRIPLES = _build()
