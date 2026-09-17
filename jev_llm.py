"""Jev as an autoregressive language model, ~1 round trip per word.

Each word is produced in two stages that Jev's parallel question batching and
its indifference to concurrent requests let us overlap:

  stage 1  fan-out   G independent Choice questions, each over a disjoint
                     slice of the vocabulary (+ punctuation + OTHER), sent as
                     several small concurrent HTTP requests (~0.9 s wall for
                     any G).  Cheap, wide, noisy.  Gives a candidate pool.
  stage 2  rerank    one Choice over the pool, each option shown as the full
                     reply so far with the candidate appended.  Sharp and
                     grammatical; this is the distribution we decode from.

Speculation: the round that reranks word t also fans out word t+1 for the top
S stage-1 candidates of word t.  If the reranker picks one of them the next
round is again rerank + speculation, so a hit costs one round trip (~0.9 s)
per word and a miss costs two.  Beam search (B beams) rides on the same
rounds: every beam's rerank and speculative fan-outs go in the same batch.
"""
import json, math, os, random, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

API = "https://api.typesafe.ai/v1/systemone"
HERE = os.path.dirname(os.path.abspath(__file__))
PUNCT = {  # text -> description used in stage 1
    ".": "a full stop ending the sentence",
    ",": "a comma",
    "?": "a question mark",
    "!": "an exclamation mark",
    ":": "a colon",
    "\n": "a line break starting a new paragraph or list line",
}
OTHER = "(not listed)"
GROUP = 255 - len(PUNCT) - 1  # words per stage-1 question; + punctuation + OTHER = Jev's 255 cap
SENTENCE_END = (".", "?", "!", "\n")
CHUNK = 2  # stage-1 questions per HTTP request; ~0.8 s each, and they run concurrently


def api_key():
    k = os.environ.get("TYPESAFE_API_KEY")
    if not k and os.path.exists(os.path.join(HERE, ".env")):
        for line in open(os.path.join(HERE, ".env")):
            if line.startswith("TYPESAFE_API_KEY="):
                k = line.split("=", 1)[1].strip()
    if not k:
        sys.exit("set TYPESAFE_API_KEY (or put it in .env)")
    return k


def load_vocab(n_groups, path=os.path.join(HERE, "words.txt")):
    words = []
    for line in open(path, encoding="utf8"):
        w = line.split()[0]
        if re.fullmatch(r"[a-z][a-z']*", w) and w not in PUNCT:
            words.append(w)
    top = words[: n_groups * GROUP]
    # ponytail: round-robin split so every group has the same frequency profile;
    # Jev's OTHER is overconfident, and symmetric groups make that bias cancel.
    return [top[i::n_groups] for i in range(n_groups)]


class Jev:
    def __init__(self, key=None, retries=4, workers=32):
        self.key, self.retries = key or api_key(), retries
        self.pool = ThreadPoolExecutor(workers)
        self.calls = self.rounds = self.input_tokens = self.output_tokens = 0
        self.seconds = 0.0

    def one(self, state, questions):
        body = json.dumps({"model": "jev-latest", "state": state, "questions": questions}).encode()
        req = urllib.request.Request(API, body, {"Authorization": "Bearer " + self.key, "Content-Type": "application/json"})
        for attempt in range(self.retries + 1):
            try:
                r = json.load(urllib.request.urlopen(req, timeout=120))
                break
            except urllib.error.HTTPError as e:
                if e.code not in (429, 500, 502, 503, 529) or attempt == self.retries:
                    raise RuntimeError(f"Jev HTTP {e.code}: {e.read()[:300].decode(errors='replace')}")
                time.sleep(2**attempt)
        self.calls += 1
        self.input_tokens += r["usage"]["input_tokens"]
        self.output_tokens += r["usage"]["output_tokens"]
        return r["answers"]

    def __call__(self, state, questions):
        """One logical call: split into concurrent HTTP requests, merge the answers."""
        items = list(questions.items())
        chunks = [dict(items[i:i + CHUNK]) for i in range(0, len(items), CHUNK)]
        t = time.time()
        answers = {}
        for a in self.pool.map(lambda c: self.one(state, c), chunks):
            answers.update(a)
        self.seconds += time.time() - t
        self.rounds += 1
        return answers


def render(tokens):
    """Join word/punct tokens into text with sane spacing and capitalisation."""
    out = ""
    for i, tok in enumerate(tokens):
        if tok in PUNCT:
            out += tok
            continue
        if tok in ("i", "i'm", "i've", "i'll", "i'd"):
            tok = "I" + tok[1:]
        if tok in ("a", "an") and i + 1 < len(tokens):  # ponytail: a/an fixed by rule, not by Jev
            tok = "an" if tokens[i + 1][:1].lower() in "aeiou" else "a"
        if not out or out[-1] == "\n" or out.rstrip()[-1:] in ".?!":
            tok = tok[0].upper() + tok[1:]
        if out and out[-1] != "\n":
            out += " "
        out += tok
    return out


