# 00. Hardware Profiling & Discovery

> **Goal:** Standardize the first 30 seconds of any interaction with a new simple/run pod to prevent incorrect execution assumptions.

## Environment Profiling Checklist

Every time the agent connects to a new SSH instance, the following discovery suite MUST be executed iteratively to catalog the operational environment.

### 1. GPU Compute Discovery
```bash
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
```
- **If total VRAM is < 16GB:** You MUST consult `02_hardware_profiles/rtx3060_12gb.md` (or similar low-VRAM profiles) before loading any FLUX pipelines. Proceeding with FP16 weights will result in immediate CUDA OOM crashes.
- **If total VRAM is > 20GB:** Safe to assume standard precision constraints.

### 2. File System Discovery
Do not assume ComfyUI is installed at a universal path. Cloud providers vary drastically.
```bash
# Check standard SimplePod vs RunPod paths
ls -la /app/ComfyUI/ 2>/dev/null || echo "Not at /app"
ls -la /workspace/ComfyUI/ 2>/dev/null || echo "Not at /workspace"
```
Determine the absolute path to ComfyUI and set it dynamically for all subsequent operational tasks. 

### 3. Dependency Logic Discovery
Ascertain how the system installs dependencies. Do not assume `pip` or virtual environments natively exist.
```bash
python --version
which pip
```

### 4. Storage Bounds
```bash
df -h /
```
- Determine free space. An end-to-end Flux setup requires ~20-25GB for base models (UNET, VAE, CLIP).

### Next Steps ➡️

Once profiled, move directly onto the universal installation instructions defined in `01_environment_agnostic.md`, and supplement any hardware limitations discovered during profiling by following the designated profile in `02_hardware_profiles/`.
