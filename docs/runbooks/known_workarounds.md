# 🔨 Known Fixes & Workarounds Ledger

> Every time the Production Engineer encounters a failed installation, a path failure, or an infrastructure blocker, it MUST be cataloged here alongside the successful resolution.

## SimplePod Networking

### 🔴 Problem: `git clone` fails with "could not read Username"
- **Context:** Occurs when cloning custom nodes (specifically `ComfyUI-RMBG`).
- **Cause:** The repository URL was incorrect or private. Initial URL attempted was `https://github.com/AILab-AI/ComfyUI-RMBG.git`.
- **✅ Resolution:** The correct, actively maintained repository URL is `https://github.com/1038lab/ComfyUI-RMBG.git`. Git falls back to asking for a username when a URL results in a 404, causing automated scripts to hang or fail.

## Container PID 1 Restart Protocol

### 🔴 Problem: ComfyUI port `8188` already in use upon restart.
- **Context:** Trying to restart the ComfyUI server after installing custom nodes.
- **Cause:** SimplePod (and many cloud containers) boot ComfyUI as `PID 1` — the primary container entrypoint. Executing `kill -9 1` or force-killing python processes leads to stranded sub-processes or container looping without actually releasing the port bindings internally.
- **✅ Resolution:** Never manual-kill the primary python instance. On the April 11, 2026 SimplePod instance, authenticated `POST /manager/reboot` returned `405` and authenticated `GET /manager/reboot` returned `404`, so the safe path is to restart the pod/container from the provider control plane. After restart, verify `/object_info` before queueing workflows that depend on newly installed custom nodes.

## System Dependencies

### 🔴 Problem: `sshpass` is natively unavailable on macOS.
- **Context:** The orchestration agent attempting to automatically push `production/workflows/*.json` into the remote SimplePod.
- **Cause:** Apple removed/forbids `sshpass` natively for security reasons. `brew install sshpass` often fails or points to unsupported manual taps.
- **✅ Resolution:** Pivot to pure Python SFTP. We established a local `.venv` housing the `paramiko` library, utilizing standard `os.getenv()` logic to silently upload files and bypass manual password prompts securely.

### 🔴 Problem: UI Automation fails with `net::ERR_CONNECTION_REFUSED` or `net::ERR_INVALID_RESPONSE`
- **Context:** Running Playwright or other headless visual testers against the ComfyUI login page on a restarted pod.
- **Cause:** SimplePod aggressively scrambles ephemeral ports on every reboot or redeploy (e.g. bouncing from `20006` to `20009`). Furthermore, attempting to use headless browser subagents to click complex single-page apps (SPAs) like ComfyUI V2 leads to infinite DOM loops and connection timeouts.
- **✅ Resolution:** **NEVER rely entirely on UI automation for critical path tests.** Integrate Human-in-the-Loop (HITL). Always update `SIMPLEPOD_COMFYUI_URL` dynamically, and defer complex UI actions (like dragging and dropping JSONs or resetting the node registry) to the user manually. Agents should focus exclusively on API triggers, file verification, and log parsing.

## ComfyUI Module Execution

### 🔴 Problem: Node registry check can falsely report missing nodes
- **Context:** `check_nodes.py` returned only one node type and reported Impact Pack / MediaPipe nodes missing, even though authenticated ComfyUI later reported 1166 node types and `MediaPipeFaceMeshToSEGS` was present.
- **Cause:** The quick node-check path did not authenticate the same way as the working browser/API flow. It navigated to the base URL and filled only the password field when visible, which can leave the request in a limited or stale login context.
- **✅ Resolution:** For node availability checks, navigate to `<SIMPLEPOD_COMFYUI_URL>/login`, fill username `root` and `SIMPLEPOD_PASSWORD`, wait briefly, then call `/object_info` from that authenticated page context. Do not reinstall nodes just because `check_nodes.py` reports a one-node registry.

### 🔴 Problem: MediaPipe face detection is installed but not useful for the current target
- **Context:** `MediaPipeFaceMeshToSEGS` is installed through `ComfyUI-Impact-Pack` and appears in `/object_info`, but a Module A face-mask probe against `module0_tgt.png` produced an effectively blank mask.
- **Cause:** The original target/template image was a stylized masked superhero figure, not a normal human face. MediaPipe face mesh does not reliably detect masked or stylized face regions.
- **✅ Resolution:** Do not spend time reinstalling MediaPipe or Impact Pack for this case. Treat MediaPipe as available but unsuitable for this target. Module A needs a more reliable target-region mask strategy: manual mask, template-specific mask, SAM with an appropriate prompt/region, or a deterministic shape/region mask verified visually.

### 🔴 Problem: Module A preview node has a mask/image type mismatch
- **Context:** `moduleA_target_stage.json` queues and produces `moduleA_base_00001_.png` and `moduleA_mask_visual_00001_.png`, but ComfyUI reports a `return_type_mismatch` for preview node `6`.
- **Cause:** The `PreviewImage` node is linked to the `GrowMask` `MASK` output. `PreviewImage` expects `IMAGE`, not `MASK`.
- **✅ Resolution:** This warning is non-fatal for the current Module A save outputs. For a durable workflow fix, replace that preview with `MaskPreview` or insert `MaskToImage` before `PreviewImage`.

