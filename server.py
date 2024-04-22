import socket
import threading
from utils import (PORT, IP, BUFFER_SIZE, compute_checksum, headers, get_message, get_checksum, unpack_data, get_sequence_number)
import traceback
import time

class ChatServer:
    user_list = []
    client_connections = []
    sequence_numbers = []
    
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((IP, PORT))
        self.server_socket.listen()

        self.acknowledgements = {}
        self.message_timeout = 30
        self.window_size = 5
        self.nack_messages = {}

        self.window_lock = threading.Lock()
        self.sequence_lock = threading.Lock()

        self.receive_messages()

    def send_to_all(self, data):
        try:
            for connection in self.client_connections:
                connection.send(data)
            with self.window_lock:
                self.window_size += 1
        except:
            print(traceback.print_exc())

    def handle_messages(self, connection):
        while True:
            try:
                data = connection.recv(BUFFER_SIZE)
                received_checksum = get_checksum(data)
                message = get_message(data)
                received_sequence = get_sequence_number(data)
                with self.window_lock:
                    self.window_size -= 1

                index = self.client_connections.index(connection)
                with self.sequence_lock:
                    current_sequence = self.sequence_numbers[index]
                    current_sequence += 1
                    self.sequence_numbers[index] = current_sequence

                client_ack = self.sequence_numbers[index] + 1

                if received_checksum == compute_checksum(message):
                    if self.sequence_numbers[index] == received_sequence:
                        force_error = False
                        unpacked_data = unpack_data(data)
                        unpacked_data['window_size'] = self.window_size
                        # window_
                        unpacked_data['ack'] = client_ack
                        data = headers(unpacked_data)
                        self.nack_messages[message] = (connection, data)
                        if "TIMEOUTERROR" in message:
                            force_error = True
                        acknowledgment_timer = threading.Thread(target=self.timer, args=(connection, data, force_error))
                        acknowledgment_timer.start()
                        self.send_to_all(data)
                    else:
                        print("Número de sequência incorreto.")
                else:
                    print("Soma de verificação inválida.")
            except:
                print("Ocorreu um erro:")
                print(traceback.print_exc())
                self.remove_connection(connection)
                break

    def timer(self, _, data, force_error):
        time.sleep(self.message_timeout)
        if not self.ack_ok(data) or force_error:
            print("Timeout. Tentando novamente...")
            self.send_to_all(data)

    def ack_ok(self, data):
        message = get_message(data)
        if message in self.nack_messages:
            del self.nack_messages[message]
            return True
        return False

    def receive_messages(self):
        while True:
            connection, address = self.server_socket.accept()
            print("Conexão estabelecida com {}".format(str(address)))

            connection.send(headers({"message": "NICK", "window_size": self.window_size, "ack": 1}))
            data = connection.recv(BUFFER_SIZE)
            received_checksum = get_checksum(data)
            nickname = get_message(data)
            if received_checksum != compute_checksum(nickname):
                print("Erro ao enviar o apelido.")
            else:
                self.user_list.append(nickname)
                self.client_connections.append(connection)
                self.sequence_numbers.append(0)
                print(f"{nickname} conectado ao servidor.")
                connection.send(headers({"message": f"Bem-vindo {nickname}!", "window_size": self.window_size, "ack": 1}))
                self.send_to_all(headers({"message": f"{nickname} entrou no chat!\n", "window_size": self.window_size, "ack": 1}))
                thread = threading.Thread(target=self.handle_messages, args=(connection,))
                thread.start()

    def remove_connection(self, connection):
        index = self.client_connections.index(connection)
        self.client_connections.remove(connection)
        connection.close()
        nickname = self.user_list[index]
        self.send_to_all(headers({"message": f"{nickname} saiu.", "window_size": self.window_size, "ack": 100}))
        self.user_list.remove(nickname)

if __name__ == '__main__':
    server = ChatServer()
