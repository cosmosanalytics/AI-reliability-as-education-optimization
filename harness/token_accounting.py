import os
import tiktoken

enc_cl100k = tiktoken.get_encoding("cl100k_base")
enc_o200k = tiktoken.get_encoding("o200k_base")

brief_dir = os.path.join(os.path.dirname(__file__), "..", "repo_push", "briefs")
briefs = ["B.md", "S1.md", "S2.md", "S4.md", "P2.md", "P3.md", "U2.md", "R2.md"]

print("| Brief | Description | Chars | Words | Tokens (cl100k) | Tokens (o200k) |")
print("|---|---|---|---|---|---|")

desc = {
    "B": "Full 16-Rule Book",
    "S1": "Bare Prompt (No Book)",
    "S2": "Short 5-Rule Book",
    "S4": "Student Study Notes",
    "P2": "Practice Notes",
    "P3": "Worked Examples (+Book)",
    "U2": "Test Runner (+Book)",
    "R2": "Self-Review Checklist (+Book)",
}

counts = {}
for b in briefs:
    p = os.path.join(brief_dir, b)
    with open(p, "r", encoding="utf-8") as f:
        txt = f.read()
    chars = len(txt)
    words = len(txt.split())
    tok_cl = len(enc_cl100k.encode(txt))
    tok_o = len(enc_o200k.encode(txt))
    name = b.replace(".md", "")
    counts[name] = {"chars": chars, "words": words, "cl100k": tok_cl, "o200k": tok_o}
    print(f"| {b} | {desc[name]} | {chars} | {words} | {tok_cl} | {tok_o} |")

print("\n### Exact Incremental Token Costs (cl100k_base)")
b_cl = counts["B"]["cl100k"]
s1_cl = counts["S1"]["cl100k"]
s2_cl = counts["S2"]["cl100k"]
s4_cl = counts["S4"]["cl100k"]
p2_cl = counts["P2"]["cl100k"]
p3_cl = counts["P3"]["cl100k"]
u2_cl = counts["U2"]["cl100k"]
r2_cl = counts["R2"]["cl100k"]

print(f"- **Bare Prompt ($S_1$):** {s1_cl} tokens")
print(f"- **Full Book ($B$ / $s_3$):** {b_cl} tokens (Incremental over $S_1$: +{b_cl - s1_cl} tokens)")
print(f"- **Short Book ($S_2$ / $s_2$):** {s2_cl} tokens (Incremental over $S_1$: +{s2_cl - s1_cl} tokens)")
print(f"- **Student Notes ($S_4$):** {s4_cl} tokens (Incremental over $S_1$: +{s4_cl - s1_cl} tokens)")
print(f"- **Practice Notes ($P_2$):** {p2_cl} tokens (Incremental over $B$: +{p2_cl - b_cl} tokens)")
print(f"- **Worked Examples ($P_3$):** {p3_cl} tokens (Incremental over $B$: +{p3_cl - b_cl} tokens)")
print(f"- **Interactive Test Runner Brief ($U_2$):** {u2_cl} tokens (Incremental over $B$: +{u2_cl - b_cl} tokens)")
print(f"- **Self-Review Checklist ($R_2$):** {r2_cl} tokens (Incremental over $B$: +{r2_cl - b_cl} tokens)")
