import os
import base64
import tools
from cryptography.fernet import Fernet, MultiFernet, InvalidToken
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305, AESGCM, AESCCM

def save_decrypted_output(filename, decrypted_data):
    output_path = os.path.join("restored_file", filename)
    with open(output_path, 'wb') as out:
        out.write(decrypted_data)
    print(f"[✔] Decrypted '{filename}' → saved to restored_file/ ({len(decrypted_data)} bytes)")

def Algo1_decrypt(data, key):
    try:
        f = Fernet(key)
        return f.decrypt(data).decode()
    except InvalidToken:
        raise ValueError("❌ Failed to decrypt metadata — Fernet key may be incorrect or corrupted.")

def Algo1_extended_decrypt(filename, key1, key2):
    try:
        f = MultiFernet([Fernet(key1), Fernet(key2)])
        with open(f'raw_data/{filename}', 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data)
        save_decrypted_output(filename, decrypted_data)
    except InvalidToken:
        raise ValueError(f"❌ Failed to decrypt file {filename} using MultiFernet.")

def Algo2_decrypt(filename, key, nonce):
    chacha = ChaCha20Poly1305(key)
    aad = b"authenticated but unencrypted data"
    with open(f'raw_data/{filename}', 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = chacha.decrypt(nonce, encrypted_data, aad)
    save_decrypted_output(filename, decrypted_data)

def Algo3_decrypt(filename, key, nonce):
    aesgcm = AESGCM(key)
    aad = b"authenticated but unencrypted data"
    with open(f'raw_data/{filename}', 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = aesgcm.decrypt(nonce, encrypted_data, aad)
    save_decrypted_output(filename, decrypted_data)

def Algo4_decrypt(filename, key, nonce):
    aesccm = AESCCM(key)
    aad = b"authenticated but unencrypted data"
    with open(f'raw_data/{filename}', 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = aesccm.decrypt(nonce, encrypted_data, aad)
    save_decrypted_output(filename, decrypted_data)

def parse_metadata(meta_text):
    meta = {}
    for line in meta_text.strip().splitlines():
        if '=' in line:
            key, value = line.strip().split('=', 1)
            meta[key.strip()] = value.strip()
    return meta

def decrypter():
    print("[*] Cleaning 'restored_file' directory...")
    tools.empty_folder('restored_file')

    print("[*] Loading master key from 'key/My_Key.pem'...")
    with open("key/My_Key.pem", "rb") as key_file:
        master_key = key_file.read().strip()
        if len(master_key) != 44:
            raise ValueError("❌ Master key must be a valid 32-byte base64-encoded Fernet key (44 characters).")

    print("[*] Decrypting metadata from 'raw_data/store_in_me.enc'...")
    with open("raw_data/store_in_me.enc", "rb") as enc_meta:
        decrypted_meta_text = Algo1_decrypt(enc_meta.read(), master_key)

    metadata = parse_metadata(decrypted_meta_text)

    try:
        key1 = base64.b64decode(metadata["FernetKey1"])
        key2 = base64.b64decode(metadata["FernetKey2"])
        key3 = base64.b64decode(metadata["ChaChaKey"])
        key4 = base64.b64decode(metadata["AESKey"])
        key5 = base64.b64decode(metadata["AESCCMKey"])
        nonce12 = base64.b64decode(metadata["Nonce12"])
        nonce13 = base64.b64decode(metadata["Nonce13"])
    except KeyError as e:
        raise ValueError(f"❌ Missing key in metadata: {e}")
    except Exception as e:
        raise ValueError(f"❌ Error decoding keys from metadata: {e}")

    # Collect files to decrypt
    files = sorted([
        f for f in tools.list_dir('raw_data')
        if f != 'store_in_me.enc' and f.startswith("SECRET")
    ])

    print(f"[*] Found {len(files)} encrypted file(s) to decrypt.")
    for index, filename in enumerate(files):
        try:
            print(f"\n[+] Decrypting file [{index+1}/{len(files)}]: {filename}")
            if index % 4 == 0:
                Algo1_extended_decrypt(filename, key1, key2)
            elif index % 4 == 1:
                Algo2_decrypt(filename, key3, nonce12)
            elif index % 4 == 2:
                Algo3_decrypt(filename, key4, nonce12)
            else:
                Algo4_decrypt(filename, key5, nonce13)
        except Exception as e:
            print(f"❌ Error decrypting {filename}: {e}")

    print("\n✅ All decryption completed.")
    print("📁 Files successfully written to 'restored_file':")
    for f in os.listdir('restored_file'):
        path = os.path.join('restored_file', f)
        print(f" - {f} ({os.path.getsize(path)} bytes)")

    # 🔄 Merge all SECRET chunks into final file
    restored_files = sorted(
        [f for f in os.listdir('restored_file') if f.startswith('SECRET')],
        key=lambda x: int(x.replace("SECRET", ""))
    )

    output_path = os.path.join("restored_file", "restored_output.txt")
    with open(output_path, 'wb') as out_file:
        for fname in restored_files:
            with open(os.path.join("restored_file", fname), 'rb') as part_file:
                out_file.write(part_file.read())

    print(f"[+] Merged {len(restored_files)} chunks into 'restored_output.txt'")