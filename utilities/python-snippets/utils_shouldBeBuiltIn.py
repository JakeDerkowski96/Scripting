import os
import platform


# determine which OS the script is being ran from
def get_path_sep():
    if platform.system() == "Windows":
        path_sep = '\\'
    else:
        path_sep = '/'
    return path_sep


# to check if arg is directory
def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_HOME = os.path.dirname(ROOT_DIR)