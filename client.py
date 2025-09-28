
import subprocess
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import nanoid
import requests

SERVER_URL = "https://client-challenge:8400"
SERVER_IP = "47.243.182.216"
SALT = "oursalt"
KEY_PURPOSE = "encryption_key"



def get_temp_code():
    temp_code = open("tempcode.dat", "r").read().split("\n")
    return temp_code

def bget_temp_code():
    temp_code = open("tempcode.dat", "r").read().split("\n")[0].encode()
    return temp_code.ljust(12, b"\x00")[:12]


def get_local_ip()-> str:
    result = subprocess.run(
        ["curl", "-s", "ifconfig.me"],
        capture_output=True,
        text=True
    )
    local_ip = result.stdout.strip()
    return local_ip

def get_client_id() -> str:
    client_id = nanoid.generate(size=21)   
    return client_id 


def gen_client_info(client_id: str):
    nonce = bget_temp_code()
    client_ip = get_local_ip()
    ikm = f"{client_ip}|{SERVER_IP}|{nonce}".encode() 
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT.encode(),
        info=KEY_PURPOSE.encode()
    )
    key = hkdf.derive(ikm)
    aes = AESGCM(key)
    ecid = aes.encrypt(nonce, client_id.encode(), associated_data=None)
    ecip = aes.encrypt(nonce, client_ip.encode(), associated_data=None)
    ecid_b64 = base64.b64encode(ecid).decode()  
    ecip_b64 = base64.b64encode(ecip).decode()
    return ecid_b64, ecip_b64


def get_challenge():
    client_id = get_client_id()
    ecid_b64, ecip_b64  = gen_client_info(client_id)

    resp = requests.post(
        f"{SERVER_URL}/get-challenge", 
        json={"ecid_b64":ecid_b64, "ecip_b64":ecip_b64}, 
        verify=False
    )
    resp.raise_for_status()
    return resp.json()




# import os, platform, hashlib, requests, hmac, hashlib, base64, time
# from cryptography import x509
# from cryptography.x509.oid import NameOID
# from cryptography.hazmat.primitives import serialization, hashes
# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.backends import default_backend


# CLIENT_ID = "client01"
# SECRET_KEY = b"supersecretkey"
# VERIFY_SSL = False


# def generate_cert(client_id, machine_id):
#     key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
#     cn = f"{client_id}-{hashlib.sha256(machine_id.encode()).hexdigest()}"
#     subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
#     cert = (
#         x509.CertificateBuilder()
#         .subject_name(subject)
#         .issuer_name(issuer)
#         .public_key(key.public_key())
#         .serial_number(x509.random_serial_number())
#         .not_valid_before(x509.datetime.datetime.utcnow())
#         .not_valid_after(x509.datetime.datetime.utcnow() + x509.datetime.timedelta(days=365))
#         .sign(key, hashes.SHA256(), default_backend())
#     )
#     cert_pem = cert.public_bytes(serialization.Encoding.PEM)
#     key_pem = key.private_bytes(serialization.Encoding.PEM,
#                                 serialization.PrivateFormat.TraditionalOpenSSL,
#                                 serialization.NoEncryption())
#     return key_pem, cert_pem, cn

# def sign_challenge(client_id, token, ts, machine_id):
#     msg = f"{client_id}|{token}|{ts}|{machine_id}".encode()
#     return hmac.new(SECRET_KEY, msg, hashlib.sha256).hexdigest()

# def register_cert(client_id, cert_pem, challenge, machine_id):
#     token = challenge['token']
#     ts = challenge['ts']
#     sig = sign_challenge(client_id, token, ts, machine_id)
#     payload = {
#         "client_id": client_id,
#         "cert": base64.b64encode(cert_pem).decode(),
#         "token": token,
#         "ts": ts,
#         "sig": sig,
#         "machine_id": machine_id
#     }
#     resp = requests.post(f"{SERVER_URL}/register-cert", json=payload, verify=VERIFY_SSL)
#     resp.raise_for_status()
#     return resp.json()

# if __name__ == "__main__":
#     machine_id = get_machine_fingerprint()
#     key_pem, cert_pem, cn = generate_cert(CLIENT_ID, machine_id)
#     challenge = get_challenge(CLIENT_ID)
#     result = register_cert(CLIENT_ID, cert_pem, challenge, machine_id)
#     print("注册结果:", result)
#     with open("client.key", "wb") as f: f.write(key_pem)
#     with open("client.crt", "wb") as f: f.write(cert_pem)
#     print("证书和私钥已保存，本地使用 mTLS 调用 /secure")
