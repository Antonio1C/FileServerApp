import os
import random
from src import utils

def unique_filename():
    length = 3 + random.choice(range(4))
    filename = utils.random_string(length)
    return filename

def read_file(filename):
    if not os.path.isfile(filename):
        return None
    
    with open(filename, "r") as f:
        data = f.read()
    
    return data


def create_file(content: str):
    filename = unique_filename()
    while True:
        if not os.path.exists(filename):
            break
        filename = unique_filename()
    
    with open(filename, "w") as f:
        f.write(content)

    return filename

def delete_file(filename):
    if not os.path.isfile(filename):
        return

    os.remove(filename)


def list_dir():
    return os.listdir()


def change_dir(dirname):
    if not os.path.isdir(dirname):
        return False

    os.chdir(dirname)
    return True