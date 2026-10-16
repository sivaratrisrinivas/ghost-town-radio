# Ghost Town Radio

**Bodie, California, 1879 and 1880.** At its peak, thousands of people lived here, and the town had its own daily newspapers. Today it is a ghost town. This is a radio station that plays what those newspapers said. A fictional DJ, Hollis Vane, reads it out. If the archive says nothing about a subject, he says nothing. Four hours of the schedule are deliberately silent for that reason.

**Listen:** https://sivaratrisrinivas.github.io/ghost-town-radio/ (press play, or turn the knob to pick an hour)
**Demo video (71 s):** https://sivaratrisrinivas.github.io/ghost-town-radio/demo/ghost-town-radio-demo.mp4

Every claim has a source link, the exact quote, and a license on a live card. The quote is shown exactly as the OCR has it, typos included. The DJ's voice is synthetic. The DJ is not a real person. The facts are not made up.

## How it works
1. **Corpus:** 96 public domain issues of the Bodie Chronicle, Bodie Morning News and Daily Bodie Standard (Internet Archive, California Revealed, Mammoth Museum). About 6M characters of OCR text, each with title, date, URL and license in `data/corpus_meta.json`.
2. **Facts:** a free LLM (Groq gpt-oss-120b, then Gemini 3.5 Flash Lite when Groq's daily quota ran out) reads passages and proposes `claim + exact quote`. All outputs are cached in `data/llm_cache`.
3. **Code checks** throw out anything unsafe (see numbers below). Quotes the LLM silently "fixed" are snapped back to the real source text.
4. **Script:** a 24 hour schedule is assembled by code from checked facts only. Between facts the DJ only says fixed lines with no digits and no names.
5. **Audio:** Kokoro (local, voice am_onyx) plus a synthesized wind and crackle bed. 4 MB total.

## Eval numbers
| Check | Result |
|---|---|
| LLM quote was word for word right away (dev, n=147) | 71.4% |
| Same, held-out docs (n=17, tiny) | 47.1% |
| Facts that passed all code checks (dev / held-out) | 46 of 147 / 2 of 17 |
| **Claims in the final broadcast with a verbatim quote** | **100% (40 of 40)** |
| Final claims with source ID, archive URL, date, license | 100% (40 of 40) |
| Hand check: claim supported by its quote (48 facts that passed code, one reviewer) | 46 of 48 (95.8%). The 2 failures were removed. |
| Hand check before the grounding check was added (31 facts) | 27 of 31 (87%). That is why the check exists. |

The 100% is by construction: a fact cannot enter the broadcast unless its quote is found in its source after collapsing whitespace. Case, punctuation and OCR errors are kept. `scripts/09_eval_broadcast.py` re-checks the shipped data and tests itself on planted fake quotes. 10 of 40 final quotes were snapped from an LLM version to the real span.
The held-out split is `sha256(doc id) mod 5 == 0` (13 of 83 usable docs). It was fixed before extraction, and the rules were tuned on dev only. The held-out run was done once.

## Honest limits
- **Library of Congress / Chronicling America was my first choice, but its API returned a Cloudflare challenge to my server.** I did not try to bypass it. The same Bodie papers are public domain on the Internet Archive, so I used those. No census or oral histories are in the corpus. Only newspapers.
- Only 40 facts survived, from 27 issues. OCR on microfilm is bad, and many LLM facts failed. Mining reports dominate, so nightlife, weather and most crime hours are silent.
- Faithfulness was hand checked by one reviewer (me), not an independent one. The check proves the claim fits the quote, not that the 1879 newspaper was right.
- The held-out sample is too small to say much. No LLM judge was used, so there is nothing to validate there.
- The spoken quote removes line break hyphens (`assess- ment` is read as assessment). The card shows the exact text.
- Error analysis was automated, not an interactive human review session. Failure modes found: LLM cleans OCR (29%), claim adds names or numbers not in the quote, garbled OCR, ellipsis-joined spans.

## Novelty check
I found related work but nothing that does this exact thing. I cannot prove nothing exists.
- [Backcast](https://github.com/David-Gesl/Backcast): 24/7 AI retro radio telling "this day in history". No per-claim sources.
- [Chronoscapes](https://github.com/sharmilaraghu/Chronoscapes): turns historical newspaper passages into era music and a radio host, with a "Chrono Radio" mode. Closest in spirit. Generative music, not verbatim quote checks.
- [old-time-radio](https://github.com/codebox/old-time-radio): streams real archive radio shows.
- Fairbury Echoes (42 local history radio segments) and the Archives of Michigan Podunk interview are human made audio histories.
- Quote-verification is the part I could not find elsewhere in this form.

## Run it
`pip install requests rapidfuzz kokoro-onnx soundfile`, then run `scripts/01` to `09` in order. Needs `GROQ_API_KEY`. Pages serves `docs/`. Code is MIT. The corpus text is public domain.
