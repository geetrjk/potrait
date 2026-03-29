import paramiko, os
from dotenv import load_dotenv

load_dotenv('.env')
HOST, PORT, USER, PWD = os.getenv('SIMPLEPOD_SSH_HOST'), int(os.getenv('SIMPLEPOD_SSH_PORT', 22)), os.getenv('SIMPLEPOD_SSH_USER', 'root'), os.getenv('SIMPLEPOD_PASSWORD')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, port=PORT, username=USER, password=PWD)
sftp = c.open_sftp()

print("Uploading inputs...")
sftp.put('subject_5 year curly.webp', '/app/ComfyUI/input/subject_5 year curly.webp')
sftp.put('production/workflows/module0_preprocessing.json', '/app/ComfyUI/user/default/workflows/portrait_pipeline/module0_preprocessing.json')

sftp.close()
c.close()
print("Upload complete!")
