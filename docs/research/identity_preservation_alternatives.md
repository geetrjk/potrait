# Research: Zero-Shot Identity Preservation & Alignment Alternatives

**Date:** April 11, 2026
**Objective:** Evaluate modern zero-shot face swap, identity preservation, and alignment models that might offer a simpler, direct approach compared to complex multi-stage masking and ControlNet diffusion pipelines.

---

## 1. ReActor (Fast Face Swap)
ReActor is a dedicated custom node for high-speed, direct face swapping without generating the image from scratch via diffusion.

- **Quality & Control:** Good for photorealistic swaps on front-facing subjects. It struggles significantly with extreme lighting differences, non-photorealistic artistic styles (e.g., stylized Superman), and extreme angles. No explicit structural pose control.
- **Local (SimplePod) Viability:** **High.** Extremely VRAM efficient. Easily runs on 6-8GB VRAM cards.
- **Setup Complexity:** **Low.** Single custom node (`ComfyUI-ReActor`), though it strictly requires `insightface` compilation (which can sometimes be tricky on Linux pods but once installed, works seamlessly).
- **Pros:** Fast, low VRAM, simple node topology.
- **Cons:** Very little artistic blending; often looks "pasted" on if lighting doesn't match perfectly.

## 2. PuLID (Portrait-based Lightning Identity)
A modern integration, heavily favored in the Flux ecosystem, designed to preserve identity without heavy training or LoRAs.

- **Quality & Control:** State-of-the-art likeness retention. When paired with Flux (e.g., `PuLID-Flux`), it handles lighting, texture, and artistic styles beautifully without the harsh edges of traditional face swappers.
- **Local (SimplePod) Viability:** **Medium.** Needs a base model like SDXL or Flux (quantized to FP8/GGUF to fit 12GB restrictions). It will push the 12GB VRAM limit aggressively if generating large images.
- **Setup Complexity:** **Medium to High.** Needs specific adapter nodes, `insightface`, and careful VRAM management on 12GB cards.
- **Pros:** High-fidelity blending, handles artistic styles securely, modern text-to-image integration.
- **Cons:** Can be slow and VRAM hungry depending on the base model used.

## 3. InstantID
A highly robust identity-preserving method specifically designed for structural consistency and pose handling.

- **Quality & Control:** Excellent. Uses a specialized ControlNet to enforce the facial structure and pose while the IP-Adapter transfers the identity. This solves the "orientation" problem directly within the generation pass.
- **Local (SimplePod) Viability:** **Medium-Low.** It heavily relies on SDXL + InstantID IP-Adapter + ControlNet concurrently. 12GB VRAM is the bare minimum, and Out-of-Memory (OOM) errors are common unless heavily optimized.
- **Setup Complexity:** **High.** Complex node spaghetti. Requires precise weight tuning (Identity vs. ControlNet structural weight).
- **Pros:** The strongest solution for retaining exact facial structures at difficult angles.
- **Cons:** Very heavy on VRAM, complex node setup.

## 4. OmniGen
A unified multimodal generative model handling text-to-image, inpainting, and identity preservation natively without swapping adapters.

- **Quality & Control:** Impressive unified capabilities, essentially an "all-in-one" black box. Less granular control over individual elements compared to modular nodes like ControlNet.
- **Local (SimplePod) Viability:** **Zero (Currently).** Requires a minimum of 24GB VRAM.
- **Setup Complexity:** **Low (Software) / Impossible (Hardware).** Simple node setup conceptually, but unrunnable on our current 12GB profile hardware constraints.
- **Pros:** Massively simplifies workflow topology.
- **Cons:** VRAM requirements make it a non-starter for SimplePod.

---

## Strategy Recommendation

**Verdict & Suggestion:** A **Hybrid Approach (PuLID + Inpainting/Masking)** or **ReActor (with a diffusion pass)** is recommended given our 12GB VRAM limits on SimplePod.

1. **Avoid OmniGen and InstantID** directly generating the entire composition simultaneously, as 12GB VRAM will likely bottleneck.
2. **The "Best of Both Worlds" Alternative:**
   - **Step 1: Generate Base Target.** Get the Superman target ready.
   - **Step 2 (Simpler Setup):** Use **ReActor** to do the heavy lifting of the initial face swap. This is incredibly VRAM-cheap.
   - **Step 3 (The Blending Pass):** Instead of complex orientation ControlNets, we run the ReActor output through a low-denoise (`0.25 - 0.35`) classic **SDXL/Flux inpainting pass** using our dilated mask. The diffusion model uses the ReActor face as the structural base and simply "paints over" the lighting and edges to match the artistic style.

This hybrid approach gives the **high identity match** of ReActor with the **perfect lighting/style blending** of diffusion, all while keeping peak VRAM usage comfortably within the 12GB hardware limits.
