import json
import os


def get_module_dir(file):
    return os.path.dirname(os.path.realpath(file))


def get_local_json_file(module_dir, relative_file_path):
    path = os.path.join(module_dir, relative_file_path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
