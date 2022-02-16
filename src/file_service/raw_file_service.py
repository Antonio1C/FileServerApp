from datetime import datetime
import os
from src import utils
from typing import Optional, Tuple, Union
from src.file_service import FileService

class RawFileService(FileService):


    def __init__(self, directory: str = '.') -> None:
        self.work_dir = os.path.abspath(directory)
        

    @staticmethod
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
    
    
    def pwd(self) -> str:
        '''Return abs path of working directory'''
        return self.work_dir
    
    
    def abspath(self, fd_name:str) -> str:
        '''Return abs path for directory or file'''
        return '/'.join([self.pwd(), fd_name])


    def create(self, data: bytes) -> str:
        '''
        Create file from user content with unique file name

        Parameters
        ------------
            data: str
                content for new file

        Returns
        ------------
            name of created file
        '''
        filename = RawFileService.unique_filename(6)
        abs_path_filename = self.abspath(filename)
        
        with open(abs_path_filename, "wb") as file:
            file.write(data)

        return filename


    def read(self, filename: str) -> bytes:
        '''
        Read file using recieved file name

        Parameters
        ------------
            filename: str

        Returns
        ------------
            content of file or raise exception "FileNotFound" if file doesn't exist
        '''
        abs_path_file = self.abspath(filename)
        if not os.path.isfile(abs_path_file):
            raise FileNotFoundError(abs_path_file)
        
        with open(abs_path_file, "rb") as file:
            data = file.read()
        
        return data


    def ls(self) -> list:
        '''
        Return list of directories and files in current directory

        Returns
        ------------
            list of directories and files in current directory
        '''
        return os.listdir(path=self.work_dir)


    def chdir(self, new_directory: str) -> None:
        '''
        Change current directory using new directory name

        Parameters
        ------------
            new_directory: str
                name of new directory

        Returns
        ------------
            True: if changed was successful
            False: if changed wasn't successful
        '''
        abs_path = self.abspath(new_directory)
        if not os.path.isdir(abs_path):
            raise NotADirectoryError

        if not new_directory == '.':
            self.work_dir = os.path.abspath(abs_path)


    def delete(self, filename: str) -> None:
        '''
        Delete file by name

        Parameters
        ------------
            filename: str
        '''
        abs_path = self.abspath(filename)
        if not os.path.isfile(abs_path):
            raise FileNotFoundError

        os.remove(abs_path)

    def get_meta_data(self, filename: str) -> Tuple[str, str, int]:
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
        abspath = self.abspath(filename)
        if not os.path.isfile(abspath):
            raise FileNotFoundError
        
        file_stat = os.stat(abspath)
        ctime = datetime.fromtimestamp(file_stat.st_ctime).strftime('%m/%d/%Y %H:%M:%S')
        mtime = datetime.fromtimestamp(file_stat.st_mtime).strftime('%m/%d/%Y %H:%M:%S')
        fsize = file_stat.st_size

        return (ctime, mtime, fsize)