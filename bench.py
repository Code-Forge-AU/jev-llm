"""Run a few prompts through a decoder config and append results to results.md.

    python bench.py GROUPS SPEC BEAMS [key=value ...]     e.g. python bench.py 16 2 1 spec_min=0.4
"""
import sys
from jev_llm import Generator

PROMPTS = ["Tell me about dogs.", "How do I boil an egg?", "Who are you?", "What is the capital of France?"]

if __name__ == "__main__":
    groups, spec, beams = (int(x) for x in sys.argv[1:4])
    kw = {k: float(v) if "." in v else int(v) for k, v in (a.split("=") for a in sys.argv[4:])}
    label = f"g={groups} s={spec} b={beams} " + " ".join(f"{k}={v}" for k, v in kw.items())
    rows = []
    for p in PROMPTS:
        reply, st = Generator(groups, spec, beams, **kw).generate(p, max_words=50)
        w = max(1, st["words"])
        rows.append(f"| {label} | {p} | {st['rounds']} | {st['rounds']/w:.2f} | {st['seconds']/w:.2f} | "
                    f"{st['spec_hits']}/{st['words']} | {st.get('widened', '-')}/{st.get('phrases', '-')} |{st['input_tokens']/1000:.0f}k | "
                    f"{st['input_tokens']/w/1000:.1f}k | {reply.replace(chr(10), ' / ')} |")
        print(rows[-1], flush=True)
    with open("results.md", "a", encoding="utf8") as f:
        f.write("\n".join(rows) + "\n")
