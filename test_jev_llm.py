"""Offline self-check: python test_jev_llm.py"""
from jev_llm import render, Generator, PUNCT, OTHER, GROUP

assert render(["i", "am", "a", "assistant", ".", "an", "dog", "?", "yes", "\n", "ok"]) == "I am an assistant. A dog? Yes\nOk"
assert render([]) == ""

groups = [["the", "cat", "sat"], ["on", "mat", "dog"]]
g = Generator(groups, jev=object())
ans = {"mg0": {"probabilities": {"the": 0.5, "cat": 0.3, "sat": 0.1, ".": 0.1, OTHER: 0.0}},
       "mg1": {"probabilities": {"on": 0.4, "mat": 0.2, "dog": 0.1, ".": 0.3, OTHER: 0.0}}}
pool = g.pool(ans, "m", ["the", "cat", "sat", "the", "cat"])
keys = [k for k, _ in pool]
assert "cat" not in keys and "sat" not in keys, "immediate repeat and repeated trigram are blocked"
assert pool[0] == ("the", 0.5)
assert "." in keys and g.pool(ans, "m", ["the", "."])[0][0] not in PUNCT, "no doubled punctuation"
assert len(g.fanout_questions("Hi", "m")) == 2
assert "END" not in g.rerank_questions(["hi"], [("there", 0.5)])["r"]["criteria"]
assert "END" in g.rerank_questions(["hi", "."], [("there", 0.5)])["r"]["criteria"]
assert [k for k, p in pool if p >= g.spec_min][:2] == ["the", "on"], "speculation gate keeps only rated candidates"
assert GROUP + len(PUNCT) + 1 == 255
print("ok")
