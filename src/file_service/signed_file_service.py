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
        self.signature_dir = os.path.abspath(config.signature_dir())
     
    
    def pwd(self) -> None:
        return self.wrapped_fs.pwd()
    
    
    def abspath(self, fd_name:str) -> str:
        return '/'.join([self.signature_dir, fd_name])


    def create(self, data):
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
        filename = self.wrapped_fs.create(data)

        signature_filename = self.signer.get_sign_filename(filename)
        abs_path = self.abspath(signature_filename)
        with open(abs_path, 'w') as file:
            file.write(data_hash)

        return filename

    def read(self, filename):
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

        content = self.wrapped_fs.read(filename)
        
        abspath_filename = self.abspath(filename)
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
        abspath_filename = self.abspath(filename)
        sign_filename = self.signer.get_sign_filename(abspath_filename)
        if not os.path.exists(sign_filename):
            return
        
        os.remove(sign_filename)
        

    def ls(self) -> list:
        return self.wrapped_fs.ls()


    def chdir(self, new_directory):
        return self.wrapped_fs.chdir(new_directory)
        
        
    def get_meta_data(self, filename: str):
        return self.wrapped_fs.get_meta_data(filename)