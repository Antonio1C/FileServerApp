#! /usr/bin/env/ python

import argparse
from datetime import datetime
from src.config import Config
from src.crypto.encryption import HybridEncryption, SymetricEncryption
from src.file_service import FileService, RawFileService, SignedFileService
from src.file_service import FileBroken
import logging
import yaml
import logging.config

from src.file_service.encrypted_file_service import EncryptedFileService

def read_file(f_service):
    filename = input("Enter file name : ")
    content = f_service.read(filename)
    print(f'Content: {content}')


def create_file(f_service):
    content = input("Enter file content : ")
    filename = f_service.create(content)
    
    print(f"created file name: {filename}")


def delete_file(f_service):
    filename = input("Enter file name : ")
    f_service.delete(filename)


def list_dir(f_service):
    print(f_service.ls())


def change_dir(f_service: FileService):
    directory = input("Enter directory name : ")
    f_service.chdir(directory)


def get_file_meta_data(f_service):
    filename = input("Enter file name: ")
    meta_data = f_service.get_meta_data(filename)
    if meta_data == None:
        return
    
    ctime = datetime.fromtimestamp(meta_data[0])
    mtime = datetime.fromtimestamp(meta_data[1])
    fsize = meta_data[2]

    print(f'Creation time: {ctime}\nModification time: {mtime}\nFile size: {fsize}')


def pwd(f_service: FileService):
    print(f_service.pwd())
    

def main():

    with open(file='./logging_config.yaml', mode='r') as f:
        logging_yaml = yaml.load(stream=f, Loader=yaml.FullLoader)
    
    logging.config.dictConfig(config=logging_yaml)

    logging.info('start server')

    default_dir = './file_storage'

    parser = argparse.ArgumentParser("File server application")
    parser.add_argument("-d", "--directory", help='Set current directory', default=default_dir)
    parser.add_argument('-c', '--config', help='file with server configuration', default='config.ini')
    
    logging.info('parse arguments')
    args = parser.parse_args()
    logging.info(f"getting args: {args}")

    config = Config()
    config.load(args.config)
    
    # create instances for encryption
    hybrid_encr = HybridEncryption()
    
    raw_fs = RawFileService(args.directory)
    sign_fs = SignedFileService(raw_fs)
    encr_fs = EncryptedFileService(sign_fs)
    
    commands = {
        "get": read_file,
        "create": create_file,
        "delete": delete_file,
        "ls": list_dir,
        "cd": change_dir,
        "pwd": pwd,
        "meta": get_file_meta_data,
    }

    while True:
        command = input("Enter command: ")
        if command == "exit":
            logging.info('stop server')
            return
        if command not in commands:
            print("Unknown command")
            continue
        
        command = commands[command]
        
        # try:
        logging.info(f'executing command: {command}')
        command(raw_fs)
        # except FileBroken as ex:
            # err_text = f'sorry, the file "{ex.args[0]}" was broken'
            # logging.error(err_text)
        # except FileNotFoundError as ex:
            # err_text = f'unfortunately file "{ex.args[0]}" not found, please, check the file name'
            # logging.error(err_text)
        # except Exception as ex:
            # err_text = f"Error on {command} execution : {ex}"
            # logging.error(err_text)


if __name__ == "__main__":
    main()