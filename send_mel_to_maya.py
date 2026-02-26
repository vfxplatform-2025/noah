#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

def send_mel_file_to_maya(mel_file_path, host='localhost', port=4434):
    """Send MEL file to Maya via command port"""
    try:
        with open(mel_file_path, 'r') as f:
            mel_content = f.read()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        sock.send(mel_content.encode('utf-8'))
        
        # Receive response
        response = ""
        sock.settimeout(5)
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                response += data.decode('utf-8')
            except socket.timeout:
                break
        
        sock.close()
        return response
    except Exception as e:
        return "Error: " + str(e)

# Send the MEL script
result = send_mel_file_to_maya('query_maya.mel')
print(result)