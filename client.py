import socket
import threading
from utils import IP, PORT, get_message, headers
from datetime import datetime
import traceback

class Client:
  def __init__(self):
    self.running = True
    self.nickname = input("Escolha seu nome: ")
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

  def receive(self): 
    while self.running:
      try:
        data = self.client.recv(1024)
        message = get_message(data)

        if message == 'name':
           self.client.send(headers({ "message": self.nickname }))
        else:
          print(f"{datetime.now().strftime('%H:%M')} {message}\n")
      except:
        print(traceback.print_exc())
        self.client.close()
        break
  
  def write(self):
    while self.running:
      try:
        if self.sequence_number - self.last_ack_received < self.window_size:
          message = '{}: {}'.format(self.nickname, input('> '))

          self.increment_sequence_number()
          
          data = {"sequence_number": self.sequence_number, "message": message}
          json_data = headers(data)
          
          self.client.send(json_data)
      except:
        print("Ocorreu um erro!")
        print(traceback.print_exc())

def client_program():
    host = socket.gethostname()  # as both code is running on same pc
    port = 8000  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    message = input(" -> ")  # take input

    while message.lower().strip() != 'bye':
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(1024).decode()  # receive response

        print('Received from server: ' + data)  # show in terminal

        message = input(" -> ")  # again take input

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client = Client()
