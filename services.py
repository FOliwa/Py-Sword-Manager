from cryptography.fernet import Fernet
from dotenv import dotenv_values
import re


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


class EntryFileServices():

    @staticmethod
    def add_entry(description: str, uname: str, password: str) -> None:
        try:
            if '=' in description:
                raise Exception("You can't use '=' in description!")
            if len(description) > 32:
                raise Exception("Description to broad - the max is 60 characters!")
            encrypted_data = AESService.encrypt(f"USERNAME: {uname}, PASSWD: {password}").decode()
            entry = f"{description.capitalize()}={encrypted_data}\n"
            with open(".entries", "a+") as f:
                f.write(entry)
        except Exception as e:
            return e

    @staticmethod 
    def get_entry(entry_row: str) -> str:
        pattern = r'^([^:]+):(.*)'
        results = re.match(pattern, entry_row)
        description = results.group(1)
        encrypted_data = results.group(2)
        return description, encrypted_data


class ConfigFileServices():

    @staticmethod
    def save_in_config_file(variable_name: str, value: str) -> str:
        with open(".env", "r") as env_file:
            variable_exist = any(map(lambda l: l.startswith(variable_name), env_file.readlines()))
        if variable_exist:
            return f"Variable {variable_name} already exist in .env file!"

        with open(".env", "a+") as env_file:
            encrypted_data = AESService.encrypt(value).decode()
            env_file.write(f"{variable_name}={encrypted_data}\n")
        return f"Variable {variable_name} successfully saved in .env file!"
    
    def set_master_password():
        pass
