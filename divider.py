# divider.py

import os
import tools

CHUNK_SIZE = 32 * 1024  # 32 KB per chunk
UPLOADS_DIR = 'uploads'
FILES_DIR = 'files'
RAW_DATA_DIR = 'raw_data'

def divide(input_path=None):
    # Clean up from any previous operation
    tools.empty_folder(FILES_DIR)
    tools.empty_folder(RAW_DATA_DIR)

    # Get the file to split: if not given, use the first upload
    if input_path is None:
        uploaded = tools.list_dir(UPLOADS_DIR)
        if not uploaded:
            print("No file in uploads folder.")
            return
        input_path = os.path.join(UPLOADS_DIR, uploaded[0])

    # Prepare meta info file
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    meta_path = os.path.join(RAW_DATA_DIR, "meta_data.txt")
    file_name = os.path.basename(input_path)

    meta_info = []
    chapters = 0
    buffer = b''
    BUF = 50 * 1024 * 1024  # 50 MB read buffer, safe for memory

    with open(meta_path, 'w') as meta_file, open(input_path, 'rb') as src:
        meta_file.write(f"File_Name={file_name}\n")
        while True:
            part_filename = f'SECRET{chapters:07d}'
            with open(os.path.join(FILES_DIR, part_filename), 'wb') as part_file:
                written = 0
                while written < CHUNK_SIZE:
                    if buffer:
                        part_file.write(buffer)
                        written += len(buffer)
                        buffer = b''
                    chunk = src.read(min(BUF, CHUNK_SIZE - written))
                    if not chunk:
                        break  # EOF
                    part_file.write(chunk)
                    written += len(chunk)
                buffer = src.read(1)
            if not buffer:
                break
            chapters += 1
        meta_file.write(f"chapters={chapters + 1}")

    print(f"✅ Split '{file_name}' into {chapters + 1} parts in '{FILES_DIR}'.")

if __name__ == "__main__":
    # CLI usage: python divider.py [input_file]
    import sys
    if len(sys.argv) > 1:
        divide(sys.argv[1])
    else:
        divide()
