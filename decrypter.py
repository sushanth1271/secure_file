# decrypter.py

import os
import json
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

PACKAGE_DIR = "packages"
RESTORE_DIR = "restored_file"
KEY_DIR = "key"

def load_rsa_private(path="key/private.pem", password=None):
    """
    Loads an RSA private key from the given PEM file.
    """
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=password)

def numeric_sorted_parts(folder, prefix="part_", suffix=".bin"):
    """
    Returns a sorted list of chunk filenames matching the part_* pattern.
    """
    parts = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(suffix)]
    parts.sort(key=lambda x: int(x[len(prefix):-len(suffix)]))
    return parts

def decrypt_package(package_name, private_key_path="key/private.pem"):
    """
    Decrypts a package folder produced by encrypter.py.
    - package_name: the name of the package folder (not full path, just folder name)
    - private_key_path: location of the PEM private key
    Returns the path to the restored file.
    """
    package_path = os.path.join(PACKAGE_DIR, package_name)
    meta_path = os.path.join(package_path, "metadata.json")
    if not os.path.exists(meta_path):
        raise FileNotFoundError("No metadata.json found in: " + package_path)

    with open(meta_path, "r") as f:
        meta = json.load(f)

    priv_key = load_rsa_private(private_key_path)
    aes_key = priv_key.decrypt(
        bytes.fromhex(meta["rsa_encrypted_key_hex"]),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    aesgcm = AESGCM(aes_key)
    parts = numeric_sorted_parts(package_path)
    nonces = meta["nonces_hex"]
    sha = hashlib.sha256()

    os.makedirs(RESTORE_DIR, exist_ok=True)
    restored_path = os.path.join(RESTORE_DIR, meta["original_name"])

    with open(restored_path, "wb") as out:
        for fname, nonce_hex in zip(parts, nonces):
            part_path = os.path.join(package_path, fname)
            nonce = bytes.fromhex(nonce_hex)
            with open(part_path, "rb") as f:
                ct = f.read()
            pt = aesgcm.decrypt(nonce, ct, None)
            sha.update(pt)
            out.write(pt)

    # Integrity check
    if sha.hexdigest() != meta["original_sha256"]:
        print("⚠️ Integrity check failed! Restored file hash does not match original.")
    else:
        print("✅ File restored and verified:", restored_path)
    return restored_path

if __name__ == "__main__":
    # CLI usage: python decrypter.py <package_folder> [private_key_path]
    import sys
    if len(sys.argv) < 2:
        print("Usage: python decrypter.py <package_folder> [private_key_path]")
        sys.exit(1)
    package_folder = sys.argv[1]
    key_path = sys.argv[2] if len(sys.argv) == 3 else "key/private.pem"
    outpath = decrypt_package(package_folder, private_key_path=key_path)
    print("Restored file:", outpath)
