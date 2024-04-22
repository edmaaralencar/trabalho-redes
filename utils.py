PORT = 1233
IP = '127.0.0.1'
BUFFER_SIZE = 1024

import json

def calculate_checksum(data):
    checksum = 0
    try:
        data = data.decode("ascii")
    except AttributeError:
        pass
    for char in data:
        checksum ^= ord(char)
    return checksum

def headers(data):
    data['checksum'] = calculate_checksum(data['message'])
    json_data = json.dumps(data).encode('ascii')
    return json_data

def unpack_data(data):
    data = data.decode('ascii')
    json_data = json.loads(data)
    return json_data
    
def get_message(data):
    json_data = unpack_data(data)
    message = json_data['message']
    return message

def get_checksum(data):
    json_data = unpack_data(data)
    checksum = json_data['checksum']
    return int(checksum)

def get_sequence_number(data):
    json_data = unpack_data(data)
    sequence_number = json_data['sequence_number']
    return int(sequence_number)

def get_window_size(data):
    json_data = unpack_data(data)
    window_size = json_data['window_size']
    return int(window_size)

def get_ack(data):
    json_data = unpack_data(data)
    ack = json_data['ack']
    return int(ack)