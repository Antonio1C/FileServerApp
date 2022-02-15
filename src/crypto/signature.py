import hashlib


class SignLabelIsIncorrect(Exception):
    pass


class SignatureFactory(type):

    signers = {}
    
    def __new__(cls, classname, parents, attributes):
        if '__call__' not in attributes:
            raise Exception(f'Signer class {classname} must implement function "__call__"')

        signer_class = type(classname, parents, attributes)
        if 'label' not in attributes:
            signer_class.label = classname.lower()
        
        def get_sign_filename(self, filename: str) -> str:
            return f'{filename}.{self.label}'
        
        signer_class.get_sign_filename = get_sign_filename

        SignatureFactory.signers[signer_class.label] = signer_class()

        return signer_class

    @staticmethod
    def get_signer(label: str):
        signer = SignatureFactory.signers.get(label)
        if signer == None: raise SignLabelIsIncorrect(f"Didn't find signer by '{label}' label")
        return signer

class Md5Signer(metaclass=SignatureFactory):

    label = 'md5'
    def __call__(self, string_data: str) -> str:
        
        if isinstance(string_data, bytes):
            return hashlib.md5(string_data).hexdigest()
            
        return hashlib.md5(string_data.encode()).hexdigest()


class Sha512Signer(metaclass=SignatureFactory):

    label = 'sha512'
    def __call__(self, string_data: str) -> str:
        
        if isinstance(string_data, bytes):
            return hashlib.sha512(string_data).hexdigest()
            
        return hashlib.sha512(string_data.encode()).hexdigest()
