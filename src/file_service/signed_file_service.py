import copy
import os
from src.file_service import FileService
from src.config import Config
from src.crypto import SignatureFactory


class FileBroken(Exception):
    pass


class SignedFileService(FileService):

    def __init__(self, wrapped_fs: FileService) -> None:
        self.wrapped_fs = wrapped_fs
        
        config = Config()
        sign_method = config.signature_algo()
        self.signer = SignatureFactory.get_signer(sign_method)
        self.signature_dirname = config.signature_dirname()
     
    
    def pwd(self) -> None:
        return self.wrapped_fs.pwd()
    
    
    def abspath(self, fd_name:str) -> str:
        return os.path.join(self.signature_dirname, fd_name)


    async def create(self, data: bytes) -> str:
        '''
        Create file from user content with unique file name
        and also files with hash

        Parameters
        ------------
            data: str
                content for new file

        Returns
        ------------
            name of created file
        '''
        data_hash = self.signer(data)
        filename = await self.wrapped_fs.create(data)

        signature_path = os.path.join(self.pwd(), self.signature_dirname)
        if not os.path.exists(signature_path):
            os.mkdir(signature_path)

        signature_filename = self.signer.get_sign_filename(filename)
        abs_path = os.path.join(signature_path, signature_filename)
        
        with open(abs_path, 'w') as file:
            file.write(data_hash)

        return filename


    async def read(self, filename: str) -> bytes:
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

        content = await self.wrapped_fs.read(filename)
        
        abspath_filename  = os.path.join(self.pwd(), self.signature_dirname,
                    filename)
        sign_filename = self.signer.get_sign_filename(abspath_filename)
        if not os.path.exists(sign_filename):
            raise FileBroken(abspath_filename)

        with open(sign_filename, 'r') as file:
            expected_hash = file.read()
        
        actual_hash = self.signer(content)
        if expected_hash == actual_hash:
            return content
            
        raise FileBroken(abspath_filename)


    def delete(self, filename):
        self.wrapped_fs.delete(filename)
        abspath_filename  = os.path.join(self.pwd(), self.signature_dirname,
                    filename)
        sign_filename = self.signer.get_sign_filename(abspath_filename)
        if not os.path.exists(sign_filename):
            return
        
        os.remove(sign_filename)
        

    def ls(self) -> list:
        files_list = self.wrapped_fs.ls()
        if self.signature_dirname in files_list:
            files_list.remove(self.signature_dirname)
        return files_list


    def chdir(self, new_directory):
        return self.wrapped_fs.chdir(new_directory)
        
        
    def get_meta_data(self, filename: str):
        return self.wrapped_fs.get_meta_data(filename)