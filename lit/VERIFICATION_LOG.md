# Verification Log — cl4fm-selfevolve-forgetting

All entries live-verified on 2026-09-07.
Verification sources: arXiv abstract page (WebFetch), Semantic Scholar API, Crossref API, Google Scholar (WebSearch).

| bibkey | title (short) | venue / year | verified via | notes |
|--------|---------------|-------------|--------------|-------|
| wang2023voyager | Voyager | TMLR 2023 | S2 arXiv:2305.16291, confirmed authors 8 | Authors: Wang, Xie, Jiang, Mandlekar, Xiao, Zhu, Fan, Anandkumar |
| shinn2023reflexion | Reflexion | NeurIPS 2023 | arXiv:2303.11366 `citation_author` meta (re-verified 2026-09-07) | **Authors: Shinn, Cassano, Berman, Gopinath, Narasimhan, Yao (6).** Corrected 2026-09-07: this row previously read "Labash", which is the arXiv **v1** author list, superseded by the published 6-author version. DOI 10.52202/075280-0377 is deliberately NOT carried in `refs.bib`: the Crossref proceedings record omits Berman, so verifying against it would force dropping a real author to pass gate 11b. arXiv is authoritative here. Gate 11/11b re-run 2026-09-07: OK, n_authors=6, 0 MISMATCH. |
| zhao2023expel | ExpeL | AAAI 2024 | WebFetch arxiv.org/abs/2308.10144 | Authors: Andrew Zhao, Daniel Huang, Quentin Xu, Matthieu Lin, Yong-Jin Liu, Gao Huang |
| madaan2023selfrefine | Self-Refine | NeurIPS 2023 | WebSearch → S2 record confirmed arXiv:2303.17651 | 16 authors confirmed from S2 paper page |
| zelikman2022star | STaR | NeurIPS 2022 | arXiv page 2203.14465 | Authors: Zelikman, Wu, Mu, Goodman |
| gulcehre2023rest | ReST | preprint 2023 | WebSearch PDF 2308.08998 | 14 authors confirmed from paper |
| yuan2024selfrewarding | Self-Rewarding LMs | preprint 2024 | WebSearch arXiv:2401.10020 | 7 authors (v3 includes Xian Li) |
| chen2024spin | SPIN | preprint 2024 | WebSearch arXiv:2401.01335 | 5 authors confirmed |
| wu2024selfimpreversal | Progress or Regress? | preprint 2024 | WebFetch arxiv.org/abs/2407.05013 | Authors: Ting Wu, Xuefeng Li, Pengfei Liu |
| zhang2025darwin | Darwin Gödel Machine | preprint 2025 | WebSearch + S2 arXiv:2505.22954 | Authors: Jenny Zhang, Shengran Hu, Cong Lu, Robert Lange, Jeff Clune |
| yin2024godelagent | Gödel Agent | preprint 2024 | WebSearch arXiv:2410.04444 | Authors: Yin, Wang, Pan, Lin, Wan, W.Y. Wang |
| novikov2025alphaevolve | AlphaEvolve | preprint 2025 | S2 record + WebSearch arXiv:2506.13131 | 18 authors confirmed from S2 |
| lin2026selfregress | Self-Improvement Can Self-Regress | preprint 2026 | WebSearch arXiv:2606.21090 | CAUTION: task desc said "Cheng et al. 2025"; live-verified author is Jianzhe Lin (single), June 2026. Closest match to described paper. |
| schmidhuber2007godel | Gödel Machine | Springer 2007 | WebSearch DOI 10.1007/978-3-540-68677-4_7 + arXiv cs/0309048 | Book chapter in "Artificial General Intelligence" |
| yang2026selfimprovement | Self-Improvement of LLMs | TMLR 2026 | WebFetch arxiv.org/abs/2603.25681 | 7 authors, accepted at TMLR with Survey Certification |
| gao2025selfevolving | Self-Evolving Agents Survey | preprint 2025 | WebFetch arxiv.org/abs/2507.21046 + WebSearch | 27 authors confirmed |
| sun2025solververifier | Solver-Verifier Gap | preprint 2025 | WebFetch arxiv.org/abs/2507.00075 | 5 authors confirmed |
| mccloskey1989catastrophic | Catastrophic Interference | Psych. Learn. Motiv. 1989 | S2 + Crossref DOI 10.1016/S0079-7421(08)60536-8 | Book chapter, confirmed title/author/vol/pages |
| french1999catastrophic | Catastrophic forgetting | Trends Cogn. Sci. 1999 | S2 + WebSearch DOI 10.1016/S1364-6613(99)01294-2 | Single author |
| kirkpatrick2017ewc | EWC | PNAS 2017 | WebSearch + arXiv:1612.00796 + DOI 10.1073/pnas.1611835114 | 14 authors confirmed |
| lopezpaz2017gem | GEM | NeurIPS 2017 | WebSearch arXiv:1706.08840 | 2 authors confirmed |
| rebuffi2017icarl | iCaRL | CVPR 2017 | WebSearch arXiv:1611.07725 | 4 authors confirmed |
| rolnick2019experience | Experience Replay | NeurIPS 2019 | WebSearch arXiv:1811.11682 | Authors: Rolnick, Ahuja, Schwarz, Lillicrap, Wayne |
| chaudhry2019tiny | Tiny Episodic Memories | preprint 2019 | WebSearch arXiv:1902.10486 | 7 authors confirmed |
| diazrodriguez2018dont | Don't Forget... | NeurIPS CL Workshop 2018 | WebSearch arXiv:1810.13166 | 4 authors confirmed |
| wu2024cl4llms | CL for LLMs survey | preprint 2024 | WebSearch arXiv:2402.01364 | 6 authors confirmed |
| shi2024cl4llms | CL of LLMs comprehensive | preprint 2024 | WebSearch arXiv:2404.16789 | 9 authors confirmed |
| li2026jitrl | Just-In-Time RL | preprint 2026 | WebSearch + WebFetch arXiv:2601.18510 | 8 authors confirmed |
| ding2026memory | Controlled Memory Interference | preprint 2026 | WebSearch arXiv:2608.07622 | 7 authors confirmed |
| cobbe2021gsm8k | GSM8K | preprint 2021 | WebSearch arXiv:2110.14168 (PDF visible) | 12 authors confirmed |
| mirzadeh2024gsmsymbolic | GSM-Symbolic | preprint 2024 | WebSearch arXiv:2410.05229 | 6 authors confirmed (Apple) |
| hendrycks2021math | MATH dataset | NeurIPS 2021 | WebSearch arXiv:2103.03874 | 8 authors confirmed |
| lightman2023verify | Let's Verify Step by Step | preprint 2023 | WebSearch arXiv:2305.20050 (PDF confirms) | 10 authors confirmed (OpenAI) |
| clark2018arc | ARC Challenge | preprint 2018 | WebSearch arXiv:1803.05457 | 7 authors confirmed (AI2) |
| suzgun2022bbh | BIG-Bench Hard | preprint 2022 | WebFetch arxiv.org/abs/2210.09261 | 11 authors confirmed |
| chen2021humaneval | HumanEval | preprint 2021 | WebFetch arxiv.org/abs/2107.03374 | 58 authors confirmed (OpenAI) |
| hendrycks2020mmlu | MMLU | ICLR 2021 | WebFetch arxiv.org/abs/2009.03300 | 7 authors confirmed |
| zheng2023mtbench | MT-Bench / LLM-as-judge | NeurIPS 2023 | WebSearch arXiv:2306.05685 | 13 authors confirmed |
| wang2023llmfair | LLMs Not Fair Evaluators | preprint 2023 | WebSearch arXiv:2305.17926 | 10 authors confirmed |
| wahi2026proctor | LLM-as-Judge Not an Oracle | preprint 2026 | WebFetch arxiv.org/abs/2609.02246 | Single author confirmed, Sep 2026 |
| talmor2019commonsenseqa | CommonsenseQA | NAACL-HLT 2019 | arXiv API id_list=1811.00937 + Crossref DOI 10.18653/v1/N19-1421 | 4 authors confirmed (Talmor, Herzig, Lourie, Berant). Added 2026-09-07: family C was used as a dataset but uncited; now cited in §Setup. Gate 11 resolves the DOI OK. |

