import os
from typing import List, Tuple
from src.crypto import Encryption
from src.file_service import FileService


class EncryptedFileService(FileService):
    
    
    def __init__(self, wrapped_fs: FileService):
        self.wrapped_fs = wrapped_fs
        

    def read(self, filename : str) -> str:
        encryptor = Encryption.get_encryptor(filename)
        key_file_name = encryptor.key_filename(filename)
        with open(key_file_name, 'rb') as file:
            key = file.read()
        encrypted_data = self.wrapped_fs.read(filename)
        decrypted_data = encryptor.decrypt(encrypted_data, key)
        return decrypted_data
        

    def create(self, data : str) -> str:
        encryptor = Encryption.get_encryptor()
        encrypted_data, key = encryptor.encrypt(data)
        filename = self.wrapped_fs.create(encrypted_data)
        key_file_name= encryptor.key_filename(filename)
        with open(key_file_name, 'wb') as f:
            f.write(key)
        return filename


    def ls(self) -> List[str]:
        return self.wrapped_fs.ls()
        

    def chdir(self, dir: str) -> None:
        self.wrapped_fs.chdir(dir)
        

    def delete(self, filename: str) -> None:
        self.wrapped_fs.delete(filename)
        encryptor = Encryption.get_encryptor(filename)
        key_file_name = encryptor.key_filename(filename)
        os.remove(key_file_name)
        

    def get_meta_data(self, filename: str) -> Tuple[int, int, int]:
        return self.wrapped_fs.get_meta_data(filename)


    def pwd(self) -> str:
        '''Return abs path of working directory'''
        return self.wrapped_fs.pwd()
    
    
    def abspath(self, fd_name:str) -> str:
        '''Return abs path for directory or file'''
        return '/'.join([self.pwd(), fd_name])

