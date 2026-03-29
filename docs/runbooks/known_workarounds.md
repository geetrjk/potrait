# 🔨 Known Fixes & Workarounds Ledger

> Every time the Production Engineer encounters a failed installation, a path failure, or an infrastructure blocker, it MUST be cataloged here alongside the successful resolution.

## SimplePod Networking

### 🔴 Problem: `git clone` fails with "could not read Username"
- **Context:** Occurs when cloning custom nodes (specifically `ComfyUI-RMBG`).
- **Cause:** The repository URL was incorrect or private. Initial URL attempted was `https://github.com/AILab-AI/ComfyUI-RMBG.git`.
- **✅ Resolution:** The correct, actively maintained repository URL is `https://github.com/1038lab/ComfyUI-RMBG.git`. Git falls back to asking for a username when a URL results in a 404, causing automated scripts to hang or fail.

## Container PID 1 Restart Protocol

### 🔴 Problem: ComfyUI port `8188` already in use upon restart.
- **Context:** Trying to restart the ComfyUI server after installing custom nodes.
- **Cause:** SimplePod (and many cloud containers) boot ComfyUI as `PID 1` — the primary container entrypoint. Executing `kill -9 1` or force-killing python processes leads to stranded sub-processes or container looping without actually releasing the port bindings internally.
- **✅ Resolution:** Never manual-kill the primary python instance. Authenticate with the ComfyUI API (`/auth`) using the server `.env` credentials to obtain a bearer token, and then `POST` to the `/manager/reboot` API. This initiates a graceful python-level shutdown and restart without severing the container lifecycle or orphan-locking the SQLite database.

## System Dependencies

### 🔴 Problem: `sshpass` is natively unavailable on macOS.
- **Context:** The orchestration agent attempting to automatically push `production/workflows/*.json` into the remote SimplePod.
- **Cause:** Apple removed/forbids `sshpass` natively for security reasons. `brew install sshpass` often fails or points to unsupported manual taps.
- **✅ Resolution:** Pivot to pure Python SFTP. We established a local `.venv` housing the `paramiko` library, utilizing standard `os.getenv()` logic to silently upload files and bypass manual password prompts securely.
