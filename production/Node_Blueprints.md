# Production Blueprint: Modular Node Schematics

This document serves as the **Senior ComfyUI Architect's Blueprint** for translating the Phase 1 Research logic into explicit `.json` subgraph instructions. The **Production Engineer** must follow these node mappings precisely to ensure compatibility with our `Human-in-the-Loop` remote scaling strategy.

---

## Shared Architectural Rules
1. **No Monolithic Clusters:** Every Module listed below must be created as a separate workflow `.json` or explicitly encapsulated into a rigid "Subgraph" block in ComfyUI.
2. **Output Formatting:** All `SaveImage` nodes must be configured with specific prefix naming corresponding to their module (e.g., `moduleA_template/moduleA_base`).
3. **Model Selection:** All UNets must use `.safetensors`, specifically `GGUF` or `INT4/FP8` variants to abide by VRAM constraints.

---

## Module 0: Input Preprocessing (The Ingestion Block)
**Purpose:** Standardize chaotic human inputs into strict 1MP mathematical constraints.

*   **Primary Nodes Required:**
    *   `LoadImage` (x2) (One for Subject, One for Target)
    *   `GetImageSize` (From Comfy-Core / IT Tools)
    *   `ImageScaleToTotalPixels`
    *   `SaveImage` (x2)
*   **Data Flow Schema:**
    1.  `LoadImage(IMAGE)` routes to `GetImageSize` for validation.
    2.  `LoadImage(IMAGE)` routes to `ImageScaleToTotalPixels` (Set interpolation to `lanczos`, total pixels to match 1024x1024 area).
    3.  `ImageScaleToTotalPixels(IMAGE)` routes directly to `SaveImage`.
*   **Output Prefix:** `outputs/run_timestamp/module0_preprocessing/module0_...`

---

## Module A: Target Stage Composition (The Environment)
**Purpose:** Load the environment and prepare the target insertion zone.

*   **Primary Nodes Required:**
    *   `LoadImage` / `LayerUtility: LoadImagesFromPath` (To support dynamic folders)
    *   `RMBG` or `SAM2` (To isolate the replacement area)
    *   `SaveImage` (x2)
*   **Data Flow Schema:**
    1.  Ingest normalized `module0_tgt.png`.
    2.  Route to `SAM2` to pull a binary mask of the *Target's Face Area*.
*   **Output Prefix:** `moduleA_template/moduleA_base` & `moduleA_template/moduleA_mask` (Outputs the raw pixel space and the black/white mask).

---

## Module B: Identity Isolation (The Subject)
**Purpose:** Extract the user's face structure flawlessly from the source image.

*   **Primary Nodes Required:**
    *   `LoadImage`
    *   `RMBG` (Node: ComfyUI-RMBG, Model: RMBG-2.0)
    *   `AILab_CropObject` (To trim alpha-dead space)
    *   `SaveImage` (x2)
*   **Data Flow Schema:**
    1.  Ingest normalized `module0_subj.png`.
    2.  Route to `RMBG(IMAGE)` for background wipe -> `AILab_CropObject`.
*   **Output Prefix:** `moduleB_identity/moduleB_crop` & `moduleB_identity/moduleB_mask`.

---

## Module C: Hybrid Harmonization (The Integration)
**Purpose:** The critical blending block. Composites the cropped face, injects identity guidance, and inpaints the lighting.

*   **Primary Nodes Required:**
    *   `LoadImage` (Loading the Module A & B tracked outputs)
    *   `LayerUtility: ImageBlendAdvance V2` or `AILab_ImageCombiner`
    *   **Flux Ecosystem:** `UNETLoader`, `FluxKVCache`, `VAELoader`, `CLIPLoader`
    *   **Conditioning Protocol:** `CLIPTextEncode`, `ConditioningZeroOut`, `ReferenceLatent`, `InpaintModelConditioning`
    *   **Execution:** `InpaintCropImproved`, `KSampler`, `VAEDecode`, `InpaintStitchImproved`
    *   `SaveImage`
*   **Data Flow Schema (Advanced):**
    1.  **Composite:** `Target Base` + `Cropped Face` + `Target Mask` -> `LayerUtility` composites the raw pixels.
    2.  **Crop & Encode:** `Composite Image` + `Target Mask` -> `InpaintCropImproved` -> `VAEEncode`.
    3.  **Conditioning Engine:** `CLIPTextEncode` (Positive: "Raw details, perfect lighting", Negative: zero-out) -> `ConditioningZeroOut` -> `ReferenceLatent` -> `InpaintModelConditioning`.
    4.  **Sampling:** Feed all models, latent buffers, and conditioning into `KSampler`. 
        *   **CRITICAL VAR:** Denoise **0.55 - 0.75**. Sampler: `euler`, Scheduler: `simple`.
    5.  **Reconstruction:** `KSampler(LATENT)` -> `VAEDecode(PIXELS)` -> `InpaintStitchImproved` (fuses the high-res face back into the 1MP target).
*   **Output Prefix:** `moduleC_composite/moduleC_harmonized`.

---

## Module D: API-Augmented Upscaling (The Polish)
**Purpose:** Offload VRAM constraints to cloud detailing.

*   **Primary Nodes Required:**
    *   `LoadImage` (pulling `moduleC_harmonized.png`)
    *   `Nano Banana Pro` or equivalent API Upscale Proxy
    *   `SaveImage`
*   **Output Prefix:** `moduleD_final/moduleD_upscaled`.

---

## Module E: Evaluation / Validation (The QA Block)
**Purpose:** The Human-in-the-Loop visual array for artifact-based post-mortems over SSH.

*   **Primary Nodes Required:**
    *   `LoadImage` (x3 - loading Subject, Target, and Harmonized output)
    *   `Image Comparer (rgthree)` (Set mode to: Slide)
    *   `AILab_ImageCompare`
*   **Execution Strategy:** This subgraph is pure presentation. It does not generate new pixels. It loads the artifact paths dynamically and populates the ComfyUI browser with interactive sliders for immediate operator verification against identity drift.
