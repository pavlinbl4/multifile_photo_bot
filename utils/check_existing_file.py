import os


def create_dir(folder_name: str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(script_dir, folder_name)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    return folder_path
