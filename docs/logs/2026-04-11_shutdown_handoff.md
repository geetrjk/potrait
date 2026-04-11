# Shutdown Handoff - April 11, 2026

## Safe Shutdown Verdict

The SimplePod instance can be turned off. The repository is the source of truth for workflow JSONs and runbook state. The latest workflows were deployed to the pod before shutdown, and the relevant local JSONs validate with `python -m json.tool`.

Do not rely on pod-local state after shutdown except for the notes below. A fresh pod should be bootstrapped from this repository with `init_pod.py`.

## Latest Remote State Before Shutdown

- Branch: `codex-initial-draft`
- Remote ComfyUI root: `/app/ComfyUI`
- GPU profile observed earlier in the session: RTX 3060 / 12GB VRAM
- Remote workflow directory: `/app/ComfyUI/user/default/workflows/portrait_pipeline`
- Active target template: local `superman.png` uploaded as `/app/ComfyUI/input/target_template.png`
- Module 0 Superman prompt: `35cf0d0e-d101-4efb-9285-eab9ae83045b`
- Latest Module C Superman prompt: `7900fa7d-55a5-4960-885b-214e3c56d599`
- Latest Module C Superman output: `/app/ComfyUI/output/moduleC_composite/moduleC_harmonized_00007_.png`
- Downstream handoff copied to: `/app/ComfyUI/input/moduleC_harmonized.png`
- SHA-256 for both latest Module C files: `af018420a70a2c68b816403aa0e262376260f59ee2350ad65955001f225e45e6`

## What Works

- `module0_preprocessing.json` runs with `superman.png` as `target_template.png`.
- `moduleC_harmonization.json` runs against the Superman target without node validation errors.
- `moduleC_inpaint_repair_experimental.json` queues and outputs a local seam-repair attempt.
- `init_pod.py` successfully drives the idempotent bootstrap and uploads workflows/inputs.

## What Is Still Not Good Enough

- The current Module C canonical output is a composite fallback, not true harmonization. It still reads as a pasted child head over the superhero target.
- Seam-only inpainting does not fix the architecture because it repairs the edge after the wrong primary operation.
- Module B only performs basic subject extraction. It does not yet split face, neck, and body into separate assets.

## ReActor Status

ReActor is the recommended next practical path for the Superman template, followed by low-denoise diffusion cleanup.

- Corrected workflow: `production/workflows/moduleA_fast_swap.json`
- Correct ReActor class name: `ReActorFaceSwap`
- Correct swap model path: `/app/ComfyUI/models/insightface/inswapper_128.onnx`
- Standalone Python import on the pod exposed `ReActorFaceSwap`, `ReActorFaceSwapOpt`, and related classes.
- Live `/object_info` did not expose ReActor before shutdown because the ComfyUI backend had not had a real provider-level restart after the node/model installation.
- Authenticated `POST /manager/reboot` returned `405`; authenticated `GET /manager/reboot` returned `404`.

After turning the pod back on, run `init_pod.py`, then verify `/object_info` contains `ReActorFaceSwap` before queueing `moduleA_fast_swap.json`.

## Repeated Mistakes To Avoid

- Do not reinstall MediaPipe for masked/stylized superhero targets. MediaPipe can be installed and still be useless for a masked or stylized face region.
- Do not assume `ReferenceLatent` is identity conditioning. It did not transfer the child identity reliably in these tests.
- Do not promote seam-repair outputs to `moduleC_harmonized.png`; they are diagnostics only.
- Do not assume a custom node folder means the live ComfyUI process has loaded it. Verify `/object_info`.
- Do not use `ReactorFaceSwap`; the class name is `ReActorFaceSwap`.
- Do not skip `inswapper_128.onnx`; ReActor needs it under `models/insightface`.
- Do not trust `/manager/reboot` on this SimplePod setup without checking the HTTP status and then verifying `/object_info`.

## Restart Checklist

1. Start a new SimplePod instance from the provider UI.
2. Update `.env` if the SSH or ComfyUI port changed.
3. Run `python init_pod.py` from the repo root.
4. Verify the hardware profile and `/object_info`; specifically confirm `ReActorFaceSwap` is present.
5. Run Module 0 with `superman.png`.
6. Copy latest `module0_tgt` and `module0_subj` outputs into `/app/ComfyUI/input/`.
7. Queue `moduleA_fast_swap.json`.
8. If ReActor output is acceptable, build the low-denoise cleanup pass; otherwise continue with PuLID/IPAdapter FaceID research.
