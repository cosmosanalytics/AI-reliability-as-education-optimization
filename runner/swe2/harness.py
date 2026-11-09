"""SWE-2 knowledge harness: ontology schema, context index, and retrieval over the knowledge graph.

The student sees only renderings produced here (typed triples), never the handbook prose."""
import math
import re

import ontology

SCHEMA = (
    "ONTOLOGY (classes): Convention = a house rule of this codebase; Domain = code area it governs; "
    "Scope = where it (or an exception) applies; Behavior = what code must do; Alternative = a "
    "practice it prohibits; Format = an exact string/record layout; Literal = an exact token, name or "
    "value; Case = a worked example (input -> output).\n"
    "RELATIONS: governs, applies_to, requires, prohibits, has_format, uses_literal, except_in, "
    "exception_requires, derived_by, has_part, has_case, case_input, case_output."
)

_CACHE = {}


def graph(source):
    if source not in _CACHE:
        g = ontology.build(source)
        out = {}
        for s, p, o in g["triples"]:
            out.setdefault(s, []).append((p, o))
        conv = [i for i, n in g["nodes"].items() if n["class"] == "Convention"]
        _CACHE[source] = {"nodes": g["nodes"], "triples": g["triples"], "out": out, "conventions": conv}
    return _CACHE[source]


def _fmt_node(n):
    s = f"{n['class']}: {n['label']}"
    if n.get("value"):
        s += f" = `{n['value']}`"
    return s


def render_convention(cid, source="handbook"):
    g = graph(source)
    lines = [f"[{cid}] {_fmt_node(g['nodes'][cid])}"]

    def walk(nid, depth, seen):
        for p, o in g["out"].get(nid, []):
            lines.append("  " * depth + f"{p} -> {_fmt_node(g['nodes'][o])}")
            if o not in seen and g["nodes"][o]["class"] != "Convention":
                walk(o, depth + 1, seen | {o})

    walk(cid, 1, {cid})
    return "\n".join(lines)


def context_index(source="handbook"):
    """Context graph entry points: one line per convention (id, label, governed area/scope)."""
    g = graph(source)
    rows = []
    for cid in g["conventions"]:
        where = [g["nodes"][o]["label"] for p, o in g["out"].get(cid, []) if p in ("governs", "applies_to")]
        rows.append(f"[{cid}] {g['nodes'][cid]['label']}" + (f" -- {where[0]}" if where else ""))
    return "\n".join(rows)


def _alias_terms(source):
    g = graph(source)
    terms = {}
    for cid in g["conventions"]:
        al = {a.lower() for a in g["nodes"][cid]["aliases"]}
        for p, o in g["out"].get(cid, []):
            al.update(a.lower() for a in g["nodes"][o]["aliases"])
        terms[cid] = al
    df = {}
    for al in terms.values():
        for a in al:
            df[a] = df.get(a, 0) + 1
    n = len(terms)
    return terms, {a: math.log(1 + n / c) for a, c in df.items()}


def score(text, source="handbook"):
    terms, idf = _alias_terms(source)
    low = text.lower()
    out = []
    for cid, al in terms.items():
        s = 0.0
        for a in al:
            k = len(re.findall(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", low))
            if k:
                s += idf[a] * (1 + math.log(k))
        out.append((s, cid))
    out.sort(key=lambda x: (-x[0], x[1]))
    return out


def retrieve(text, k=3, source="handbook", exclude=("H01",)):
    return [cid for s, cid in score(text, source) if cid not in exclude and s > 0][:k]


def knowledge_block(text, k=3, source="handbook"):
    ids = retrieve(text, k, source)
    body = "\n\n".join(render_convention(c, source) for c in ids)
    return ids, body


def query(q, source="handbook", k=2):
    """Tool: `know` -- a convention id (e.g. H07) or free-text query."""
    g = graph(source)
    q = q.strip()
    ids = [c for c in re.findall(r"\b[HP]\d\d\b", q) if c in g["nodes"]]
    if not ids:
        ids = retrieve(q, k, source, exclude=())
    if not ids:
        return "no matching convention"
    return "\n\n".join(render_convention(c, source) for c in ids)
