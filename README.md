# Ghost Town Radio

**Five towns now: Bodie (California, 1879 and 1880), Bangalore, Coorg, Hyderabad and Mumbai (Bombay).** A town selector sits under the title. The old-India towns come from public domain gazetteers and books on the Internet Archive, not newspapers, so each source is a book with a publication year, not a daily issue.

| Town | Sources | Claims on air | Silent hours |
|---|---|---|---|
| Bodie | 96 newspaper issues, 1879 to 1915 | 40 | 4 |
| Bangalore | Bangalore Gazetteer 1875, Rice's Mysore gazetteer 1897 (2 volumes) | 22 | 5 |
| Coorg | Richter's Manual of Coorg 1870, Gazetteer of Coorg, Rice's Mysore and Coorg 1876 | 23 | 4 |
| Hyderabad | Hyderabad Affairs 1889, Hyderabad under Salar Jung 1884, Imperial Gazetteer Hyderabad 1909, History of Freemasonry in Hyderabad 1910 | 17 | 10 |
| Mumbai | Gazetteer of Bombay City and Island, vols 1 and 3 (1909, 1910) | 18 | 9 |

Same rule everywhere: a claim goes on air only if its quote is found word for word in the source text by code. Numbers for the new towns are in the section "New towns: eval numbers" below. The Bodie text that follows is the original write up.

**Bodie, California, 1879 and 1880.** At its peak, thousands of people lived here, and the town had its own daily newspapers. Today it is a ghost town. This is a radio station that plays what those newspapers said. A fictional DJ, Hollis Vane, reads it out. If the archive says nothing about a subject, he says nothing. Four hours of the schedule are deliberately silent for that reason.

**Listen:** https://sivaratrisrinivas.github.io/ghost-town-radio/ (press play, or turn the knob to pick an hour)
**Demo video (five towns, 90 s):** https://sivaratrisrinivas.github.io/ghost-town-radio/demo/ghost-town-radio-demo-5towns.mp4 (original Bodie only cut, 71 s: `demo/ghost-town-radio-demo.mp4`)

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

## New towns: eval numbers
Pipeline: `TOWN=<slug>` selects the town (`data/towns.json`). `02b_fetch_town.py` fetches Internet Archive text, `03` picks passages that mention the town, `04` asks a free LLM for claim plus quote, `06` runs the same code checks, `07` builds the schedule, `08` renders audio, `09` re-checks the shipped data. `09` with no `TOWN` set checks all five towns, and that is what CI runs.
- **Licensing:** every source is dated 1930 or earlier, so it is public domain in the US by age. Only the 1875 Bangalore Gazetteer carries an explicit Public Domain Mark on the Internet Archive. The other items have no rights statement there, and the license line on each card says so. This is my age based reading, not a legal opinion.
- **Raw LLM quote exactly verbatim:** Bangalore 93.2% (n=117), Coorg 90.5% (n=137), Hyderabad 83.8% (n=142), Mumbai 88.1% (n=118). Models: Groq gpt-oss-120b for the first passages of Bangalore, Mumbai, Coorg and Hyderabad, then gpt-oss-20b once the 120b daily free quota ran out. The rates mix both models.
- **Passed all code checks:** Bangalore 70, Coorg 88, Hyderabad 56, Mumbai 60.
- **Final on-air claims with a verbatim quote, source id, archive URL, date and license:** 100% (22, 23, 17, 18). By construction, and re-checked by `09`, which also catches planted fake quotes.
- **Hand check (one reviewer, me, an AI agent):** 114 in-scope candidates read against their quotes, 96 supported (84.2%), 18 removed as unsupported (claim added a word or fact, quote was a question fragment or garbled). Details in `evals/hand_labels_new_towns.json`. There is no independent reviewer and no held-out split for these towns; the split is by passage and nothing was tuned on it.
- **Limits:** "Bangalore", "Coorg" and "Hyderabad" mean the town plus its district or state, as the gazetteers describe them. Mumbai uses only the city gazetteers. Books give publication years, not dates of events. Nightlife has no sources, so those hours are silent. Many facts are dry census and school numbers, because that is what gazetteers contain.
