# Shared Agent Contract

This file is the shared operating contract for Codex and Gemini / Antigravity.
Tool-specific entrypoints remain in `AGENTS.md` for Codex and `GEMINI.md` for
Gemini / Antigravity.

## Project Goal

Build a professional ComfyUI system for identity-consistent artistic generation,
where a person's identity can be integrated into portraits, themed templates,
and varied character styles.

## Core Principle

Research MUST precede Architecture.

No models, nodes, or architectures should be assumed a priori. System design
must be derived from the Research Lead's materials and findings.

## Roles

1. Research Lead: analyze reference materials and extract methodologies,
   node-specific settings, model references, and workflow topology without
   assuming tools in advance.
2. Senior ComfyUI Architect: translate research findings into modular ComfyUI
   blueprints and pipeline designs.
3. Production Engineer: implement the blueprints as modular, robust ComfyUI
   workflow JSONs and operational scripts.

## Repository Map

- `AGENTS.md`: Codex entrypoint and non-negotiable instructions.
- `GEMINI.md`: Gemini / Antigravity entrypoint and non-negotiable instructions.
- `.agents/skills/*/SKILL.md`: reusable task skills. Codex can discover these
  in the IDE harness; Antigravity may also use them.
- `.agents/workflows/`: Antigravity-style workflow documents. Codex can read
  them when explicitly referenced, but should not assume they are automatic.
- `docs/runbooks/`: operational memory for remote execution and setup.
- `production/Node_Blueprints.md`: ComfyUI architecture blueprint.
- `production/workflows/*.json`: source-of-truth ComfyUI workflow JSON files.
- `research/`: source research and reference materials.

## Remote Execution Rules

Before running remote provisioning or setup commands, consult `docs/runbooks/`.

On a new pod, profile the environment first:

```bash
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
df -h /
python --version || python3 --version
which pip
```

Keep universal setup steps in `docs/runbooks/01_environment_agnostic.md`.
Keep hardware-specific constraints in `docs/runbooks/02_hardware_profiles/`.
Log successful new installation steps, path discoveries, configuration fixes,
and operational workarounds back into the runbooks.

## Workflow JSON Iteration

The Git repository is the source of truth for workflow JSONs. ComfyUI pods are
transient execution environments.

- Local source: `production/workflows/*.json`
- Remote destination: `<COMFY_ROOT>/user/default/workflows/portrait_pipeline/`

If a workflow is manually changed in the ComfyUI UI, sync the updated JSON back
to the repository before continuing automated iteration.

Validate JSON syntax before merge when workflow files change:

```bash
for f in production/workflows/*.json; do python3 -m json.tool "$f" >/dev/null; done
```

## Parallel Codex and Antigravity Work

Codex and Antigravity may work against separate checkouts and branches, but they
should avoid editing the same workflow module or operational runbook at the same
time unless the user explicitly coordinates that work.

Suggested branch naming:

- Codex: `codex-<task>` or `codex/<task>` when the repository supports slash
  namespaces.
- Antigravity: `antigravity-<task>` or `antigravity/<task>`.

High-conflict files:

- `AGENTS.md`
- `GEMINI.md`
- `docs/agent_contract.md`
- `docs/runbooks/bootstrap.sh`
- `docs/runbooks/known_workarounds.md`
- `docs/STATUS.md`
- `production/workflows/*.json`

Before merging parallel work, review these files carefully and prefer preserving
tool-specific entrypoints while keeping shared rules in this contract.
