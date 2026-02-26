#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct Maya structure comparison via command port
"""

import socket

def send_maya_command(command, host='localhost', port=4434):
    """Send command to Maya via command port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect((host, port))
        
        # Send as MEL command
        sock.send(command.encode('utf-8'))
        
        # Receive response
        response = ""
        sock.settimeout(10)
        try:
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data.decode('utf-8')
        except socket.timeout:
            pass
        
        sock.close()
        return response.strip()
    except Exception as e:
        return "Error: " + str(e)

print("=== Direct Maya Hair Structure Comparison ===")

# Step 1: Check existence and get basic info
print("\n1. Object existence check:")
cmd1 = '''
print("=== EXISTENCE CHECK ===");
int $groupExists = `objExists "group"`;
int $refExists = `objExists "c0082ma_e200_kite:c0078ma_e200_romi_daily:root"`;
print("Group exists: " + $groupExists);
print("Reference exists: " + $refExists);
'''

result = send_maya_command(cmd1)
print(result)

# Step 2: Get detailed structure of group
print("\n2. Group structure analysis:")
cmd2 = '''
print("=== GROUP STRUCTURE ===");
if (`objExists "group"`) {
    string $groupChildren[] = `listRelatives -children "group"`;
    print("Group children count: " + size($groupChildren));
    for ($i = 0; $i < size($groupChildren); $i++) {
        string $child = $groupChildren[$i];
        string $childType = `nodeType $child`;
        print("  [" + $i + "] " + $child + " (type: " + $childType + ")");
        
        // Get grandchildren for first few items
        if ($i < 3) {
            string $grandChildren[] = `listRelatives -children $child`;
            if (size($grandChildren) > 0) {
                print("    - has " + size($grandChildren) + " children");
                for ($j = 0; $j < min(3, size($grandChildren)); $j++) {
                    print("      * " + $grandChildren[$j]);
                }
            }
        }
    }
} else {
    print("Group not found");
}
'''

result = send_maya_command(cmd2)
print(result)

# Step 3: Get detailed structure of reference
print("\n3. Reference structure analysis:")
cmd3 = '''
print("=== REFERENCE STRUCTURE ===");
string $refRoot = "c0082ma_e200_kite:c0078ma_e200_romi_daily:root";
if (`objExists $refRoot`) {
    string $refChildren[] = `listRelatives -children $refRoot`;
    print("Reference children count: " + size($refChildren));
    for ($i = 0; $i < size($refChildren); $i++) {
        string $child = $refChildren[$i];
        string $childType = `nodeType $child`;
        print("  [" + $i + "] " + $child + " (type: " + $childType + ")");
        
        // Get grandchildren for first few items
        if ($i < 3) {
            string $grandChildren[] = `listRelatives -children $child`;
            if (size($grandChildren) > 0) {
                print("    - has " + size($grandChildren) + " children");
                for ($j = 0; $j < min(3, size($grandChildren)); $j++) {
                    print("      * " + $grandChildren[$j]);
                }
            }
        }
    }
} else {
    print("Reference root not found");
}
'''

result = send_maya_command(cmd3)
print(result)

# Step 4: Compare hair-specific objects
print("\n4. Hair object comparison:")
cmd4 = '''
print("=== HAIR OBJECTS COMPARISON ===");

// Look for hair objects in group
print("Hair objects under group:");
string $groupHair[] = `ls -dag "group" -type "transform"`;
for ($obj in $groupHair) {
    if (`gmatch $obj "*hair*"`) {
        print("  GROUP: " + $obj);
    }
}

// Look for hair objects in reference
print("Hair objects under reference:");
string $refHair[] = `ls -dag "c0082ma_e200_kite:c0078ma_e200_romi_daily:root" -type "transform"`;
for ($obj in $refHair) {
    if (`gmatch $obj "*hair*"`) {
        print("  REF: " + $obj);
    }
}
'''

result = send_maya_command(cmd4)
print(result)

print("\n=== Comparison Complete ===")