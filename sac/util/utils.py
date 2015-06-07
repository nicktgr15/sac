import shutil
import os


def remove_dir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)


def get_class_from_filename(filename):
    return filename.split("_")[-1].split(".")[0]