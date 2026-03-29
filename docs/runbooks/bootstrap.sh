#!/bin/bash
# =============================================================================
# SimplePod Bootstrap Script — Infrastructure Agnostic Core
# =============================================================================
# This script automates the full setup of a fresh ComfyUI container for the
# portrait pipeline. It is designed to be dynamically driven by the Agent's
# pre-execution hardware profiling checks.
#
# Usage (from local machine):
#   .venv/bin/python pod_ssh.py run "bash -s" < docs/runbooks/bootstrap.sh
# =============================================================================

set -e

COMFY_ROOT="${1:-/app/ComfyUI}"
CUSTOM_NODES="${COMFY_ROOT}/custom_nodes"
MODELS="${COMFY_ROOT}/models"

# Optional precision flag from hardware profiles
USE_FP8="${2:-false}"

echo "=============================================="
echo "  Bootstrap: ComfyUI Infrastructure Agnostic"
echo "=============================================="

# --- Step 1: Verification ---
echo "[1/5] Verifying ComfyUI installation..."
if [ ! -d "$COMFY_ROOT" ]; then
    echo "ERROR: ComfyUI not found at $COMFY_ROOT"
    exit 1
fi
echo "  ✅ Server detected at $COMFY_ROOT"

# --- Step 2: Custom Node Installations ---
echo ""
echo "[2/5] Cloning validated extensions..."
cd "$CUSTOM_NODES"

declare -A NODES
NODES["ComfyUI-RMBG"]="https://github.com/1038lab/ComfyUI-RMBG.git"
NODES["ComfyUI-Inpaint-CropAndStitch"]="https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch.git"
NODES["rgthree-comfy"]="https://github.com/rgthree/rgthree-comfy.git"
NODES["ComfyUI-KJNodes"]="https://github.com/kijai/ComfyUI-KJNodes.git"

for name in "${!NODES[@]}"; do
    if [ -d "$name" ]; then
        echo "  ⏭️  $name already installed."
    else
        echo "  📦 Cloning $name..."
        git clone "${NODES[$name]}" 2>&1 | tail -1
        echo "  ✅ Installed."
    fi
done

# --- Step 3: Python Environment Mapping ---
echo ""
echo "[3/5] Syncing internal Python logic..."

if [ -f "$CUSTOM_NODES/ComfyUI-RMBG/requirements.txt" ]; then
    pip install -r "$CUSTOM_NODES/ComfyUI-RMBG/requirements.txt" --quiet 2>&1 | tail -3
fi

if [ -f "$CUSTOM_NODES/ComfyUI-KJNodes/requirements.txt" ]; then
    pip install -r "$CUSTOM_NODES/ComfyUI-KJNodes/requirements.txt" --quiet 2>&1 | tail -3
fi

# --- Step 4: Hardware Dynamic Model Installs ---
echo ""
echo "[4/5] Initiating cloud model synchronization..."

FLUX_DIR="${MODELS}/diffusion_models/flux2"
mkdir -p "$FLUX_DIR"

if [ "$USE_FP8" = true ]; then
    echo "  ⚠️ HARDWARE PROFILE TRIGGERED: Utilizing FP8 precision models."
    
    # UNET Setup
    FLUX_FILE="${FLUX_DIR}/flux-2-klein-9b-kv-fp8.safetensors"
    if [ ! -f "$FLUX_FILE" ]; then
        wget -q --show-progress -O "$FLUX_FILE" 'https://huggingface.co/black-forest-labs/FLUX.2-klein-9b-kv-fp8/resolve/main/flux-2-klein-9b-kv-fp8.safetensors'
    fi

    # Text Encoder Setup
    CLIP_FILE="${MODELS}/text_encoders/qwen_3_8b_fp8mixed.safetensors"
    if [ ! -f "$CLIP_FILE" ]; then
        wget -q --show-progress -O "$CLIP_FILE" 'https://huggingface.co/Comfy-Org/flux2-klein-9B/resolve/main/split_files/text_encoders/qwen_3_8b_fp8mixed.safetensors'
    fi

else
    echo "  ⚠️ Proceeding with standard FP16 tensor models."
    # (Future-proofed automation lines for higher tier hardware...)
fi

# Universal VAE Setup
VAE_FILE="${MODELS}/vae/flux2-vae.safetensors"
if [ ! -f "$VAE_FILE" ]; then
    wget -q --show-progress -O "$VAE_FILE" 'https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors'
fi

# --- Step 5: Directory Map Setup ---
echo ""
echo "[5/5] Mapping blueprint destinations..."
WORKFLOW_DIR="${COMFY_ROOT}/user/default/workflows/portrait_pipeline"
mkdir -p "$WORKFLOW_DIR"

echo "=============================================="
echo "  Bootstrap Pipeline Synchronization Complete."
echo "=============================================="
