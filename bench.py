"""Run a few prompts through several decoder configs and append results to results.md."""
import sys, time
from jev_llm import Generator

PROMPTS = ["Tell me about dogs.", "How do I boil an egg?", "Who are you?", "What is the capital of France?"]

if __name__ == "__main__":
    groups, spec, beams = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    rows = []
    for p in PROMPTS:
        reply, st = Generator(groups, spec, beams).generate(p, max_words=50)
        rows.append(f"| g={groups} s={spec} b={beams} | {p} | {st["rounds"]} | {st["rounds"]/max(1,st["words"]):.2f} | "
                    f"{st['seconds']/max(1,st['words']):.2f} | {st['spec_hits']}/{st['words']} | {st['input_tokens']/1000:.0f}k | "
                    f"{reply.replace(chr(10), ' / ')} |")
        print(rows[-1], flush=True)
    with open("results.md", "a", encoding="utf8") as f:
        f.write("\n".join(rows) + "\n")
