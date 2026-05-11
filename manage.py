# -*- coding: utf-8 -*-
import json
import os
import io
from Crypto.Cipher import AES
from Crypto.Util import Padding

PWD2 = b'v-2-v-4-v-8-v-16'
PWD3 = b'8-16-32-64-128-0'

def encrypt_data(data):
    cipher = AES.new(PWD2, AES.MODE_CBC, PWD3)
    encoded = data.encode('utf-16le')
    padded = Padding.pad(encoded, AES.block_size)
    return cipher.encrypt(padded)

def generate():
    if not os.path.exists('users.json'):
        print("Error: users.json not found")
        return
        
    with io.open('users.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        users = data.get('users', [])
        
    lines = []
    for user in users:
        # ID|名稱|到期日
        line = u"{}|{}|{}".format(user.get('id', ''), user.get('name', ''), user.get('expire', ''))
        lines.append(line)
    
    full_text = u"\n".join(lines)
    encrypted = encrypt_data(full_text)
    
    if not os.path.exists('Reliable'):
        os.makedirs('Reliable')
        
    with open('Reliable/Reversible', 'wb') as f:
        f.write(encrypted)
    
    print("Generated: {} bytes".format(len(encrypted)))

if __name__ == "__main__":
    generate()