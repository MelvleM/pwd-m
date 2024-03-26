# Password Manager
# Li Wang
# 20/03/2024

# TODO Add exit in function add password and change password

from cryptography.fernet import Fernet
import sqlite3
from typing import Tuple, Union, Optional


class Sql_Database():
    def connect_database_passwords(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        with sqlite3.connect("password_manager.db") as conn:
            cursor = conn.cursor()
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                platform TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL)
                """)
            return conn, cursor


class Password_Encryptor():
    def __init__(self) -> None:
        self.encryption_key = self.get_key()

     # Read key from key.txt file
    def read_key_from_file(self) -> Union[bytes, None]:
        # Try to read key.txt file, return key value
        try:
            with open('key.txt', 'rb') as f:
                key = f.read()
        # key.txt doesn't exist, retun None
        except FileNotFoundError:
            key = None
        return key

    # Write Key to key.txt file
    def write_key_to_file(self, key: str) -> None:
        with open('key.txt', 'wb') as file:
            file.write(key)

    # Get key, read from file. if no key exists, then generate a new key and write it to file.
    def get_key(self) -> bytes:
        key = self.read_key_from_file()
        # If key is not existing, then create a new one and write it to file
        if key is None:
            key = Fernet.generate_key()
            self.write_key_to_file(key)
            print(type(key))
        return key

    # Encrypte password
    def encrypt_password(self, password: str) -> str:
        f = Fernet(self.encryption_key)
        return f.encrypt(password.encode())

    # Decrypt password
    def decrypt_password(self, encrypted_password: str) -> str:
        f = Fernet(self.encryption_key)
        return f.decrypt(encrypted_password).decode()


class Password_Manager():
    def __init__(self) -> None:
        self.conn, self.cursor = Sql_Database().connect_database_passwords()
        self.encryptor = Password_Encryptor()

    # Add platform, username, encrypted password to database
    def add_password(self) -> None:
        platform = input("Please enter your platform: ").lower()
        username = input("Please enter your username: ")
        password = input("Please enter your password: ")

        encrypted_password = self.encryptor.encrypt_password(password)

        self.cursor.execute(
            f"SELECT * FROM passwords WHERE platform = '{platform}' AND username = '{username}'")
        data = self.cursor.fetchall()
        if data:
            print("Data already exists")

        else:
            self.cursor.execute(
                f"INSERT INTO passwords (platform, username, password) VALUES(?,?,?)", (platform, username, encrypted_password))
            self.conn.commit()
            print(
                f"Password added successfully\nPlatform: {platform}\nUsername: {username}\nEncrypted Password: {encrypted_password.decode()}")

    def select_form_list(self, data: list, type: str, message: str) -> Optional[str]:
        if len(data) == 0:
            print(message)
            return None

        elif len(data) == 1:
            return data[0][0]

        else:
            for num, item in enumerate(data, start=1):
                print(f"{num}. {item[0]}")
            try:
                index = int(
                    input(f"Please enter the number of {type} you want to change password: ")) - 1
                return data[index][0]
            except Exception:
                print("Invalid choice. Please enter a valid number")
                self.change_password()

    def select_platform(self) -> str:
        self.cursor.execute(
            "SELECT platform FROM passwords")
        data_platform = self.cursor.fetchall()
        print(data_platform)
        return self.select_form_list(data_platform, type="platform", message="No platforms found in the database. Please add a new password by selecting option 2.")

    def select_username(self, platform: str) -> str:
        self.cursor.execute(
            "SELECT username FROM passwords WHERE platform = ?", (platform,))
        data_username = self.cursor.fetchall()
        return self.select_form_list(data_username, type="username", message="No username found in the database. Please add a new password by selecting option 2.")

    def change_password(self) -> None:
        platform = self.select_platform()
        if platform == None:
            return

        username = self.select_username(platform)

        print(f"Platform: {platform}\nUername: {username}")
        new_password = input("Please enter the new password: ")
        encrypted_new_password = self.encryptor.encrypt_password(new_password)
        self.cursor.execute("UPDATE passwords SET password = ? WHERE platform = ? AND username = ?",
                            (encrypted_new_password, platform, username))
        self.conn.commit()
        print("-"*50)
        print(
            f"Password changed successfully\nPlatform: {platform}\nUsername: {username}\nNew Encrypted Password: {encrypted_new_password.decode()}")

    def my_password(self) -> None:
        self.cursor.execute(f"SELECT * FROM passwords")
        data = self.cursor.fetchall()
        if data:
            print(
                f"| {'Index':^10} | {'Platform':^25} | {'Username':^25} | {'Password':^25} |")
            for index, platform, username, encrypted_password in data:
                password = self.encryptor.decrypt_password(encrypted_password)
                print(
                    f"| {index:^10} | {platform:^25} | {username:^25} | {password:^25} |")

        else:
            print(
                "No data found in the database. Please add a new password by selecting option 2.")


def menu() -> None:
    while True:
        print("-"*50)
        print("1. View passwords\n2. Add Password\n3. Change Password\n4. Exit")
        choice = input("Please Enter your choice: ")
        manager = Password_Manager()
        match choice:
            case "1":
                print("My Passwords:")
                print('-' * 98)
                manager.my_password()
                print('-' * 98)

            case "2":
                print("-"*50)
                manager.add_password()

            case "3":
                print("-"*50)
                manager.change_password()

            case  "4":
                break

            case _:
                print("Invalid choice")


if __name__ == "__main__":
    menu()
