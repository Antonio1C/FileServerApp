#! /usr/bin/env/ python

import argparse
from src import file_service

def read_file():
    filename = input("Enter file name : ")
    content = file_service.read_file(filename)
    if content == None:
        print(f'file "{filename}" not exist!')
        return
    print(f'Content: {content}')


def create_file():
    content = input("Enter file content : ")
    filename = file_service.create_file(content)
    
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

# def set_mode():
#     filename = input("Enter file name: ")
#     if not os.path.isfile(filename):
#         print('file doesn\'t exist')
#         return
#     
#     new_mode = int(input('Enter new mode for file: '), 8)
#     os.chmod(filename, new_mode)
#     print(f'new mode for file: {oct(os.stat(filename).st_mode)}')
# 
# 
# def get_mode():
#     filename = input("Enter file name: ")
#     if not os.path.isfile(filename):
#         print('file not exists')
#         return
#     
#     print(f'{oct(os.stat(filename).st_mode)}')


def main():

    default_dir = './'

    parser = argparse.ArgumentParser("File server application")
    parser.add_argument("-d", "--directory", help='Set current directory', default=default_dir)
    args = parser.parse_args()

    file_service.change_dir(args.directory)
    
    commands = {
        "get": read_file,
        "create": create_file,
        "delete": delete_file,
        "ls": list_dir,
        "cd": change_dir,
#         "setmode": set_mode,
#         "getmode": get_mode
    }

    while True:
        command = input("Enter command: ")
        if command == "exit":
            return
        if command not in commands:
            print("Unknown command")
            continue
        command = commands[command]
        try:
            command()
        except Exception as ex:
            print(f"Error on {command} execution : {ex}")


if __name__ == "__main__":
    main()