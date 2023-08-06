from cryptography.fernet import Fernet
from dotenv import dotenv_values


def add_entry(description: str, uname: str, password: str) -> None:
    '''
    This method have to:
    1. get data from user
    2. encrypt data with AES algorythm
    3. save encrypted data in file
    '''
    pass


def encrypt(data: str) -> str:
    """
    Fernet is the AES in CBC mode

    AES:Advanced Encryption Standard
    CBC: Cipher Block Chaining
    """
    SECRET_KEY = dotenv_values(".env").get("SECRET_KEY")
    cipher = Fernet(SECRET_KEY)
    data_bytes = data.encode()
    encrypted_data = cipher.encrypt(data_bytes)
    print(encrypted_data)
    return encrypted_data


def decrypt(encrypted_data: str) -> str:
    SECRET_KEY = dotenv_values(".env").get("SECRET_KEY")
    cipher = Fernet(SECRET_KEY)
    decrypted_data = cipher.decrypt(encrypted_data)
    data = decrypted_data.decode()
    print(data)
    return data
