import hashlib


class SignatureFactory(type):

    signers = {}
    
    def __new__(cls, classname, parents, attributes):
        if '__call__' not in attributes:
            raise Exception(f'Signer class {classname} must implement function "__call__"')

        signer_class = type(classname, parents, attributes)
        if 'label' not in attributes:
            signer_class.label = classname

        SignatureFactory.signers[signer_class.label] = signer_class
        return signer_class

    @staticmethod
    def get_signer(label: str):
        return SignatureFactory.signers.get(label)

class Md5Signer(metaclass=SignatureFactory):

    label = 'md5'
    def __call__(self, string_data: str) -> str:
        return hashlib.md5(string_data.encode()).hexdigest()


class Sha512Signer(metaclass=SignatureFactory):

    label = 'sha512'
    def __call__(self, string_data: str) -> str:
        return hashlib.sha512(string_data.encode()).hexdigest()
