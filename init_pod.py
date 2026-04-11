import paramiko
import os
import sys
from dotenv import load_dotenv

load_dotenv('.env')

HOST = os.getenv('SIMPLEPOD_SSH_HOST')
PORT = int(os.getenv('SIMPLEPOD_SSH_PORT', 22))
USER = os.getenv('SIMPLEPOD_SSH_USER', 'root')
PWD = os.getenv('SIMPLEPOD_PASSWORD')

LOG_FILE = 'docs/logs/bootstrap.log'
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

print("🚀 Starting Resilient Pod Setup Orchestrator...")
print(f"Log output actively capturing to: {LOG_FILE} (run 'tail -f {LOG_FILE}' to watch)")

try:
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=PORT, username=USER, password=PWD, timeout=10)

    # 1. Upload Bootstrap
    print("⏳ Synchronizing bootstrap scripts...")
    sftp = c.open_sftp()
    sftp.put('docs/runbooks/bootstrap.sh', '/tmp/bootstrap.sh')

    # 2. Execute Bootstrap robustly
    print("⏳ Initiating Cloud Bootstrap Phase...")
    cmd = "bash /tmp/bootstrap.sh /app/ComfyUI true"
    stdin, stdout, stderr = c.exec_command(cmd, get_pty=True)

    # We will log everything to the file, but only print clean summaries to stdout
    with open(LOG_FILE, 'w') as log:
        log.write(f"=== Bootstrap Run: {HOST} ===\n")

        while True:
            line = stdout.readline()
            if not line:
                break

            stripped = line.strip()
            log.write(line)
            log.flush()

            # Print concise progress summaries only
            if "[START]" in stripped:
                print(f"  {stripped}")
            elif "[SUCCESS]" in stripped:
                print(f"  ✅ {stripped.replace('[SUCCESS] ', '')}")
            elif "[ERROR]" in stripped:
                print(f"  ❌ {stripped.replace('[ERROR] ', '')}")

    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print(f"\n❌ FATAL ERROR: Bootstrap exited with status {exit_status}.")
        print(f"Check {LOG_FILE} for full stack trace.")
        sys.exit(exit_status)

    print("✅ System Core Bootstrap complete.")

    # 3. Upload JSON Workflows
    print("\n⏳ Mapping workflows -> /app/ComfyUI/user/default/workflows/portrait_pipeline/")
    remote_wf_dir = '/app/ComfyUI/user/default/workflows/portrait_pipeline'

    local_wf_dir = 'production/workflows'
    count = 0
    for root, dirs, files in os.walk(local_wf_dir):
        for f in files:
            if f.endswith('.json'):
                sftp.put(os.path.join(root, f), f"{remote_wf_dir}/{f}")
                count += 1

    print("⏳ Mapping Inputs -> /app/ComfyUI/input/")
    sftp.put('subject_5 year curly.webp', '/app/ComfyUI/input/subject_5 year curly.webp')
    sftp.put('superman.png', '/app/ComfyUI/input/target_template.png')

    sftp.close()
    c.close()
    print(f"✅ {count} workflows and specific inputs synced successfully.")
    print("✨ Pod Setup 100% complete. Ready for Execution.")

except Exception as e:
    print(f"\n❌ SCRIPT CRASHED. Reason: {str(e)}")
    sys.exit(1)
