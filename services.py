from cryptography.fernet import Fernet
from dotenv import dotenv_values
import re
import curses
import hashlib
import os


class AESService():

    @staticmethod
    def generate_secret_key():
        return Fernet.generate_key().decode()

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
    def add_entry(description: str, login: str, password: str) -> None:
        try:
            if '=' in description:
                return False, "You can't use '=' in description!"
            if len(description) > 32:
                return False, "Description to broad - the max is 60 characters!"
            encrypted_data = AESService.encrypt(f"USERNAME: {login}, PASSWD: {password}").decode()
            entry = f"{description.capitalize()}={encrypted_data}\n"
            with open(".entries", "a+") as f:
                f.write(entry)
            return True, "Entry added!!!"
        except Exception as e:
            return False, e

    @staticmethod 
    def get_entry(entry_row: str) -> str:
        pattern = r'^([^=]+)=(.*)'
        results = re.match(pattern, entry_row)
        description = results.group(1)
        encrypted_data = results.group(2)
        return description, encrypted_data

    @classmethod
    def get_all_entries_descriptions(cls):
        with open(".entries", "r") as f:
            lines = f.readlines()
        return [item[0] for item in map(cls.get_entry, lines)]


class ConfigFileServices():

    @staticmethod
    def save_in_config_file(variable_name: str, value: str) -> str:
        with open(".env", "a+") as env_file:
            # encrypted_data = AESService.encrypt(value).decode()
            env_file.write(f"{variable_name}={value}\n")
        return f"Variable {variable_name} successfully saved in .env file!"


class InputService():

    @staticmethod
    def get_input_from_user(stdscr, x=1, y=0, msg="Enter your text:", show_input=True):
        height, width = stdscr.getmaxyx()
        input_window = curses.newwin(x, width, height - x, y)
        input_window.addstr(0, 0, msg)
        input_window.refresh()

        user_input = ""
        while True:
            key = input_window.getch()
            if key == 10:
                # ENTER PRESSED
                return user_input
            elif key == 127:
                # BACKSPACE PRESSED
                user_input = user_input[:-1]
            else:
                user_input += chr(key)
            input_window.clear()
            if show_input:
                input_window.addstr(0, 0, msg + user_input)
            else:
                input_window.addstr(0, 0, msg + len(user_input)*'*')
            input_window.refresh()


class LogInService():

    def create_master_password(stdscr):
        height, width = stdscr.getmaxyx()
        while True:
            msg="Set MASTER PASSWROD and press [ENTER]\n\t\t"
            password1 = InputService.get_input_from_user(stdscr, 
                                                         x=int(height/2), 
                                                         y=int(width/2) - int(len(msg)/2), 
                                                         msg=msg, show_input=False)
            msg="Retype MASTER MASSWORD and press [ENTER]\n\t\t"
            password2 = InputService.get_input_from_user(stdscr, 
                                                         x=int(height/2), 
                                                         y=int(width/2) - int(len(msg)/2), 
                                                         msg=msg, show_input=False)
            if password1 and password1 == password2:
                salt = HasherService().get_salt()
                salted_password = password1 + salt.hex()
                hash = HasherService().hash_data(salted_password.encode())
                aes_key = AESService.generate_secret_key()
                ConfigFileServices.save_in_config_file("SALT", salt)
                ConfigFileServices.save_in_config_file("SECRET_KEY", aes_key)
                ConfigFileServices.save_in_config_file("MASTER_PASSWORD", hash)

    def user_authenticated(password):
        salt = HasherService().get_salt()
        salted_password = password + salt
        hash = HasherService().hash_data(salted_password.encode)
        return hash == dotenv_values(".env").get("MASTER_PASSWORD")
        

    @classmethod
    def authenticate_user(cls, stdscr):
        height, width = stdscr.getmaxyx()
        while True:
            master_password = dotenv_values(".env").get("MASTER_PASSWORD")
            if master_password:
                msg=f"Enter MASTER PASSWROD and press [ENTER]\n\t\t"
                user_input = InputService.get_input_from_user(stdscr, 
                                                            x=int(height/2), 
                                                            y=int(width/2) - int(len(msg)/2),
                                                            msg=msg, show_input=False)
                return cls.user_authenticated(user_input)
            else:
                cls.create_master_password(stdscr)


    @staticmethod
    def password_correct(passwrod):
        hash, _ = HasherService().hash_data(passwrod)
        master_password = dotenv_values(".env").get("MASTER_PASSWORD")
        return hash, master_password


class HasherService():

    @classmethod
    def hash_data(cls, value):
        hash_obj = hashlib.sha256(value)
        return hash_obj.hexdigest()

    @classmethod
    def get_salt(cls) -> bytes:
        salt = dotenv_values(".env").get("SALT")
        return salt.encode() if salt else os.urandom(16)
