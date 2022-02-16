
from abc import ABCMeta, abstractmethod
import os
from Crypto import Random
from typing import Tuple

from src.config import Config
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from src.utils import random_string


class Encryption(metaclass=ABCMeta):

    encryptors = []

    def __init__(self) -> None:
        config = Config()
        self.keys_path = os.path.abspath(config.encryption_keys_path())
        Encryption.encryptors.append(self)
        
    
    def key_filename(self, filename: str) -> str:
        return os.path.join(self.keys_path, '.'.join([filename, self.get_type()]))
    
    
    @abstractmethod
    def encrypt(self, data: str) -> Tuple[str, str]: raise NotImplemented()

    
    @abstractmethod
    def decrypt(self, encrypted_data: str, key: str) -> str: raise NotImplemented()


    @abstractmethod
    def get_type(self) -> str: raise NotImplemented()


    @staticmethod
    def get_encryptor(filename: str=''):
        if filename == '':
            encr_type = Config().encryption_type()
            for encryptor in Encryption.encryptors:
                if encryptor.get_type() == encr_type:
                    return encryptor
            raise Exception('Not found encryptor by type %s' %encr_type)
        else:
            for encryptor in Encryption.encryptors:
                key_file = encryptor.key_filename(filename)
                if os.path.exists(key_file):
                    return encryptor
            raise Exception('Not found encryptor for filename %s' %filename)
    
    
class SymetricEncryption(Encryption):

    def encrypt(self, data: bytes) -> Tuple[bytes, bytes]:

        key = random_string(16).encode()
        aes = AES.new(key, AES.MODE_EAX)
        encrypted_data, tag = aes.encrypt_and_digest(data)

        session_key = bytearray(key)
        session_key.extend(bytearray(tag))
        session_key.extend(bytearray(aes.nonce))
        
        print(session_key)
        
        return encrypted_data, session_key

    
    def decrypt(self, encrypted_data: bytes, key: bytes) -> bytes:
        n = 16
        print(key)
        session_key, tag, nonce = (bytearray(key[i:i+n]) for i in range(0, len(key), n))
        aes = AES.new(session_key, AES.MODE_EAX, nonce)
        decrypted_data = aes.decrypt_and_verify(encrypted_data, tag)
        return decrypted_data
    

    def get_type(self) -> str:
        return 'aes'


class HybridEncryption(Encryption):


    def __init__(self) -> None:
        super().__init__()
        
        self.sym_encryption = SymetricEncryption()
        private_key_file = os.path.join(self.keys_path, 'key.pem')
        if os.path.exists(private_key_file):
            self.rsa_key = RSA.import_key(open(private_key_file).read())
        else:
            random_generator = Random.new().read
            self.rsa_key = RSA.generate(1024, random_generator)
            with open(private_key_file, 'wb') as file:
                file.write(self.rsa_key.export_key('PEM'))
        

    def encrypt(self, data: bytes) -> Tuple[bytes, bytes]:
        encrypted_data, sym_key = self.sym_encryption.encrypt(data)
        encrypted_key = PKCS1_OAEP.new(self.rsa_key).encrypt(sym_key)
        return encrypted_data, encrypted_key
    

    def decrypt(self, encrypted_data: bytes, encrypted_key: bytes) -> bytes:
        symetric_key = PKCS1_OAEP.new(self.rsa_key).decrypt(encrypted_key)
        decrypted_data = self.sym_encryption.decrypt(encrypted_data, symetric_key)
        return decrypted_data
    

    def get_type(self) -> str:
        return 'rsa'