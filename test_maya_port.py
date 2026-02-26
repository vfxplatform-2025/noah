#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Maya command port connection
"""

import socket

def test_connection(host='localhost', port=4434):
    """Test if Maya command port is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        sock.connect((host, port))
        
        # Send simple command
        test_cmd = 'print("Connection successful")'
        sock.send(test_cmd.encode('utf-8'))
        
        # Receive response
        data = sock.recv(1024)
        response = data.decode('utf-8')
        
        sock.close()
        return True, response
    except Exception as e:
        return False, str(e)

# Test connection
success, result = test_connection()
if success:
    print("Maya command port is accessible")
    print("Response:", result)
else:
    print("Failed to connect to Maya command port")
    print("Error:", result)