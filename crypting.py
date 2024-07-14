from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
import os

def generate_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    with open("private.pem", "wb") as priv_file:
        priv_file.write(private_key)

    public_key = key.publickey().export_key()
    with open("public.pem", "wb") as pub_file:
        pub_file.write(public_key)

def encrypt(source_path, dest_path):
    try:
        with open(source_path, 'rb') as enc_file:
            data_enc = enc_file.read()

        if os.path.isfile('public.pem'):
            public_rsa = RSA.import_key(open('public.pem').read())
            session_key = get_random_bytes(16)

            chips_rsa = PKCS1_OAEP.new(public_rsa)
            enc_session_key = chips_rsa.encrypt(session_key)

            chips_aes = AES.new(session_key, AES.MODE_EAX)
            chips_text, tag = chips_aes.encrypt_and_digest(data_enc)

            with open(dest_path, 'wb') as file_out:
                for x in (enc_session_key, chips_aes.nonce, tag, chips_text):
                    file_out.write(x)
            print(f'{source_path} зашифрован')
            os.remove(source_path)
            return True
        else:
            print("Нет публичного ключа для шифрования. Сгенерируйте ключи.")
            return False
    except Exception as e:
        print(f"Ошибка при шифровании: {str(e)}")
        return False

def decrypt(source_path, dest_path):
    try:
        if os.path.isfile("private.pem"):
            priv_key_rsa = RSA.import_key(open("private.pem").read())
            with open(source_path, "rb") as file_in:
                enc_session_key, nonce, tag, chips_text = [file_in.read(x) for x in (priv_key_rsa.size_in_bytes(), 16, 16, -1)]

            chips_rsa = PKCS1_OAEP.new(priv_key_rsa)
            session_key = chips_rsa.decrypt(enc_session_key)

            chips_aes = AES.new(session_key, AES.MODE_EAX, nonce)
            data = chips_aes.decrypt_and_verify(chips_text, tag)
            with open(dest_path, "wb") as file_out:
                file_out.write(data)
            print(f'{source_path} дешифрован')
            return True
        else:
            print('Нет приватного ключа для дешифровки. Скопируйте ключ "private.pem" в папку со скриптом!')
            return False
    except Exception as e:
        print(f"Ошибка при дешифровании: {str(e)}")
        return False
