import os
import tools

def restore():
    tools.empty_folder('restored_file')

    # Initialize a default filename
    default_filename = "restored_output.txt"
    meta_info = []

    try:
        with open('raw_data/meta_data.txt', 'r') as meta_data:
            for row in meta_data:
                temp = row.strip().split('=')
                if len(temp) > 1:
                    meta_info.append(temp[1])
    except FileNotFoundError:
        meta_info.append(default_filename)

    # Use the filename from meta_data.txt or fallback
    filename = meta_info[0] if meta_info and meta_info[0] else default_filename
    address = os.path.join('restored_file', filename)

    list_of_files = sorted(tools.list_dir('files'))

    with open(address, 'wb') as writer:
        for file in list_of_files:
            path = os.path.join('files', file)
            with open(path, 'rb') as reader:
                writer.write(reader.read())

    tools.empty_folder('files')
