import os
import shutil

def empty_folder(directory_name: str):
    """
    Remove all files and subdirectories within the specified directory.
    If the directory does not exist, it is created.
    """
    try:
        if not os.path.isdir(directory_name):
            os.makedirs(directory_name, exist_ok=True)
        else:
            for entry in os.listdir(directory_name):
                file_path = os.path.join(directory_name, entry)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # Remove file or symbolic link
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # Remove directory and its contents
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    except Exception as e:
        print(f"Error in empty_folder({directory_name}): {e}")

def list_dir(path: str):
    """
    Return a sorted list of non-hidden files in the specified directory.
    """
    try:
        if not os.path.isdir(path):
            return []
        files = [f for f in os.listdir(path) if not f.startswith('.')]
        return sorted(files)
    except Exception as e:
        print(f"Error listing directory {path}: {e}")
        return []
