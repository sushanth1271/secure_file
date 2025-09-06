import sys
import tools

def divide():
    tools.empty_folder('files')
    tools.empty_folder('raw_data')
    FILE = tools.list_dir('uploads')
    FILE = './uploads/' + FILE[0]

    MAX = 1024 * 32                  # 32 KB - max chapter size
    BUF = 50 * 1024 * 1024          # 50 MB buffer size (reduced from 50GB to avoid system overload)

    chapters = 0
    uglybuf = b''                   # Make this a bytes buffer (important!)
    meta_data = open('raw_data/meta_data.txt', 'w')
    
    file__name = FILE.split('/')[-1]
    print(file__name)               # ✅ Fixed Python 3 print syntax
    
    meta_data.write(f"File_Name={file__name}\n")
    
    with open(FILE, 'rb') as src:
        while True:
            target_file = open(f'files/SECRET{chapters:07d}', 'wb')
            written = 0
            while written < MAX:
                if len(uglybuf) > 0:
                    target_file.write(uglybuf)
                    uglybuf = b''
                chunk = src.read(min(BUF, MAX - written))
                if not chunk:
                    break
                target_file.write(chunk)
                written += len(chunk)
            uglybuf = src.read(1)
            target_file.close()
            if not uglybuf:
                break
            chapters += 1
    
    meta_data.write(f"chapters={chapters + 1}")
    meta_data.close()
