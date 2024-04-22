import socket
import threading
from utils import (PORT, IP, BUFFER_SIZE, compute_checksum, headers, get_message,
                   get_checksum, get_window_size, get_ack)
from datetime import datetime
import traceback
import json

class Client:
    def __init__(self):
        self.running = True
        self.nickname = input("Escolha seu apelido: ")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((IP, PORT))

        self.sequence_number = 0
        self.sequence_number_lock = threading.Lock()
        self.window_size = 5
        self.last_ack_received = 0

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        write_thread = threading.Thread(target=self.write)
        write_thread.start()

    def increment_sequence_number(self):
        with self.sequence_number_lock:
            self.sequence_number += 1

    def receive(self):
        while self.running:
            try:
                data = self.client.recv(BUFFER_SIZE)
                message = get_message(data)
                self.window_size = get_window_size(data)
                self.last_ack_received = get_ack(data)
                if message == 'NICK':
                    self.client.send(headers({"message": self.nickname}))
                else:
                    print(f"\n{datetime.now().strftime('%H:%M')} {message}\n")
            except:
                print("Ocorreu um erro!")
                self.client.close()
                break

    def write(self):
        while self.running:
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
            if input_message == 'Sair':
                self.client.close()
                print("Conexão encerrada.")

            message = f"{self.nickname}: {input_message}"
            self.increment_sequence_number()
            data = {"sequence_number": self.sequence_number, "message": message}
            json = headers(data)
            self.client.send(json)

    def send_batch(self):
        batch_size = int(input("Digite o tamanho do lote: "))
        for _ in range(batch_size):
            self.send_single_packet()

if __name__ == '__main__':
    client = Client()
