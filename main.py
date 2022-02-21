#! /usr/bin/env/ python

import argparse
from src.config import Config
from src.file_service import FileService, RawFileService, SignedFileService, EncryptedFileService
from src.file_service import FileBroken
from src.user_service import UserService
import logging
import logging.config
import yaml
from aiohttp import web
from src.http_server import create_web_app
import psycopg2


def read_file(f_service: FileService):
    filename = input("Enter file name: ")
    content = f_service.read(filename).decode()
    print(f'Content: {content}')


def create_file(f_service: FileService):
    content = input("Enter file content: ")
    filename = f_service.create(content.encode())
    
    print(f"created file name: {filename}")


def delete_file(f_service: FileService):
    filename = input("Enter file name : ")
    f_service.delete(filename)


def list_dir(f_service: FileService):
    print(f_service.ls())


def change_dir(f_service: FileService):
    directory = input("Enter directory name : ")
    f_service.chdir(directory)


def get_file_meta_data(f_service: FileService):
    filename = input("Enter file name: ")
    meta_data = f_service.get_meta_data(filename)
    if meta_data == None:
        return
    
    print(f'Creation time: {meta_data[0]}\nModification time: {meta_data[0]}\nFile size: {meta_data[2]}')


def pwd(f_service: FileService):
    print(f_service.pwd())
    

def console_main():

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
    
    work_dir = args.directory if 'directory' in args else config.working_directory()
    
    file_service = RawFileService(work_dir)
    if config.use_signature(): file_service = SignedFileService(file_service)
    if config.use_encryption(): file_service = EncryptedFileService(file_service)

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
        
        try:
            logging.info(f'executing command: {command}')
            command(file_service)
        except FileBroken as ex:
            err_text = f'sorry, the file "{ex.args[0]}" was broken'
            logging.error(err_text)
        except FileNotFoundError as ex:
            err_text = f'unfortunately file "{ex.args[0]}" not found, please, check the file name'
            logging.error(err_text)
        except Exception as ex:
            err_text = f"Error on {command} execution : {ex}"
            logging.error(err_text)

def main():
    with open(file='./logging_config.yaml', mode='r') as f:
        logging_yaml = yaml.load(stream=f, Loader=yaml.FullLoader)
    
    logging.config.dictConfig(config=logging_yaml)

    logging.info('start server')

    parser = argparse.ArgumentParser("File server application")
    parser.add_argument("-d", "--directory", help='Set current directory')
    parser.add_argument('-c', '--config', help='file with server configuration', default='config.ini')
    
    logging.info('parse arguments')
    args = parser.parse_args()
    logging.info(f"getting args: {args}")

    config = Config()
    config.load(args.config)
    
    work_dir = args.directory if args.directory != None else config.working_directory()
    
    file_service = RawFileService(work_dir)
    if config.use_signature(): file_service = SignedFileService(file_service)
    if config.use_encryption(): file_service = EncryptedFileService(file_service)

    conn = psycopg2.connect(dbname='file_server', user='postgres', password='postgres', host='192.168.10.1')
    user_service = UserService(conn)
    app = create_web_app(file_service, user_service)
    web.run_app(app)


if __name__ == "__main__":
    main()