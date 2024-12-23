from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_file(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    encrypted_data = cipher.encrypt(data)
    with open(file_path, 'wb') as f:
        f.write(encrypted_data)

def decrypt_file(file_path):
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = cipher.decrypt(encrypted_data)
    with open(file_path, 'wb') as f:
        f.write(decrypted_data)