#!/usr/bin/env python3
"""SimplePod SSH utility for the portrait pipeline project."""
import os
import sys
import paramiko
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

HOST = os.getenv('SIMPLEPOD_SSH_HOST')
PORT = int(os.getenv('SIMPLEPOD_SSH_PORT', 22))
USER = os.getenv('SIMPLEPOD_SSH_USER', 'root')
PASSWORD = os.getenv('SIMPLEPOD_PASSWORD')

def get_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)
    return client

def run_cmd(cmd):
    client = get_client()
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    client.close()
    if out: print(out)
    if err: print(err, file=sys.stderr)
    return out

def upload_files(local_dir, remote_dir):
    client = get_client()
    sftp = client.open_sftp()
    for fname in os.listdir(local_dir):
        local_path = os.path.join(local_dir, fname)
        if os.path.isfile(local_path):
            remote_path = f"{remote_dir}/{fname}"
            print(f"  Uploading {fname} -> {remote_path}")
            sftp.put(local_path, remote_path)
    sftp.close()
    client.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python pod_ssh.py <command>")
        print("  check    - Verify ComfyUI path")
        print("  deploy   - Upload workflow JSONs")
        print("  run CMD  - Run arbitrary command")
        sys.exit(1)

    action = sys.argv[1]

    if action == 'check':
        print("=== Checking ComfyUI installation ===")
        run_cmd("ls -la /app/ComfyUI/ 2>/dev/null && echo '--- /app/ComfyUI found ---' || echo '/app/ComfyUI NOT FOUND'")
        run_cmd("ls -la /workspace/ComfyUI/ 2>/dev/null && echo '--- /workspace/ComfyUI found ---' || echo '/workspace/ComfyUI NOT FOUND'")

    elif action == 'deploy':
        print("=== Deploying workflow JSONs to SimplePod ===")
        # First, find ComfyUI path
        out = run_cmd("test -d /app/ComfyUI && echo '/app/ComfyUI' || (test -d /workspace/ComfyUI && echo '/workspace/ComfyUI' || echo 'NOT_FOUND')")
        comfy_path = out.strip()
        if comfy_path == 'NOT_FOUND':
            print("ERROR: ComfyUI not found on pod!")
            sys.exit(1)
        
        # Create the target directory
        remote_wf_dir = f"{comfy_path}/user/default/workflows/portrait_pipeline"
        run_cmd(f"mkdir -p {remote_wf_dir}")
        
        # Upload
        local_wf_dir = os.path.join(os.path.dirname(__file__), 'production', 'workflows')
        upload_files(local_wf_dir, remote_wf_dir)
        print(f"\n=== Deployed to {remote_wf_dir} ===")
        run_cmd(f"ls -la {remote_wf_dir}")

    elif action == 'run':
        cmd = ' '.join(sys.argv[2:])
        run_cmd(cmd)
