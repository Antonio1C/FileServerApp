#! /usr/bin/env/ python

import argparse
from datetime import datetime
from src import file_service
import logging
import yaml
import logging.config

def read_file():
    filename = input("Enter file name : ")
    content = file_service.read_signed_file(filename)
    if content == None:
        print(f'file "{filename}" not exist!')
        return
    print(f'Content: {content}')


def create_file():
    content = input("Enter file content : ")
    filename = file_service.create_signed_file(content, 'md5')
    
    print(f"created file name: {filename}")


def delete_file():
    filename = input("Enter file name : ")
    file_service.delete_file(filename)


def list_dir():
    print(file_service.list_dir())


def change_dir():
    directory = input("Enter directory name : ")
    if file_service.change_dir(directory):
        print(f"new directory: {directory}")


def get_file_meta_data():
    filename = input("Enter file name: ")
    meta_data = file_service.get_file_meta_data(filename)
    if meta_data == None:
        return
    
    ctime = datetime.fromtimestamp(meta_data[0])
    mtime = datetime.fromtimestamp(meta_data[1])
    fsize = meta_data[2]

    print(f'Creation time: {ctime}\nModification time: {mtime}\nFile size: {fsize}')


def main():

    with open(file='./logging_config.yaml', mode='r') as f:
        logging_yaml = yaml.load(stream=f, Loader=yaml.FullLoader)
        logging.config.dictConfig(config=logging_yaml)

    default_dir = './file_storage/'

    logging.info('start server')

    parser = argparse.ArgumentParser("File server application")
    parser.add_argument("-d", "--directory", help='Set current directory', default=default_dir)
    
    logging.info('parse arguments')
    args = parser.parse_args()
    logging.info(f"getting args: {args}")

    file_service.change_dir(args.directory)
    
    commands = {
        "get": read_file,
        "create": create_file,
        "delete": delete_file,
        "ls": list_dir,
        "cd": change_dir,
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
            command()
        except file_service.FileBroken as ex:
            err_text = f'sorry, the file "{ex.args[0]}" was broken'
            logging.error(err_text)
        except FileNotFoundError as ex:
            err_text = f'unfortunately file "{ex.args[0]}" not found, please, check the file name'
            logging.error(err_text)
        except Exception as ex:
            err_text = f"Error on {command} execution : {ex}"
            logging.error(err_text)


if __name__ == "__main__":
    main()