"""The utilities file for the API"""

import zlib
import base64
import json

def compress_data(dict_data):
    """Compresses the data using zlib and base64. Returns a string."""
    json_data = json.dumps(dict_data)
    compressed_data = zlib.compress(json_data.encode("utf-8"))
    encoded_data = base64.b64encode(compressed_data)
    return encoded_data.decode("utf-8")

def decompress_data(encoded_data):
    """Decompresses the data using zlib and base64. Returns a dictionary."""
    decoded_data = base64.b64decode(encoded_data)
    decompressed_data = zlib.decompress(decoded_data)
    json_data = decompressed_data.decode("utf-8")
    dict_data = json.loads(json_data)
    return dict_data