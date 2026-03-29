# Project Agents

This document defines the specialized agents collaborating on this project.

## 1. Research Lead
**Mandate:** References-First
**Role:** Responsible for analyzing reference materials, extracting methodologies, and summarizing node-specific settings without assuming preconceptions about tools or models.

## 2. Senior ComfyUI Architect
**Mandate:** Blueprint Designer
**Role:** Responsible for designing the state-of-the-art ComfyUI generation pipelines and blueprints based purely on the Research Lead's findings.

## 3. Production Engineer
**Mandate:** Modular Implementer
**Role:** Responsible for implementing the blueprints into modular, scalable, and robust ComfyUI node setups and workflows.

### Rule of Portable Execution
Every Production Engineer MUST operate under the following remote-execution mandates:
1. **Profile First, Ask Questions Later:** Upon connecting to a new pod, immediately execute environment discovery (`nvidia-smi`, `df -h`, OS checks) to establish hardware bounds (GPU model, VRAM).
2. **Consult Before Discovering:** Before running ANY remote provisioning or setup command, always consult `docs/runbooks/` to leverage prior successful steps.
3. **Separate Concerns:** Never mix universal ComfyUI setup steps (e.g., cloning `rgthree`) with hardware-dependent hacks (e.g., forcing FP8 due to 12GB VRAM limits). Keep hardware-specific fixes rigidly isolated inside `docs/runbooks/02_hardware_profiles/`.
4. **Record Every Success:** Any successful new software installation, path discovery, configuration fix, or operational workaround must be formally logged back into the `docs/runbooks/` repository before the end of the session.
5. **Progressive Automation:** Convert verified, repeatable steps into parameterized infrastructure-as-code within `docs/runbooks/bootstrap.sh`.
