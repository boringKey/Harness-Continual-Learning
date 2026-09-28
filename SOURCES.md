# Scientific sources and presentation boundaries — v9

## Source manuscript

All scientific content is based on the 20-page author-supplied manuscript:

`Harness_Continual_Learning__Continual_Adaptation_Beyond_Model_Parameters.pdf`

The unchanged file is distributed as `static/paper/HCL.pdf`. SHA-256:

`981d91543ed59fc13879bf9837e6278e8afdcea5d5af9bc8414232ea81fa4eb9`

The public arXiv identifier remains `2608.19013`. The website does not infer a new arXiv version, acceptance, publication date, or venue. Its revised results are not labeled as arXiv v1.

## Content map

| Website content | Source in supplied manuscript |
|---|---|
| Title, author order, affiliations | Page 1 |
| HCL definition; forgetting despite frozen parameters | Introduction and Figure 1, pages 1–3 |
| Original Figure 1: shift in learning object | Original Figure 1, page 2 |
| Four jointly versioned components | Section 3.2, pages 4–5 |
| Original Figure 2 | Page 4 |
| Candidate, evaluator, and deployment | Section 3.3, pages 5–6; Equation (10) |
| Shared acquisition–retention objective and CL relationships | Section 3.4, page 6 |
| ALFWorld selected outcomes | Table 1, page 7 |
| Minecraft tasks and actions | Figure 3 / Section 4.1, page 7 |
| Main textual and multimodal selected outcomes | Table 2, page 8 |
| Evaluation scales and settings | Appendix C.1–C.2, pages 16–17 |

The model-state / harness-state comparison now uses the manuscript's original Figure 1, not an independently generated diagram. The accompanying prose summarizes Sections 3.1–3.4. Links to traditional CL are conceptual/function-level relationships, not one-to-one algorithm implementations.

The headline “The harness becomes the continual learning state.” is project-page wording based on Sections 3.1–3.2, not a verbatim quotation. The main shared-goal statement summarizes Section 3.4.

## Starting-point comparisons added in v8

| Setting | Reported starting point | Selected HCL configuration | Website-computed absolute gain |
|---|---|---|---|
| ALFWorld | Static Harness 47.12% | Plasticity-HCL 62.98% | +15.86 percentage points |
| Minecraft | Static Harness 15/50 tasks | Plasticity-HCL 50/50 tasks | +35 tasks |
| Textual reasoning | DeepSeek-V4.1-Flash Zero-shot 63.65% | Plasticity-HCL 76.10% | +12.45 percentage points |
| Multimodal perception | Qwen3.6-27B Zero-shot 46.77 | Stability-HCL 68.92 | +22.15 score points |

Only Table 2 provides rows explicitly named Zero-shot. ALFWorld and Minecraft are not relabeled as zero-shot experiments: their reported non-adaptive comparator is Static Harness. Within each setting the comparison uses the same foundation model; the page does not present results as identical backbones across all four settings.

The original memory-based comparisons remain visible: ALFWorld **+2.30 pp vs MemRL 60.68%**; textual **+7.25 pp vs MemRL 68.85%**; multimodal **+3.76 pts vs MemP 65.16**. These are the highest final-score non-HCL rows in the respective tables, not selections by forgetting. Minecraft reports **83 HCL actions versus 88 for MemRL and 91 for MemP**. No missing task-completion counts or intermediate trajectories are inferred for those methods.

Gain annotations are arithmetic derived from source endpoints; they are not new experiments, relative percentages, confidence intervals, or statistical-significance claims. Stage-wise bars have an untruncated 0–100 scale. Minecraft task bars use 0–50. Different domain metrics are not directly comparable.

Selected configuration context remains visible: Plasticity-HCL forgetting is **10.94%** on ALFWorld and **0.40%** on textual reasoning; Stability-HCL forgetting is **0.22%** on multimodal perception. Higher final scores do not imply lower forgetting than all baselines. Minecraft reports task completion/actions rather than stage-wise forgetting.

The new `starting_point_comparisons` JSON entries are separate from the preserved `selected_comparisons` entries. The full CSV/JSON table transcriptions remain source archives; no complete table, result tabs, or expandable data layer is rendered on the homepage.

## Framework description and boundaries

The component description follows Section 3.2. The candidate-update guide follows main Section 3.3: the Optimizer proposes revisions; the Evaluator checks current improvement, historical regression budget, and task validity; only an admissible candidate is committed. If none qualifies, the deployed state remains unchanged.

This compact explanation does not assert perfect retention on all historical test cases. Appendix C.1 describes an interactive-environment caveat: LLM-based historical assessment replaces strict replay-based backtesting in ALFWorld/Minecraft. The page does not claim a re-execution audit of those environments. It also does not reconcile the main formulation with all artifact-level implementation details in Appendix B.2.

## Ambiguities retained from the manuscript

The ALFWorld prose on page 7 refers to 55.56 as the strongest non-HCL baseline, while Table 1 lists MemRL at 60.68. This website uses the numeric **Table 1 rows** for its charts and differences and does not repeat the conflicting prose ranking. This is an explicit source selection; the PDF itself remains unchanged.

The broad experiment introduction mentions Qwen-family interactive models, whereas the Minecraft-specific paragraph explicitly names `deepseek-v4-flash-0731`. The website follows that task-specific paragraph and records the choice here. It does not substitute a generic backbone from other experiments.

## Original figures

Figure 1 is a direct rendering and crop of page 2 at PDF coordinates `[107, 81, 505, 242]`, rendered at 8 pixels per PDF point. The full PNG is **3184 × 1288 pixels**. All figure content is preserved, without redraws or recoloring. The additional webpage state-equation display has been removed; the manuscript and its original figure formulas remain unchanged.

Figure 2 is a direct crop of page 4, at coordinates and resolution recorded in `static/data/figure-provenance.json`. No text, arrows, values, labels, or colors were redrawn. The full PNG is 3184 × 1848 pixels; responsive WebP variants are used for normal deployment. The portable preview embeds the PNG.

## Design references

Previous iterations referenced Nerfies (`https://nerfies.github.io/`), Voyager (`https://voyager.minedojo.org/`), OpenVLA (`https://openvla.github.io/`), and the Anthropic article (`https://www.anthropic.com/institute/recursive-self-improvement`) for page organization and restrained text/figure presentation.

They are not scientific sources for HCL. No external research conclusions, logos, figures, tracking scripts, source code, or font files from those websites are bundled. v9 preserves the established system typography and uses the original comparison figure. Four small, inline SVG interface pictograms identify the experimental domains; they are not official benchmark logos. No external icon pack is loaded.
