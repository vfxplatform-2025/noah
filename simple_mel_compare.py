#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

def send_mel(mel_cmd, host='localhost', port=4434):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        sock.send(mel_cmd.encode('utf-8'))
        
        response = ""
        sock.settimeout(5)
        try:
            data = sock.recv(4096)
            if data:
                response = data.decode('utf-8')
        except socket.timeout:
            pass
        
        sock.close()
        return response.strip()
    except Exception as e:
        return "Error: " + str(e)

print("=== Simple MEL Structure Check ===")

# Check what's actually in group
print("\n1. Group 내용:")
result = send_mel('ls -dag "group";')
print("Group descendants:", result)

print("\n2. Reference 내용:")
result = send_mel('ls -dag "c0082ma_e200_kite:c0078ma_e200_romi_daily:root";')
print("Reference descendants:", result)

print("\n3. Hair objects in scene:")
result = send_mel('ls "*hair*";')
print("Hair objects:", result)

print("\n4. Unwanted objects check:")
unwanted = ['body_all', 'teeth', 'HairGeoGrp', 'dmm_GRP']
for obj in unwanted:
    result = send_mel('ls "*{}*";'.format(obj))
    if result and 'Error' not in result:
        print("{}: {}".format(obj, result))

print("\n=== Complete ===")