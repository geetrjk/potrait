# Project Status

**Date Updated:** April 11, 2026

## 🚦 Phase 5: Live Execution & Testing Loop (HITL)

We are iterating through the pipeline physically evaluating each node. 
* **Methodology:** User drives execution via browser clicks `->` Agent validates file outputs via SSH.

| Stage | Module Name | Status |
|:---:|---|---|
| ✅ | Infrastructure / Pod Setup | **Stable**. `init_pod.py` successfully provisions the server. |
| ✅ | **Module 0** (Preprocessing) | **Verified**. Output subjects dynamically hooked to downstream inputs. |
| ⚠️ | **Module B** (Identity Isolation)| **Verified basic extraction only**. Current workflow saves `moduleB_crop`, `moduleB_mask`, and `moduleB_full_nobg`, but it does not yet split subject face/neck/body into separate assets. |
| ⚠️ | **Module C** (Composite Handoff + Experimental Repair) | **Composite handoff verified; true harmonization still blocked**. `moduleC_harmonization.json` remains the stable downstream handoff. `moduleC_inpaint_repair_experimental.json` queues successfully and performs local seam/collar repair, but visual review shows it does not solve the global pasted-head architecture problem. |
| ❌ | **Module D** (Upscale) | Pending. Current workflow is still a Nano Banana Pro/API upscale placeholder. |

## ⚠️ Current Blocker & Active Hand-off
**Agent Action Paused:** Module C is executable as a deterministic composite handoff, but true AI harmonization is not solved. The original Flux/KSampler inpaint path produced a corrupted UI/screen artifact in `moduleC_harmonized_v3_graph_00001_.png`, so it was removed from the active Module C graph rather than left as a trap for the next run. A later local seam-repair experiment executes cleanly, but it only improves the chin/collar transition and does not integrate the head into the target superhero template.

**Latest Verified Module C Run:**
1. Canonical output: `/app/ComfyUI/output/moduleC_composite/moduleC_harmonized_00002_.png`
2. Downstream input handoff: `/app/ComfyUI/input/moduleC_harmonized.png`
3. SHA-256 for both files: `b9678723974e4f3057e279a4ca4b12cd79a07080371bb811fdb0eb89b6e660a4`
4. Remote workflow deployment: `/app/ComfyUI/user/default/workflows/portrait_pipeline/moduleC_harmonization.json`
5. Visual review: accepted as a pipeline handoff image, not a final production-grade harmonized portrait.

**Latest Module C Experiment:**
1. Workflow: `production/workflows/moduleC_inpaint_repair_experimental.json`
2. Remote deployment: `/app/ComfyUI/user/default/workflows/portrait_pipeline/moduleC_inpaint_repair_experimental.json`
3. Prompt ID: `da191334-b30d-4858-b2ec-497a3540a38d`; ComfyUI returned no node validation errors.
4. Output: `/app/ComfyUI/output/moduleC_composite/moduleC_inpaint_repair_experimental_00001_.png`
5. Visual review: neck seam is somewhat softened, but the child head still reads as overlaid. Do not promote this to canonical `moduleC_harmonized.png`.

**Latest Superman Run:**
1. Input mapping: local `superman.png` uploaded to `/app/ComfyUI/input/target_template.png`.
2. Module 0 prompt ID: `35cf0d0e-d101-4efb-9285-eab9ae83045b`; output copied to `/app/ComfyUI/input/module0_tgt.png`.
3. Module C prompt IDs: `5ec21f4f-6493-429a-b819-318168d05c1d`, `9ad9290a-9124-4a2e-a42b-5895086ad06b`, and `7900fa7d-55a5-4960-885b-214e3c56d599`; all returned no node validation errors.
4. Latest output: `/app/ComfyUI/output/moduleC_composite/moduleC_harmonized_00007_.png`.
5. Downstream input handoff: `/app/ComfyUI/input/moduleC_harmonized.png`.
6. SHA-256 for both files: `af018420a70a2c68b816403aa0e262376260f59ee2350ad65955001f225e45e6`.
7. Visual review: Superman execution works, but the composite output is still a pasted-head artifact. `production/workflows/moduleA_fast_swap.json` has been corrected to use `ReActorFaceSwap`, but the live ComfyUI process still needs a real backend restart before ReActor appears in `/object_info`.

**Latest Module C Debug Output Run:**
1. Prompt ID: `2276980c-aa4f-400a-a9f5-28943012df34`; ComfyUI returned no node validation errors.
2. `C0` debug output: `/app/ComfyUI/output/moduleC_debug/moduleC_C0_resized_subject_head_00001_.png`
3. `C0` mask debug output: `/app/ComfyUI/output/moduleC_debug/moduleC_C0_subject_alpha_inverted_mask_00001_.png`
4. `C1` debug output: `/app/ComfyUI/output/moduleC_debug/moduleC_C1_final_composite_mask_00001_.png`
5. `C2` debug output: `/app/ComfyUI/output/moduleC_debug/moduleC_C2_composite_handoff_00001_.png`
6. Note: these are labels for the currently implemented composite graph only. They are not a complete implementation of the corrected identity-conditioned architecture.

**Next Required Action:**
1. Decide whether to move forward to Module D using the stable composite handoff as a temporary artifact, or stop and solve Module C first.
2. For a real Module C fix, use the corrected ReActor-first workflow after a full pod/backend restart, then add a low-denoise diffusion cleanup pass. If ReActor is not acceptable, use a proper identity-conditioned inpaint path such as PuLID, InstantID, or IPAdapter FaceID with the required model files.
