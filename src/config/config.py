from configparser import ConfigParser
import os
from src import utils

class Config(metaclass=utils.Singleton):

    SIGNATURE_SECTION = 'SIGNATURE'
    ENCRYPTION_SECTION = 'ENCRYPTION'
    COMMON_SECTION = 'COMMON'

    def __init__(self, fs_dir:str = '.'):
        if not 'config_data' in self.__dict__:
            self.config_data = None
            self.__default_fs_dir = fs_dir
        

    def load(self, filename: str):
        if not os.path.exists(filename):
            return
            
        self.config_data = ConfigParser()
        self.config_data.read(filename)

    @staticmethod
    def check_config_data(config_data, section_name, value_name) -> bool:

        if config_data == None: return False
        
        if section_name not in config_data.sections(): return False
        
        section = config_data[section_name]
        if value_name not in section: return False
        
        return True
        

    def signature_algo(self) -> str:

        default_value = 'md5'
        sign_algo = 'signature_algo'

        config_data = self.config_data
        if not Config.check_config_data(config_data, Config.SIGNATURE_SECTION, sign_algo):
            return default_value
        
        section = config_data[Config.SIGNATURE_SECTION]
        return section[sign_algo]
        

    def signature_dirname(self) -> str:
        default_dir = '.'
        signature_dir = 'signature_files_directory'
        config_data = self.config_data
        if not Config.check_config_data(config_data, Config.SIGNATURE_SECTION, signature_dir):
            return default_dir
        
        section = config_data[Config.SIGNATURE_SECTION]
        return section[signature_dir]
    

    def encryption_type(self) -> str:
        default_value = 'aes'
        enc_type = 'encryption_type'

        config_data = self.config_data
        if not Config.check_config_data(config_data, Config.ENCRYPTION_SECTION, enc_type):
            return default_value
        
        section = config_data[Config.ENCRYPTION_SECTION]
        return section[enc_type]
    
    
    def encryption_keys_dirname(self):
        default_path = '.'
        keys_path = 'encryption_keys_directory'

        config_data = self.config_data
        if not Config.check_config_data(config_data, Config.ENCRYPTION_SECTION, keys_path):
            return default_path
        
        section = config_data[Config.ENCRYPTION_SECTION]
        return section[keys_path]


    def use_signature(self):
        default_value = False
        use_sign = 'use_signature'
        
        config_data = self.config_data
        if not Config.check_config_data(config_data, Config.COMMON_SECTION, use_sign):
            return default_value
        
        section = config_data[Config.COMMON_SECTION]
        return False if section[use_sign] == 0 else True


    def use_encryption(self):
        default_value = False
        use_incr = 'use_encryption'
        
        config_data = self.config_data
        if not Config.check_config_data(config_data, Config.COMMON_SECTION, use_incr):
            return default_value
        
        section = config_data[Config.COMMON_SECTION]
        return False if section[use_incr] == 0 else True


    def filestorage_directory(self) -> str:
        default_value = self.__default_fs_dir
        fs_dir = 'filestorage_directory'
        
        config_data = self.config_data
        if not Config.check_config_data(config_data, Config.COMMON_SECTION, fs_dir):
            return default_value
        
        section = config_data[Config.COMMON_SECTION]
        return section[fs_dir]