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

print("Mapping workflow structures...")
remote_wf_dir = '/app/ComfyUI/user/default/workflows/portrait_pipeline'

local_wf_dir = 'production/workflows'
for root, dirs, files in os.walk(local_wf_dir):
    for f in files:
        if f.endswith('.json'):
            local_path = os.path.join(root, f)
            remote_path = f"{remote_wf_dir}/{f}"
            print(f"Uploading {f}...")
            sftp.put(local_path, remote_path)

print("Uploading inputs...")
input_dir = '/app/ComfyUI/input'
if os.path.exists('subject_5 year curly.webp'):
    sftp.put('subject_5 year curly.webp', f'{input_dir}/subject_5 year curly.webp')
if os.path.exists('superman.png'):
    sftp.put('superman.png', f'{input_dir}/target_template.png')

sftp.close()
c.close()
print("All workflows and inputs restored.")
