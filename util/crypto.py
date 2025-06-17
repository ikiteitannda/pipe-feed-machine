# -*- coding: utf-8 -*-
"""

AES 加密/解密密码工具

修改人： hnchen
修改时间： 2025/06/17
"""
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# === AES 加解密工具 ===
_KEY = b"AAAEE56789ABCDEF0123453289ABCDEF"  # 32 字节密钥
_BLOCK = AES.block_size  # 16

def pad(data: bytes) -> bytes:
    """PKCS7 填充"""
    pad_len = _BLOCK - (len(data) % _BLOCK)
    return data + bytes([pad_len] * pad_len)

def unpad(data: bytes) -> bytes:
    n = data[-1]
    return data[:-n]

def encrypt(plain: str) -> str:
    """返回 Base64( iv + ciphertext )"""
    try:
        raw = pad(plain.encode('utf-8'))
        iv = get_random_bytes(_BLOCK)
        cipher = AES.new(_KEY, AES.MODE_CBC, iv)
        ct = cipher.encrypt(raw)
        return base64.b64encode(iv + ct).decode('utf-8')
    except:
        return ''

def decrypt(token: str) -> str:
    """从 Base64( iv + ciphertext ) 解出明文"""
    try:
        data = base64.b64decode(token)
        iv, ct = data[:_BLOCK], data[_BLOCK:]
        cipher = AES.new(_KEY, AES.MODE_CBC, iv)
        raw = cipher.decrypt(ct)
        return unpad(raw).decode('utf-8')
    except:
        return ''