import base64

def convert_byte_to_string(obj):
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    elif isinstance(obj, dict):
        return {k: convert_byte_to_string(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_byte_to_string(v) for v in obj]
    else:
        return obj