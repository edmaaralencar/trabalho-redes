import socket
import threading
from utils import (PORT, IP, BUFFER_SIZE, headers, get_message, get_window_size, get_ack)
from datetime import datetime
import traceback

class Client:
    def __init__(self):
        self.nickname = input("Escolha seu apelido: ")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.isActive = True
        self.client.connect((IP, PORT))

        self.last_ack_received = 0
        self.sequence_number = 0
        self.window_size = 5
        self.sequence_number_lock = threading.Lock()

        write_message_thread = threading.Thread(target=self.write)
        write_message_thread.start()

        receive_message_thread = threading.Thread(target=self.receive)
        receive_message_thread.start()

    def receive(self):
        while self.isActive:
            try:
                data = self.client.recv(BUFFER_SIZE)
                message = get_message(data)
                self.window_size = get_window_size(data)
                self.last_ack_received = get_ack(data)
                if message == 'NICK':
                    self.client.send(headers({"message": self.nickname}))
                else:
                    print(f"\n(Mensagem) {message}\n")
            except:
                print("Ocorreu um erro!")
                print(traceback.print_exc())
                self.client.close()
                break

    def write(self):
        while self.isActive:
            try:
                mode = input("Digite '1' para enviar um pacote isolado ou '2' para enviar um lote: ").strip()
                if mode == '1':
                    self.send_single_packet()
                elif mode == '2':
                    self.send_batch()
                else:
                    print("Opção inválida. Tente novamente.")

            except Exception as e:
                print("Ocorreu um erro:", e)
                traceback.print_exc()

    def send_single_packet(self):
        if self.sequence_number - self.last_ack_received < self.window_size:
            input_message = input('Mensagem: ')
            if input_message.lower() == 'sair':
                print("Conexão encerrada.")
                with self.sequence_number_lock:
                    self.sequence_number += 1

                data = {"sequence_number": self.sequence_number, "message": "sair"}

                self.client.send(headers(data))
                # self.client.close()
                # self.isActive = False
                return

            message = f"{self.nickname}: {input_message}"
            with self.sequence_number_lock:
                self.sequence_number += 1
            data = {"sequence_number": self.sequence_number, "message": message}
            self.client.send(headers(data))

    def send_batch(self):
        batch_size = int(input("Digite o tamanho do lote: "))
        for _ in range(batch_size):
            self.send_single_packet()

if __name__ == '__main__':
    client = Client()
