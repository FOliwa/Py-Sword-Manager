from cryptography.fernet import Fernet
from dotenv import dotenv_values


class AESService():

    @staticmethod
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
        return encrypted_data

    @staticmethod
    def decrypt(encrypted_data: str) -> str:
        SECRET_KEY = dotenv_values(".env").get("SECRET_KEY")
        cipher = Fernet(SECRET_KEY)
        decrypted_data = cipher.decrypt(encrypted_data)
        data = decrypted_data.decode()
        return data
