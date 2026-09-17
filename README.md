# jev-llm

TypeSafe's Jev is a decision model: it takes state and typed questions and returns calibrated
probabilities over choices. It never generates text. This project turns it into an
autoregressive text generator anyway, one word per API round trip, using nothing but Jev
(no drafter model, no n-gram corpus; the only data file is a word-frequency list).

```
python jev_llm.py "How do I boil an egg?"
Here: how to boil an egg. You need: eggs. Then you put them in a pot of water and bring
to the boil. Then turn down heat. Then cook for about nine minutes.
```

## Setup

Python 3.10+, standard library only.

```bash
echo TYPESAFE_API_KEY=your-key > .env
python jev_llm.py                 # interactive chat
python jev_llm.py "Who are you?"  # one shot
python test_jev_llm.py            # offline self-check
python bench.py 16 2 1            # appends a benchmark block to results.md
```

Flags: `--beams N`, `--spec N` (speculative fan-outs per round), `--temperature T`, `--max-words N`.
`words.txt` is the English top-50k list from [hermitdave/FrequencyWords](https://github.com/hermitdave/FrequencyWords) (CC BY-SA 4.0).

## How it works

Jev caps a Choice at 255 options and its character-level distribution is nearly flat, so the
unit of generation is a word and the vocabulary has to be split across questions.

1. **Topic vocabulary, once per reply.** One wide call asks Jev, over ~4,000 common words in 16
   groups, which words belong in a good answer. The top 600 plus 400 function words plus the
   words in the prompt become the active vocabulary (~900 words, 4 groups).
2. **Stage 1, fan-out.** Each active group is a Choice: 248 words + punctuation + "(not listed)".
   The groups are sent as 2-question HTTP requests in parallel; Jev's latency is ~0.8 s per
   request no matter how many run at once, so any fan-out costs ~0.9 s wall.
3. **Stage 2, rerank.** The top candidates from every group, plus common two-word phrases and an
   END option, are shown as actual continuations of the reply ("...water to a boil"). Jev is
   sharp at judging text it can see, and this normalised distribution is what we decode from.
4. **Speculation.** The rerank round for word *t* also carries fan-outs for the candidates Jev
   rated well for word *t+1*. On a hit the next word costs one round trip; on a miss, two.
5. **Rules where Jev is weak:** a/an agreement, sentence capitalisation, "I", no doubled
   punctuation, trigram repetition block, END only after sentence-final punctuation.

## Numbers

Same four prompts, 50-word cap, greedy. Full rows in `results.md`.

| Version | s/word | rounds/word | input tokens/word |
|---|---|---|---|
| [kesku/jev-freeform](https://github.com/kesku/jev-freeform) (character level, its default search) | ~2.3 s per **character** | 60 calls for "Dogs are " | 14k per character |
| Two-stage rerank, full vocabulary every word | 1.5–1.9 | 1.6–1.8 | 45–65k |
| + topic vocabulary | 1.4–1.6 | 1.8–2.0 | 14–30k |
| + gated speculation, windowed rerank, phrases (current) | 1.2–1.4 | 1.5–1.8 | 12–14k |

At $0.042 per million input tokens a 30-word reply costs about a cent and takes about 40 s.
Short factual answers ("Paris.") are dominated by the fixed topic-selection call (~50k tokens).

## What was tried and dropped

- Character-level decoding: Jev cannot spell ("boa" outranks "boi").
- Separate punctuation question: a single "." option always beat a probability mass spread
  over thousands of words. Punctuation now lives inside every group.
- Beam search (`--beams 2`): twice the tokens, no visible quality gain. Still available.
- Skipping the rerank when stage 1 is confident: fired rarely and introduced errors ("Am an
  assistant", "a pot water"). Removed.
- A 4-token rerank window: word-order errors ("minutes ten"). 8 tokens holds.
- A 470-word active vocabulary: 5–10k tokens/word but it re-widened up to 5 times per reply.

## Known limits

- Endings are the weak spot: Jev rarely picks END and sometimes trails off into "Done. None."
- Vocabulary is ~4,000 lowercase words plus whatever is in the prompt; rare words are spelled
  only if they appear in the conversation. Proper nouns keep the casing they had in the prompt.
- Every question resends the conversation and reply prefix; there is no server-side caching.
