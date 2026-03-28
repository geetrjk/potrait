---
name: Research Analyzer
description: Extracts and summarizes node-specific settings from YouTube transcripts and research notes.
---

# Research Analyzer Skill

## Objective
Extract detailed methodologies, node-specific configurations, parameters, and model recommendations from raw research materials such as YouTube transcripts and research notes.

## Instructions
1. **Read Thoroughly**: Consume the provided text without any pre-existing biases about which ComfyUI nodes or models to use.
2. **Identify Key Components**: Look for explicit mentions of:
    - Custom nodes
    - Specific parameter values (e.g., CFG scale, denoise strength, steps)
    - Checkpoints, LoRAs, ControlNets, or IP-Adapter usage
    - Routing logic and workflow topology 
3. **Extract & Summarize**: Create a structured breakdown of the settings extracted from the source material.
4. **Remain Objective**: Do NOT assume or hallucinate nodes. If a technique is described without a specific node name, describe the *function* required.