class Generator:
    def __init__(self, groups=16, spec=2, beams=1, pool=32, temperature=0.0, core=400, topic=600, spec_min=0.4, jev=None):
        self.base_groups = load_vocab(groups) if isinstance(groups, int) else groups
        self.groups = self.base_groups
        self.spec, self.beams, self.pool_size, self.temperature = spec, beams, pool, temperature
        self.spec_min = spec_min
        self.core, self.topic = core, topic
        self.jev = jev or Jev()

    # ---- vocabulary ------------------------------------------------------
    def select_vocab(self, state, ctx):
        """One wide call per reply: which of all ~4000 words belong in this answer?

        The active vocabulary is the most frequent `core` words (function words), words from the
        conversation, and the `topic` words Jev rates most likely.  Per-word fan-outs then cover
        ~700 words in 3 groups instead of 4000 in 16, which is where 80% of the tokens went.
        """
        inst = ("user_message is what the user asked. Which of these words is most likely to appear in a "
                "helpful, correct, concise reply?")
        qs = {f"tg{g}": {"type": "choice", "instructions": inst, "criteria": {w: None for w in ws}}
              for g, ws in enumerate(self.base_groups)}
        ans = self.jev(state, qs)
        rated = sorted(((p, w) for q in ans.values() for w, p in q["probabilities"].items()), reverse=True)
        core = [w for g in zip(*self.base_groups) for w in g][: self.core]  # round-robin groups -> frequency order
        return self.regroup(core + ctx + [w for _, w in rated[: self.topic]])

    def regroup(self, words):
        words = list(dict.fromkeys(words))
        n = max(1, -(-len(words) // GROUP))
        return [words[i::n] for i in range(n)]

    # ---- stage 1 ---------------------------------------------------------
    def fanout_questions(self, so_far, tag, groups=None):
        head = f"reply_so_far = {json.dumps(so_far)}. " if so_far else "The reply is empty so far. "
        inst = head + ("Select what comes NEXT in the assistant's helpful, concise, correct reply to user_message: "
                       "the next word (a space is inserted before it) or a punctuation mark attached to the last "
                       "word. Pick (not listed) if the next word is a word not listed.")
        return {f"{tag}g{g}": {"type": "choice", "instructions": inst,  # null description = 40% fewer tokens than ""
                               "criteria": {**{w: None for w in ws}, **PUNCT, OTHER: "the next word is a word not listed"}}
                for g, ws in enumerate(groups or self.groups)}

    def pool(self, ans, tag, toks, groups=None):
        """Candidate pool from stage-1 answers: top words per group + punctuation, repetition-blocked."""
        groups = groups or self.groups
        scored = {}
        for g in range(len(groups)):
            probs = ans[f"{tag}g{g}"]["probabilities"]
            words = sorted(((p, k) for k, p in probs.items() if k not in PUNCT and k != OTHER), reverse=True)[:4]
            for p, k in words:
                scored[k] = p
            for k in PUNCT:
                scored[k] = scored.get(k, 0) + probs.get(k, 0) / len(groups)
        grams = {tuple(toks[i:i + 3]) for i in range(len(toks) - 2)}
        out = []
        for k, p in sorted(scored.items(), key=lambda kv: -kv[1]):
            if k in PUNCT and (not toks or toks[-1] in PUNCT):
                continue  # no leading or doubled punctuation
            # ponytail: repetition block, the standard LM decoding trick
            if toks and k == toks[-1] or tuple(toks[-2:] + [k]) in grams:
                continue
            out.append((k, p))
        return out[: self.pool_size]

    # ---- stage 2 ---------------------------------------------------------
    def rerank_questions(self, toks, pool, tag="r"):
        crit = {f"c{i}": json.dumps(render(toks + [k])) for i, (k, _) in enumerate(pool)}
        if toks and toks[-1] in SENTENCE_END:  # ponytail: END only after sentence-final punctuation
            crit["END"] = "Stop here; the reply is already complete."
        return {tag: {"type": "choice", "instructions":
                "Each option is the assistant's reply so far with one more word or punctuation mark appended. "
                "Which option is the best continuation: grammatical, natural, factually correct and helpful for "
                "user_message? Choose END only if the reply already answers user_message fully.",
                "criteria": crit}}

    def generate(self, user_message, conversation=(), max_words=80, on_token=None):
        jev, state = self.jev, {"conversation": list(conversation), "user_message": user_message}
        # ponytail: words from the conversation join the vocabulary as an extra group, casing kept,
        # so names and topic words ("boil", "Paris") are available even if rare in general English.
        ctx = re.findall(r"[A-Za-z][A-Za-z']*", user_message + " " + " ".join(m["content"] for m in conversation))
        self.groups, self.widened = self.select_vocab(state, ctx), set()
        beams, done, hits, widened = [([], 0.0)], [], 0, 0  # (tokens, logprob); done = ended with END
        spec = {}  # rendered prefix -> (tag, stage-1 answers), filled speculatively
        while beams and len(beams[0][0]) < max_words:
            # stage 1 for beams whose fan-out was not speculated
            need = [(b, toks) for b, (toks, _) in enumerate(beams) if render(toks) not in spec]
            if need:
                ans = jev(state, {k: q for b, toks in need for k, q in self.fanout_questions(render(toks), f"m{b}").items()})
                spec.update({render(toks): (f"m{b}", ans) for b, toks in need})
            hits += len(beams) - len(need)
            pools = [self.pool(*spec[render(toks)][::-1], toks) for toks, _ in beams]
            # ponytail: confidence-gated widening.  If the active vocabulary has no candidate the
            # stage-1 groups like (all say "not listed"), do one wide fan-out over all 4000 words
            # for the top beam and fold its best words into the active vocabulary.
            toks0 = beams[0][0]
            s1 = spec[render(toks0)]
            if toks0 and all(s1[1][f"{s1[0]}g{g}"]["choice"] == OTHER for g in range(len(self.groups))) and render(toks0) not in self.widened:
                self.widened.add(render(toks0))
                widened += 1
                wide = jev(state, self.fanout_questions(render(toks0), "w", self.base_groups))
                self.groups = self.regroup([w for ws in self.groups for w in ws] + [k for k, _ in self.pool(wide, "w", toks0, self.base_groups)[:16]])
                spec = {}
                continue
            # stage 2 for every beam + speculative stage 1 for its top S children, one round trip
            qs = {}
            # ponytail: speculate only on stage-1 candidates Jev actually rates (p >= spec_min);
            # blind top-S speculation was ~50% wasted tokens.
            specs = [[k for k, p in pools[b] if p >= self.spec_min][: self.spec] for b in range(len(beams))]
            for b, (toks, _) in enumerate(beams):
                qs.update(self.rerank_questions(toks, pools[b], f"r{b}"))
                for i, k in enumerate(specs[b]):
                    qs.update(self.fanout_questions(render(toks + [k]), f"s{b}_{i}"))
            ans = jev(state, qs)
            spec, cands = {}, []
            for b, (toks, lp) in enumerate(beams):
                probs = ans[f"r{b}"]["probabilities"]
                for i, (k, _) in enumerate(pools[b]):
                    cands.append((lp + math.log(max(probs[f"c{i}"], 1e-9)), toks + [k]))
                for i, k in enumerate(specs[b]):
                    spec[render(toks + [k])] = (f"s{b}_{i}", ans)
                if "END" in probs:
                    cands.append((lp + math.log(max(probs["END"], 1e-9)), toks + [None]))
            if self.temperature > 0:  # Gumbel-top-k = sampling without replacement at this temperature
                cands = [(s / self.temperature - math.log(-math.log(random.random())), t) for s, t in cands]
            cands.sort(key=lambda c: -c[0])
            beams = []
            for score, toks in cands[: self.beams]:
                (done if toks[-1] is None else beams).append((toks[:-1] if toks[-1] is None else toks, score))
            if on_token:
                on_token(render(max(beams + done, key=lambda c: c[1])[0]))
            if done and (not beams or max(done, key=lambda c: c[1])[1] >= beams[0][1]):
                break
        toks, logp = max(done + beams, key=lambda c: c[1])
        return render(toks), {"rounds": jev.rounds, "requests": jev.calls, "seconds": round(jev.seconds, 1),
                              "words": len(toks), "spec_hits": hits, "widened": widened, "vocab": sum(map(len, self.groups)),
                              "input_tokens": jev.input_tokens, "logprob": round(logp, 2), "finished": (toks, logp) in done}


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Chat with Jev-as-an-LLM")
    ap.add_argument("prompt", nargs="*", help="one-shot prompt; omit for interactive chat")
    ap.add_argument("--groups", type=int, default=16, help="vocabulary groups of %d words" % GROUP)
    ap.add_argument("--spec", type=int, default=2, help="speculative fan-outs per beam per round")
    ap.add_argument("--beams", type=int, default=1)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-words", type=int, default=80)
    a = ap.parse_args()
    convo, shown = [], [""]

    def stream(text):  # ponytail: with beams the best text can change; reprint the line then
        if text.startswith(shown[0]):
            print(text[len(shown[0]):], end="", flush=True)
        else:
            print("\r\x1b[K" + text, end="", flush=True)
        shown[0] = text

    def turn(msg):
        shown[0] = ""
        gen = Generator(a.groups, a.spec, a.beams, temperature=a.temperature)
        reply, stats = gen.generate(msg, convo, a.max_words, on_token=stream)
        stream(reply)
        print()
        print(stats, file=sys.stderr)
        convo.extend([{"role": "user", "content": msg}, {"role": "assistant", "content": reply}])

    if a.prompt:
        turn(" ".join(a.prompt))
        return
    while True:
        try:
            msg = input("\nyou> ").strip()
        except EOFError:
            break
        if msg:
            turn(msg)


if __name__ == "__main__":
    main()
