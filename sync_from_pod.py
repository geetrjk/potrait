import paramiko, os
from dotenv import load_dotenv

load_dotenv('.env')
HOST = os.getenv('SIMPLEPOD_SSH_HOST')
PORT = int(os.getenv('SIMPLEPOD_SSH_PORT', 22))
USER = os.getenv('SIMPLEPOD_SSH_USER', 'root')
PWD = os.getenv('SIMPLEPOD_PASSWORD')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, port=PORT, username=USER, password=PWD)
sftp = c.open_sftp()

print("Syncing Workflows from Pod...")
remote_wf_dir = '/app/ComfyUI/user/default/workflows/portrait_pipeline'
local_wf_dir = 'production/workflows'
os.makedirs(local_wf_dir, exist_ok=True)

try:
    for f in sftp.listdir(remote_wf_dir):
        if f.endswith('.json'):
            print(f"Downloading {f}...")
            sftp.get(f'{remote_wf_dir}/{f}', os.path.join(local_wf_dir, f))
except Exception as e:
    print(f"Error accessing workflows: {e}")

sftp.close()
c.close()
print("Sync complete.")
