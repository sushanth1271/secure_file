# encrypter.py

import os
import json
import uuid
import hashlib
from secrets import token_bytes

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

CHUNK_SIZE = 1024 * 1024      # 1 MB per chunk
NONCE_SIZE = 12
PACKAGE_DIR = "packages"
KEY_DIR = "key"

def load_rsa_public(path="key/public.pem"):
    """
    Load RSA public key (PEM), used to wrap the AES key.
    """
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())

def encrypt_file(file_path, rsa_public_path="key/public.pem"):
    """
    Encrypts a file in chunks using AES-GCM, wraps AES key with a provided RSA public key,
    and stores everything in a dedicated package folder with a metadata.json.
    Returns path to the package folder.
    """
    filename = os.path.basename(file_path)
    package_id = f"{uuid.uuid4().hex}_{filename}"
    package_folder = os.path.join(PACKAGE_DIR, package_id + ".package")
    os.makedirs(package_folder, exist_ok=True)

    # Generate AES key and AESGCM instance
    aes_key = token_bytes(32)
    aesgcm = AESGCM(aes_key)

    nonces = []
    sha = hashlib.sha256()
    total = 0
    chunk_index = 0

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                if chunk_index == 0:
                    # Empty file support
                    nonce = token_bytes(NONCE_SIZE)
                    ct = aesgcm.encrypt(nonce, b"", None)
                    open(os.path.join(package_folder, f"part_{chunk_index:06d}.bin"), "wb").write(ct)
                    nonces.append(nonce.hex())
                break
            sha.update(chunk)
            total += len(chunk)
            nonce = token_bytes(NONCE_SIZE)
            ct = aesgcm.encrypt(nonce, chunk, None)
            with open(os.path.join(package_folder, f"part_{chunk_index:06d}.bin"), "wb") as out:
                out.write(ct)
            nonces.append(nonce.hex())
            chunk_index += 1

    # Wrap AES key with provided RSA public key
    pub_key = load_rsa_public(rsa_public_path)
    enc_key = pub_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    metadata = {
        "algorithm": "AES-GCM-256",
        "chunk_size": CHUNK_SIZE,
        "nonce_size": NONCE_SIZE,
        "num_chunks": chunk_index if chunk_index > 0 else 1,
        "original_name": filename,
        "file_size": total,
        "rsa_encrypted_key_hex": enc_key.hex(),
        "nonces_hex": nonces,
        "original_sha256": sha.hexdigest()
    }

    with open(os.path.join(package_folder, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    return package_folder

if __name__ == "__main__":
    # CLI usage sample: python encrypter.py <filepath>
    import sys
    if len(sys.argv) != 2:
        print("Usage: python encrypter.py <file_path>")
        sys.exit(1)
    package_folder = encrypt_file(sys.argv[1])
    print(f"Encrypted package created at: {package_folder}")
