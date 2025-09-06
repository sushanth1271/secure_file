import tools
import os
import base64
import shutil
from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305, AESGCM, AESCCM

def Algo1(data, key):
    # Save encrypted metadata to raw_data instead of encrypted/
    with open("raw_data/store_in_me.enc", "wb") as target_file:
        f = Fernet(key)
        target_file.write(f.encrypt(data.encode()))

def Algo1_extented(filename, key1, key2):
    f = MultiFernet([Fernet(key1), Fernet(key2)])
    with open(f'files/{filename}', 'rb') as file, open(f'encrypted/{filename}', 'wb') as target_file:
        target_file.write(f.encrypt(file.read()))

def Algo2(filename, key, nonce):
    chacha = ChaCha20Poly1305(key)
    aad = b"authenticated but unencrypted data"
    with open(f'files/{filename}', 'rb') as file, open(f'encrypted/{filename}', 'wb') as target_file:
        target_file.write(chacha.encrypt(nonce, file.read(), aad))

def Algo3(filename, key, nonce):
    aesgcm = AESGCM(key)
    aad = b"authenticated but unencrypted data"
    with open(f'files/{filename}', 'rb') as file, open(f'encrypted/{filename}', 'wb') as target_file:
        target_file.write(aesgcm.encrypt(nonce, file.read(), aad))

def Algo4(filename, key, nonce):
    aesccm = AESCCM(key)
    aad = b"authenticated but unencrypted data"
    with open(f'files/{filename}', 'rb') as file, open(f'encrypted/{filename}', 'wb') as target_file:
        target_file.write(aesccm.encrypt(nonce, file.read(), aad))

def encrypter():
    # Step 1: Clean folders
    tools.empty_folder('key')
    tools.empty_folder('encrypted')
    tools.empty_folder('raw_data')

    # Step 2: Generate Keys
    key_master = Fernet.generate_key()
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    key3 = ChaCha20Poly1305.generate_key()
    key4 = AESGCM.generate_key(bit_length=128)
    key5 = AESCCM.generate_key(bit_length=128)

    # Step 3: Generate nonces
    nonce12 = os.urandom(12)
    nonce13 = os.urandom(13)

    # Step 4: Encrypt files using multiple algorithms
    files = sorted(tools.list_dir('files'))

    for index, filename in enumerate(files):
        if index % 4 == 0:
            Algo1_extented(filename, key1, key2)
        elif index % 4 == 1:
            Algo2(filename, key3, nonce12)
        elif index % 4 == 2:
            Algo3(filename, key4, nonce12)
        else:
            Algo4(filename, key5, nonce13)

    # Step 5: Create metadata string
    original_filename = files[0] if files else "unknown"
    meta_data = f"""File_Name={original_filename}
chapters={len(files)}
FernetKey1={base64.b64encode(key1).decode()}
FernetKey2={base64.b64encode(key2).decode()}
ChaChaKey={base64.b64encode(key3).decode()}
AESKey={base64.b64encode(key4).decode()}
AESCCMKey={base64.b64encode(key5).decode()}
Nonce12={base64.b64encode(nonce12).decode()}
Nonce13={base64.b64encode(nonce13).decode()}
"""

    # Step 6: Encrypt and save metadata
    Algo1(meta_data, key_master)

    # Step 7: Save master key
    with open("key/My_Key.pem", "wb") as key_file:
        key_file.write(key_master)

    # Step 8: Move encrypted files into raw_data
    for f in tools.list_dir('encrypted'):
        shutil.copy(f'encrypted/{f}', f'raw_data/{f}')

    # Step 9: Clean original files folder
    tools.empty_folder('files')
