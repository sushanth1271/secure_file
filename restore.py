# restore.py

import os
import tools

FILES_DIR = 'files'
RAW_DATA_DIR = 'raw_data'
RESTORED_DIR = 'restored_file'

def restore():
    # Clear restored_file folder before starting
    tools.empty_folder(RESTORED_DIR)

    # Default restored filename fallback
    default_filename = "restored_output.txt"
    meta_file_path = os.path.join(RAW_DATA_DIR, 'meta_data.txt')

    # Read metadata: get original filename and chapter count
    filename = default_filename
    chapters = None

    if os.path.exists(meta_file_path):
        with open(meta_file_path, 'r') as meta_file:
            for line in meta_file:
                line = line.strip()
                if line.startswith("File_Name="):
                    filename = line.split('=', 1)[1]
                elif line.startswith("chapters="):
                    try:
                        chapters = int(line.split('=', 1)[1])
                    except ValueError:
                        chapters = None

    output_path = os.path.join(RESTORED_DIR, filename)
    os.makedirs(RESTORED_DIR, exist_ok=True)

    # List all files in files dir, sorted
    file_chunks = tools.list_dir(FILES_DIR)
    file_chunks.sort()

    with open(output_path, 'wb') as writer:
        for chunk in file_chunks:
            chunk_path = os.path.join(FILES_DIR, chunk)
            with open(chunk_path, 'rb') as reader:
                writer.write(reader.read())

    # Clean up chunk files after merge
    tools.empty_folder(FILES_DIR)

    print(f"✅ Restored file saved as '{output_path}'")

if __name__ == "__main__":
    restore()
