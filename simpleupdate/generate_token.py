#!/usr/bin/env python3
import os
import secrets

import bcrypt

unencrypted = secrets.token_hex(int(os.getenv('LEN', '32')))
encrypted = bcrypt.hashpw(unencrypted.encode(), bcrypt.gensalt()).decode()

print()
print('unencrypted (send with curl): ', unencrypted)
print('encrypted (store in config):  ', encrypted)
print()
print('example curl command: ')
print(f'$ curl -d "{unencrypted}" -X POST https://simpleupdate/v0/namespace/deployment')
print()
