import copy
import os
from typing import List, Tuple
from src.crypto import Encryption, HybridEncryption, SymetricEncryption
from src.file_service import FileService
from src.config import Config


class EncryptedFileService(FileService):
    
    
    def __init__(self, wrapped_fs: FileService):
        if Config().encryption_type() == 'rsa':
            HybridEncryption(wrapped_fs.pwd())
        else:
            SymetricEncryption()

        self.wrapped_fs = wrapped_fs
        self.keys_dirname = Config().encryption_keys_dirname()
        

    async def read(self, filename : str) -> str:
        encryptor = Encryption.get_encryptor(filename)
        key_file_name = os.path.join(self.pwd(), self.keys_dirname,
                encryptor.key_filename(filename))
        with open(key_file_name, 'rb') as file:
            key = file.read()
        encrypted_data = await self.wrapped_fs.read(filename)
        decrypted_data = encryptor.decrypt(encrypted_data, key)
        return decrypted_data
        

    async def create(self, data : str) -> str:
        encryptor = Encryption.get_encryptor()
        encrypted_data, key = encryptor.encrypt(data)

        keys_path = os.path.join(self.pwd(), self.keys_dirname)
        if not os.path.exists(keys_path):
            os.mkdir(keys_path)

        filename = await self.wrapped_fs.create(encrypted_data)

        key_file_name = os.path.join(keys_path, encryptor.key_filename(filename))
        with open(key_file_name, 'wb') as f:
            f.write(key)
        return filename


    def ls(self) -> list:
        files_list = self.wrapped_fs.ls()
        if self.keys_dirname in files_list:
            files_list.remove(self.keys_dirname)
        return files_list
        

    def chdir(self, dir: str) -> None:
        self.wrapped_fs.chdir(dir)
        

    def delete(self, filename: str) -> None:
        self.wrapped_fs.delete(filename)
        encryptor = Encryption.get_encryptor(filename)
        key_file_name = os.path.join(self.pwd(), self.keys_dirname,
                encryptor.key_filename(filename))
        os.remove(key_file_name)
        

    def get_meta_data(self, filename: str) -> Tuple[str, str, int]:
        return self.wrapped_fs.get_meta_data(filename)


    def pwd(self) -> str:
        '''Return abs path of working directory'''
        return self.wrapped_fs.pwd()
    
    
    def abspath(self, fd_name:str) -> str:
        '''Return abs path for directory or file'''
        return os.path.join(self.pws(), fd_name)