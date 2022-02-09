#! /usr/bin/env/ python

import os
from typing import Optional
from src import utils, crypto


def unique_filename(length: int=8) -> str:
    '''
    Generate unique file name with needed length

    Parameters
    ------------
        length: int
            length of generated file name

    Returns
    ------------
        generated file name
    '''
    filename = ''
    while True:
        filename = utils.random_string(length)
        if not os.path.exists(filename):
            break

    return filename


def create_file(content: str) -> str:
    '''
    Create file from user content with unique file name

    Parameters
    ------------
        content: str
            content for new file

    Returns
    ------------
        name of created file
    '''
    filename = unique_filename(6)
    
    with open(filename, "w") as f:
        f.write(content)

    return filename


def create_signature_file(content: str) -> str:
    '''
    Create file from user content with unique file name
    and also files with hash

    Parameters
    ------------
        content: str
            content for new file

    Returns
    ------------
        name of created file
    '''
    filename = create_file(content)
    signers = crypto.SignatureFactory.signers
    for label in signers:
        signer = signers[label]()
        hash = signer(content)
        with open(f'{filename}.{label}', 'w') as file:
            file.write(hash)
    
    return filename


def read_file(filename: str) -> Optional[str]:
    '''
    Read file using recieved file name

    Parameters
    ------------
        filename: str

    Returns
    ------------
        content of file or raise exception "FileNotFound" if file doesn't exist
    '''
    if not os.path.isfile(filename):
        raise Exception("FileNotFound")
    
    with open(filename, "r") as f:
        data = f.read()
    
    return data


def read_signature_file(filename: str) -> str:
    '''
    Read file using recieved file name. Also it cheched for sign

    Parameters
    ------------
        filename: str

    Returns
    ------------
        content of file or raise exception "FileNotFound" if file doesn't exist
        or "FileBroken" if the file is not validate
    '''

    content = read_file(filename)
    
    signers = crypto.SignatureFactory.signers

    sign_checked = True
    sign_file_exist = False

    for label in signers:
        sign_filename = f'{filename}.{label}'
        if not os.path.exists(sign_filename):
            continue

        with open(sign_filename, 'r') as file:
            expected_hash = file.read()
        
        sign_file_exist = True
        
        actual_hash = signers[label]()(content)
        sign_checked = sign_checked & (expected_hash == actual_hash)
    
    if sign_file_exist and not sign_checked:
        raise Exception("FileBroken")
    
    return content
            

def delete_file(filename: str) -> None:
    '''
    Delete file by name

    Parameters
    ------------
        filename: str

    Returns
    ------------
        None
    '''
    if not os.path.isfile(filename):
        raise Exception("FileNotFound")

    os.remove(filename)


def list_dir() -> list:
    '''
    Return list of directories and files in current directory

    Returns
    ------------
        list of directories and files in current directory
    '''
    return os.listdir()


def change_dir(dirname: str) -> bool:
    '''
    Change current directory using new directory name

    Parameters
    ------------
        dirname: str
            name of new directory

    Returns
    ------------
        True: if changed was successful
        False: if changed wasn't successful
    '''
    if not os.path.isdir(dirname):
        raise Exception("DirectoryNotFound")

    os.chdir(dirname)
    return True


def get_file_meta_data(filename: str) -> Optional[tuple]:
    '''
    Read file creation date, modification date and file size

    Parameters
    ------------
        filename: str
            filename to read

    Returns
    ------------
        (creation time, modification time, filesize): tuple
    '''
    if not os.path.isfile(filename):
        return None
    
    file_stat = os.stat(filename)
    return (file_stat.st_ctime, file_stat.st_mtime, file_stat.st_size)