### 🔴 Problem: Module C runs but does not perform true identity harmonization yet
- **Context:** `moduleC_harmonization.json` executed successfully on SimplePod and wrote `moduleC_harmonized_00001_.png` and `moduleC_harmonized_steps12_cfg1_00001_.png`, but visual inspection showed an artificial face/neck transition.
- **Cause:** The graph only loads `moduleA_base.png`. It does not directly load `moduleB_crop.png` or `moduleB_mask.png`, so the subject identity was introduced through a temporary prepared `/app/ComfyUI/input/moduleA_base.png` alpha handoff. This proves the inpaint path can execute, but it is not a robust module handoff.
- **✅ Resolution:** Replaced the active Module C graph with a verified composite handoff. The current `production/workflows/moduleC_harmonization.json` loads `module0_tgt.png` and `moduleB_crop.png` directly, crops/resizes the subject head, inverts the source alpha mask, intersects it with an oval `CreateShapeMask`, feathers the final mask, composites with `ImageCompositeMasked`, and saves `moduleC_composite/moduleC_harmonized`. Treat this as the stable Module C handoff, not true AI harmonization.

### 🔴 Problem: Module C AI inpaint path produced a screen/UI artifact
- **Context:** The v3 Module C graph loaded the correct Module B artifacts and executed without node errors, but visual inspection of `moduleC_harmonized_v3_graph_00001_.png` showed a corrupted UI/screen artifact instead of the portrait.
- **Cause:** The failure occurred after the deterministic composite stage, inside the Flux/KSampler inpaint path. The pre-sampler composite was coherent, while the sampler output was unusable.
- **✅ Resolution:** Removed the sampler/inpaint path from the active Module C workflow and preserved it as a future redesign task rather than a live path. If AI harmonization is revisited, start from the verified composite handoff and add the inpaint path behind a separate test workflow so the stable downstream `moduleC_harmonized.png` handoff is not broken again.

### 🔴 Problem: `ImageCompositeMasked` mask polarity exposed checkerboard transparency
- **Context:** A Module C composite-stage probe using the resized subject alpha mask directly produced a checkerboard transparency patch from the `moduleB_crop.png` source image.
- **Cause:** The `LoadImage` mask output for the transparent PNG behaved opposite of the desired `ImageCompositeMasked` subject mask polarity in this graph.
- **✅ Resolution:** Insert `InvertMask` after the resized source alpha mask before combining it with the oval trim mask. The verified path is `CropMask -> ResizeMask -> InvertMask -> AILab_MaskCombiner(intersection with oval) -> FeatherMask -> ImageCompositeMasked`.

### 🔴 Problem: Raising Module C CFG above 1 caused a KSampler tensor-size error
- **Context:** A stronger in-memory Module C pass with 12 steps, denoise `0.9`, and CFG `1.4` failed at `KSampler` with `RuntimeError: Sizes of tensors must match except in dimension 2. Expected size 1 but got size 2`.
- **Cause:** The current `ReferenceLatent` / `InpaintModelConditioning` graph appears sensitive to the conditioning shape when CFG is increased above the known-working value.
- **✅ Resolution:** Keep CFG at `1` for this graph until the Module C conditioning path is redesigned. A 12-step pass with CFG `1` and denoise `0.9` executed successfully, though quality remained insufficient.

### 🔴 Problem: Module C local seam repair cannot fix the pasted-head architecture
- **Context:** `moduleC_inpaint_repair_experimental.json` queued successfully on SimplePod as prompt `da191334-b30d-4858-b2ec-497a3540a38d` and produced `moduleC_inpaint_repair_experimental_00001_.png`, `moduleC_inpaint_repair_mask_00001_.png`, and `moduleC_inpaint_repair_context_00001_.png`.
- **Cause:** The graph starts from the deterministic composite handoff and masks only the chin/collar seam. This can soften the local transition, but it cannot make the full cropped child head feel generated into the target superhero template. Separate tests with `ReferenceLatent` also failed to transfer identity reliably; available pod nodes did not include a usable PuLID, InstantID, or IPAdapter FaceID pipeline/model set.
- **✅ Resolution:** Do not promote the seam-repair output to canonical `moduleC_harmonized.png`. Use it only as an experimental diagnostic. The proper fix is a target-space inpaint architecture with explicit identity conditioning: start from `module0_tgt.png`, use a target head/face mask, condition on `moduleB_crop.png` through a real identity adapter, and reserve crop/stitch seam repair for the final cleanup pass.

### 🔴 Problem: ReActor workflow failed because of class-name and live-reload mismatch
- **Context:** `moduleA_fast_swap.json` initially failed with `missing_node_type` for node title `ReActor Fast Swap`. The pod already had `/app/ComfyUI/custom_nodes/ComfyUI-ReActor`, but authenticated `/object_info` did not list ReActor nodes in the live process.
- **Cause:** The workflow used `ReactorFaceSwap`, but the actual ReActor class name is `ReActorFaceSwap`. The workflow widget order also did not match the installed ReActor schema. Separately, `inswapper_128.onnx` was missing from `/app/ComfyUI/models/insightface`, and the current SimplePod ComfyUI process is PID 1 (`python main.py --listen --enable-manager`), so the Manager reboot helper did not fully reload custom nodes: authenticated `POST /manager/reboot` returned `405`, and `GET /manager/reboot` returned `404`.
- **✅ Resolution:** Corrected `production/workflows/moduleA_fast_swap.json` to use `ReActorFaceSwap` and the installed schema. Downloaded `inswapper_128.onnx` to `/app/ComfyUI/models/insightface/inswapper_128.onnx`; standalone Python import now exposes `ReActorFaceSwap`, `ReActorFaceSwapOpt`, and related classes. Do not queue the ReActor workflow until the ComfyUI backend has had a real pod/container restart and `/object_info` confirms `ReActorFaceSwap` is present.
