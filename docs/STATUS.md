# Project Status

**Date Updated:** April 11, 2026

## 🚦 Phase 5: Live Execution & Testing Loop (HITL)

We are iterating through the pipeline physically evaluating each node. 
* **Methodology:** User drives execution via browser clicks `->` Agent validates file outputs via SSH.

| Stage | Module Name | Status |
|:---:|---|---|
| ✅ | Infrastructure / Pod Setup | **Stable**. `init_pod.py` successfully provisions the server. |
| ✅ | **Module 0** (Preprocessing) | **Verified**. Output subjects dynamically hooked to downstream inputs. |
| ✅ | **Module B** (Identity Isolation)| **Verified by agent**. Remote SHA-256 matched local `test_outputs/`; crop, no-background, and mask outputs visually inspected. |
| ✅ | **Module C** (Composite Handoff) | **Verified composite handoff**. `moduleC_harmonization.json` now loads `module0_tgt.png` and `moduleB_crop.png` directly, uses a source-alpha plus oval trim mask, and saves `moduleC_composite/moduleC_harmonized`. |
| ❌ | **Module D** (Upscale) | Pending. Current workflow is still a Nano Banana Pro/API upscale placeholder. |

## ⚠️ Current Blocker & Active Hand-off
**Agent Action Paused:** Module C is now executable as a deterministic composite handoff, but true AI harmonization is intentionally disabled. The Flux/KSampler inpaint path produced a corrupted UI/screen artifact in `moduleC_harmonized_v3_graph_00001_.png`, so it was removed from the active Module C graph rather than left as a trap for the next run.

**Latest Verified Module C Run:**
1. Canonical output: `/app/ComfyUI/output/moduleC_composite/moduleC_harmonized_00002_.png`
2. Downstream input handoff: `/app/ComfyUI/input/moduleC_harmonized.png`
3. SHA-256 for both files: `b9678723974e4f3057e279a4ca4b12cd79a07080371bb811fdb0eb89b6e660a4`
4. Remote workflow deployment: `/app/ComfyUI/user/default/workflows/portrait_pipeline/moduleC_harmonization.json`
5. Visual review: accepted as a pipeline handoff image, not a final production-grade harmonized portrait.

**Next Required Action:**
1. Implement Module D. `production/workflows/moduleD_upscale.json` currently contains only a `MarkdownNote` placeholder plus load/preview/save scaffolding.
2. If true Module C harmonization is required before upscaling, redesign the inpaint path separately from the verified composite handoff and keep CFG at `1` until the conditioning-shape issue is resolved.