## Dropped Candidates

| title / candidate | reason dropped |
|-------------------|----------------|
| "Cheng et al. 2025, Self-Improvement Can Self-Regress" | Task description metadata unverified: live search found only arXiv:2606.21090 (Jianzhe Lin, June 2026). No "Cheng et al. 2025" paper with this title found. Included closest verified match (lin2026selfregress). |
| "Continual Self-Improvement with Lightweight Experiential Latent Memories" (2606.17803) | Could not confirm full author list within session; dropped in favor of ding2026memory which covers same theme |
| "Rethinking Continual Experience Internalization" (2606.04703) | Only partial author list obtained ("Jingwen Chen and 9 others"); dropped per anti-fabrication rule |
| "LLM-as-a-Judge Not an Oracle" second candidate | Merged into single wahi2026proctor entry |
| On the Measure of Intelligence (Chollet 2019 / ARC) | Different from ARC-Challenge; not used in experiments |

## Corrections to this log

| date | what | why |
|------|------|-----|
| 2026-09-07 | `shinn2023reflexion` main-table row corrected from "Labash" to the 6-author list including Berman | The row carried the arXiv **v1** author list. A later append at the bottom of this file recorded the correct list but left the original row standing, so the log contradicted itself — and a provenance log that contradicts itself is worse than none. One row, one truth. |
| 2026-09-07 | `talmor2019commonsenseqa` and `shinn2023reflexion` moved out of "Dropped Candidates" into the verified table | Both are cited in the manuscript; neither was dropped. They had been appended to the wrong table. |
