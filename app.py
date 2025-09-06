import os
from flask import Flask, request, redirect, render_template, send_file, flash
from werkzeug.utils import secure_filename
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
import tools  # your helper functions

# ---------------- FOLDERS ---------------- #
UPLOAD_FOLDER = './uploads/'
KEY_FOLDER = './key/'
ENCRYPTED_FOLDER = './encrypted/'
RESTORED_FOLDER = './restored_file/'

# ---------------- APP CONFIG ---------------- #
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['KEY_FOLDER'] = KEY_FOLDER
app.secret_key = 'your_secret_key'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(KEY_FOLDER, exist_ok=True)
os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)
os.makedirs(RESTORED_FOLDER, exist_ok=True)

# ---------------- HYBRID ENCRYPTION ---------------- #
def encrypt_file(file_path, encrypted_path, key_folder):
    session_key = get_random_bytes(16)
    rsa_key = RSA.generate(2048)
    private_key = rsa_key.export_key()
    public_key = rsa_key.publickey().export_key()

    # Save private key
    key_filename = os.path.basename(file_path) + ".pem"
    key_path = os.path.join(key_folder, key_filename)
    with open(key_path, "wb") as f:
        f.write(private_key)

    # Encrypt AES session key with RSA public key
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(public_key))
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt file with AES
    with open(file_path, "rb") as f:
        data = f.read()
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)

    # Save encrypted file
    with open(encrypted_path, "wb") as f:
        [f.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]

    return key_filename

def decrypt_file(encrypted_path, key_folder, restored_path):
    key_files = tools.list_dir(key_folder)
    if not key_files:
        raise FileNotFoundError("No key file found. Please upload your private key first.")
    private_key_file = key_files[0]
    private_key = RSA.import_key(open(os.path.join(key_folder, private_key_file), "rb").read())

    with open(encrypted_path, "rb") as f:
        enc_session_key = f.read(private_key.size_in_bytes())
        nonce = f.read(16)
        tag = f.read(16)
        ciphertext = f.read()

    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)

    with open(restored_path, "wb") as f:
        f.write(data)

# ---------------- ROUTES ---------------- #
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download/')
def dashboard():
    return render_template('download.html')

@app.route('/data', methods=['POST'])
def upload_file():
    # Clear old files
    tools.empty_folder(UPLOAD_FOLDER)
    tools.empty_folder(ENCRYPTED_FOLDER)
    tools.empty_folder(KEY_FOLDER)
    tools.empty_folder(RESTORED_FOLDER)

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return 'NO FILE SELECTED'

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    encrypted_path = os.path.join(ENCRYPTED_FOLDER, filename + ".bin")
    key_filename = encrypt_file(file_path, encrypted_path, KEY_FOLDER)

    uploaded_files = [filename]

    message = "✅ File encrypted successfully! Now download your private key."
    return render_template('download.html', message=message, key_filename=key_filename, uploaded_files=uploaded_files)

@app.route('/return-key/<filename>')
def return_key(filename):
    key_path = os.path.join(KEY_FOLDER, filename)
    if not os.path.exists(key_path):
        return "Key file not found.", 404
    return send_file(key_path, download_name=filename, as_attachment=True)

@app.route('/download_data', methods=['POST'])
def upload_key():
    tools.empty_folder(KEY_FOLDER)  # Remove old keys

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return 'NO FILE SELECTED'

    filename = secure_filename(file.filename)
    file.save(os.path.join(KEY_FOLDER, filename))

    encrypted_files = tools.list_dir(ENCRYPTED_FOLDER)
    if not encrypted_files:
        return "No encrypted file found. Please encrypt a file first.", 404

    encrypted_path = os.path.join(ENCRYPTED_FOLDER, encrypted_files[0])
    restored_filename = encrypted_files[0].replace(".bin", "")
    restored_path = os.path.join(RESTORED_FOLDER, restored_filename)
    decrypt_file(encrypted_path, KEY_FOLDER, restored_path)

    message = "✅ File decrypted successfully! Now download your restored file."
    return render_template('download.html', message=message, restored_filename=restored_filename)

@app.route('/return-file/')
def return_file_auto():
    restored_files = tools.list_dir(RESTORED_FOLDER)
    if not restored_files:
        return "No restored file found. Please decrypt a file first.", 404
    restored_path = os.path.join(RESTORED_FOLDER, restored_files[0])
    return send_file(restored_path, download_name=restored_files[0], as_attachment=True)

# ---------------- RUN ---------------- #
if __name__ == '__main__':
    url = "http://127.0.0.1:8000"
    print(f"\n🚀 Server running! Open in browser: {url}\n")
    app.run(host='127.0.0.1', port=8000, debug=True)
