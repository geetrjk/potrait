import paramiko, os
from dotenv import load_dotenv

load_dotenv('.env')
HOST = os.getenv('SIMPLEPOD_SSH_HOST')
PORT = int(os.getenv('SIMPLEPOD_SSH_PORT'))
USER = os.getenv('SIMPLEPOD_SSH_USER')
PWD = os.getenv('SIMPLEPOD_PASSWORD')

local_out_dir = 'test_outputs'
os.makedirs(local_out_dir, exist_ok=True)

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, port=PORT, username=USER, password=PWD)
sftp = c.open_sftp()

print("Listing remote /app/ComfyUI/output/moduleB_identity")
try:
    for f in sftp.listdir('/app/ComfyUI/output/moduleB_identity'):
        if f.endswith('.png'):
            remote_path = f'/app/ComfyUI/output/moduleB_identity/{f}'
            local_path = os.path.join(local_out_dir, f)
            print(f"Downloading {f}...")
            sftp.get(remote_path, local_path)
except Exception as e:
    print(f"Error accessing remote directory: {e}")

sftp.close()
c.close()
print("Download complete.")
