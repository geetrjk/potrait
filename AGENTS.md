# Project Agents

Codex entrypoint: this file is the canonical instruction file for Codex in this
repository. Gemini / Antigravity uses `GEMINI.md`. Shared cross-agent rules live
in `docs/agent_contract.md`; follow them unless the user gives a newer direct
instruction.

## Workspace Identity and Goals

**High-Level Goal:** Identity-consistent artistic generation.

The objective is to build a professional system where any person's identity can
be seamlessly integrated into artistic portraits, themed templates, and varied
character styles using ComfyUI.

**Core Principle:** Research MUST precede Architecture.

No models, nodes, or architectures should be assumed a priori. All system design
must be strictly derived from materials and data analyzed by the Research Lead.

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
6. **Self-Verification First:** Agents *must* pull down and visually process the generated outputs (using native multimodal capabilities and compression where space is constrained) BEFORE requesting manual user verification. Only request a human verification (HITL) once the Agent considers it logically successful.
