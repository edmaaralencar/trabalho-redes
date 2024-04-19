import socket
import json

PORT = 8900
IP = socket.gethostname()
BUFFER_SIZE = 1024

def compute_checksum(data):
    checksum = 0
    try:
        data = data.decode("ascii")
    except AttributeError:
        pass
    for char in data:
        checksum ^= ord(char)
    return checksum

def  headers(data):
    data['checksum'] = compute_checksum(data['message'])
    json_data = json.dumps(data).encode('ascii')
    return json_data

def unpack_data(data):
    data = data.decode('ascii')
    data_json = json.loads(data)
    return data_json
    
def get_message(data):
    data_json = unpack_data(data)
    message = data_json['message']
    return message

def get_checksum(data):
    data_json = unpack_data(data)
    checksum = data_json['checksum']
    return int(checksum)

def get_sequence_number(data):
    data_json = unpack_data(data)
    sequence_number = data_json['sequence_number']
    return int(sequence_number)
