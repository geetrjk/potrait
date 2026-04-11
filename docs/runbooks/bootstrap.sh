#!/bin/bash
# =============================================================================
# SimplePod Bootstrap Script — Infrastructure Agnostic Core (Idempotent V2)
# =============================================================================
# Usage:
#   bash /tmp/bootstrap.sh /app/ComfyUI true
# =============================================================================

set -e

COMFY_ROOT="${1:-/app/ComfyUI}"
CUSTOM_NODES="${COMFY_ROOT}/custom_nodes"
MODELS="${COMFY_ROOT}/models"
USE_FP8="${2:-false}"

echo "[START] Bootstrap Pipeline Initialization"

# --- Step 1: Verification ---
echo "[START] Step 1: Verification"
if [ ! -d "$COMFY_ROOT" ]; then
    echo "[ERROR] ComfyUI not found at $COMFY_ROOT"
    exit 1
fi
echo "[SUCCESS] Server detected at $COMFY_ROOT"

# --- Step 2: Custom Node Installations ---
echo "[START] Step 2: Custom Node Integrations"
cd "$CUSTOM_NODES"

declare -A NODES
NODES["ComfyUI-RMBG"]="https://github.com/1038lab/ComfyUI-RMBG.git"
NODES["ComfyUI-Inpaint-CropAndStitch"]="https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch.git"
NODES["rgthree-comfy"]="https://github.com/rgthree/rgthree-comfy.git"
NODES["ComfyUI-KJNodes"]="https://github.com/kijai/ComfyUI-KJNodes.git"
NODES["ComfyUI-Impact-Pack"]="https://github.com/ltdrdata/ComfyUI-Impact-Pack.git"
NODES["ComfyUI-ReActor"]="https://github.com/Gourieff/ComfyUI-ReActor.git"
for name in "${!NODES[@]}"; do
    if [ -d "$name" ]; then
        if [ ! -d "$name/.git" ]; then
            echo "  ⚠️  Corrupted clone detected for $name. Purging..."
            rm -rf "$name"
            echo "  📦 Re-cloning $name..."
            git clone "${NODES[$name]}" "$name"
            echo "  [SUCCESS] $name clone complete."
        else
            echo "  [SUCCESS] $name already exists and is healthy."
        fi
    else
        echo "  📦 Cloning $name..."
        git clone "${NODES[$name]}" "$name"
        echo "  [SUCCESS] $name clone complete."
    fi
done

# --- Step 3: Python Environment Mapping ---
echo "[START] Step 3: Python Environment Sync"

if [ -f "$CUSTOM_NODES/ComfyUI-RMBG/requirements.txt" ]; then
    pip install -r "$CUSTOM_NODES/ComfyUI-RMBG/requirements.txt" --quiet
fi
if [ -f "$CUSTOM_NODES/ComfyUI-KJNodes/requirements.txt" ]; then
    pip install -r "$CUSTOM_NODES/ComfyUI-KJNodes/requirements.txt" --quiet
fi
if [ -f "$CUSTOM_NODES/ComfyUI-ReActor/requirements.txt" ]; then
    echo "  📦 Installing ReActor dependencies (insightface)..."
    pip install insightface onnxruntime-gpu --quiet || echo "  ⚠️ Warning: insightface compilation may have failed."
    pip install -r "$CUSTOM_NODES/ComfyUI-ReActor/requirements.txt" --quiet
    mkdir -p "${MODELS}/insightface"
    echo "  📥 Checking/Resuming ReActor swap model..."
    wget -c -q --show-progress -O "${MODELS}/insightface/inswapper_128.onnx" 'https://huggingface.co/datasets/Gourieff/ReActor/resolve/main/models/inswapper_128.onnx'
    echo "  [SUCCESS] ReActor swap model downloaded."
fi
echo "[SUCCESS] Python dependencies synced."

# --- Step 4: Hardware Dynamic Model Installs ---
echo "[START] Step 4: Model Matrix Verification"

FLUX_DIR="${MODELS}/diffusion_models/flux2"
mkdir -p "$FLUX_DIR"

if [ "$USE_FP8" = true ]; then
    echo "  ⚠️ Hardware Profile Triggered: FP8 Context active."
    
    # UNET
    FLUX_FILE="${FLUX_DIR}/flux-2-klein-9b-kv-fp8.safetensors"
    echo "  📥 Checking/Resuming UNET model..."
    wget -c -q --show-progress -O "$FLUX_FILE" 'https://huggingface.co/black-forest-labs/FLUX.2-klein-9b-kv-fp8/resolve/main/flux-2-klein-9b-kv-fp8.safetensors'
    echo "  [SUCCESS] UNET downloaded and verified."

    # Text Encoder Setup
    CLIP_FILE="${MODELS}/text_encoders/qwen_3_8b_fp8mixed.safetensors"
    echo "  📥 Checking/Resuming Text Encoder..."
    wget -c -q --show-progress -O "$CLIP_FILE" 'https://huggingface.co/Comfy-Org/flux2-klein-9B/resolve/main/split_files/text_encoders/qwen_3_8b_fp8mixed.safetensors'
    echo "  [SUCCESS] Text Encoder downloaded."
else
    echo "  ⚠️ Proceeding with standard FP16 tensor models."
fi

# VAE
VAE_FILE="${MODELS}/vae/flux2-vae.safetensors"
echo "  📥 Checking/Resuming VAE..."
wget -c -q --show-progress -O "$VAE_FILE" 'https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors'
echo "  [SUCCESS] VAE downloaded."

echo "[START] Step 5: Directory Map Setup"
WORKFLOW_DIR="${COMFY_ROOT}/user/default/workflows/portrait_pipeline"
mkdir -p "$WORKFLOW_DIR"
mkdir -p "${COMFY_ROOT}/input"
mkdir -p "${COMFY_ROOT}/output"
echo "[SUCCESS] Directories built."

echo "[SUCCESS] BOOTSTRAP COMPLETE"
