import json
import os


def get_module_dir(file):
    return os.path.dirname(os.path.realpath(file))


def get_local_json_file(module_dir, file_name):
    path = os.path.join(module_dir, file_name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)