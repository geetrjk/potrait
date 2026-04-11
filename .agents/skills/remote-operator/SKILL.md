---
name: Remote Operator
description: Teaches the Production Engineer how to interact with remote SSH environments, profile hardware, and access the dedicated runbook architectures.
---

# Remote Operator Skill

You are interacting with a remote cloud instance (e.g., SimplePod, RunPod) hosting ComfyUI. Because these instances are ephemeral or subject to scaling horizontally across different GPU architectures, you MUST abide by the logic in this skill before executing setup commands.

## Mandatory Profiling

Before attempting ANY `git clone`, `pip install`, or `wget` command on a newly provisioned pod, you must accurately diagnose the hardware bounds.

1. **Check the GPU:** Understand the CUDA limitations.
   - Execute: `nvidia-smi --query-gpu=name,memory.total --format=csv,noheader`
2. **Check the Disk:** Ensure enough storage exists for 20GB+ models.
   - Execute: `df -h /`
3. **Check the OS and Python logic:**
   - Execute: `python --version` and `which pip`

## Runbook Architecture Navigation

You must immediately consult the persistent knowledge located in `docs/runbooks/` to guide your setup. Do not reinvent the wheel using trial and error.

- Read `docs/runbooks/00_profiling_and_discovery.md` for baseline remote exploration rules.
- Read `docs/runbooks/01_environment_agnostic.md` to see exactly which universal GitHub repositories (like KJNodes, RMBG, rgthree) have been confirmed to work and their precise `git clone` URLs.
- Read `docs/runbooks/02_hardware_profiles/<profile-matching-current-gpu>.md` to understand precision constraints. For example, if your profiling determines you are on an RTX 3060 (12GB), you **must** use the constraints outlined in `rtx3060_12gb.md` (e.g., forcing FP8 over FP16).

## The Record Keeping Protocol

If you successfully implement a new installation, uncover a pod-specific directory path (e.g., `/app/ComfyUI/` vs `/workspace/ComfyUI/`), or bypass an error (e.g., by omitting interactive terminal prompts), you are strictly required to append that structural knowledge back into the `docs/runbooks/` tree.

- Hardware-agnostic changes go to `01_environment_agnostic.md`.
- Hardware-specific hacks go to the respective profile in `02_hardware_profiles/`.
- Breakdowns and workarounds go to `known_workarounds.md`.
- Reliable, idempotent deployment logic goes to `bootstrap.sh`.

## Resilient Execution & Reliability Labels

Due to silent SSH hanging bugs on large network downloads over `paramiko` `bash -s` pipes, all setup actions **MUST** utilize native stream loggers. The orchestration scripts have been classified for safety:

1. **`[Reliability: Experimental/Deprecated]`** - `pod_ssh.py run "bash..."`: Direct bash injections over `paramiko` are unbuffered and prone to hanging silently during heavy execution.
2. **`[Reliability: Stable]`** - `init_pod.py`: A native wrapper explicitly mapping stdout summaries without locking the stream. It validates exit statuses natively.

**Working Setup Step:**
If you need to bootstrap a new pod, simply run `python init_pod.py`. That script is perfectly reliable: it SFTPs `bootstrap.sh`, drives remote construction idempotently utilizing `wget -c`, streams results locally without consuming tokens, and securely manages exit codes.
