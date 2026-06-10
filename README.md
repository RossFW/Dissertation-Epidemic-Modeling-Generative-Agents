# Epidemic Modeling with Generative Agents

PhD dissertation by **Ross Williams** (Industrial & Systems Engineering, Virginia Tech).
*Methodology, Prompt Sensitivity, and LLM Sensitivity.*

A three-paper dissertation on using large-language-model–driven generative
agents to simulate human behavior in epidemics — assembled here as a single
HTML document with unifying framing and a synthesis chapter.

> **In progress.** This is a working draft, compiled from the three constituent
> papers below plus new framing (Chapter 1) and synthesis (Chapter 5).

## Read it

Open `viz/dissertation.html` in a browser, or serve locally:

```bash
cd viz && python3 -m http.server 8000
# then open http://localhost:8000/dissertation.html
```

## Structure

| Chapter | Source paper | Repo |
|---|---|---|
| 1 — Introduction / framing | new | — |
| 2 — Epidemic GABM (methodology) | Paper 1 (arXiv:2307.04986) | [Paper 1](https://github.com/RossFW/Paper1-Epidemic-Generative-Agent-Based-Model) · [bear96 (orig. code)](https://github.com/bear96/GABM-Epidemic) |
| 3 — Prompt sensitivity | Paper 2 (VT prelim) | [Paper 2](https://github.com/RossFW/Paper2-Prompt-Sensitivity-of-Generative-Agents) |
| 4 — LLM sensitivity | Paper 3 | [GABM-Mobility-Curve](https://github.com/RossFW/GABM-Mobility-Curve) · [live site](https://rossfw.github.io/GABM-Mobility-Curve/) |
| 5 — Conclusion / synthesis | new | — |

## Layout

```
viz/
  dissertation.html        The compiled dissertation
  figures/{ch2,ch3,ch4}/   Static figure exports (109 files)
  *-worked-example*.html   Supplementary statistical walkthroughs
```
