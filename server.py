import socket
from utils import IP, PORT, headers, get_message, get_checksum, compute_checksum
import traceback
import threading

class Server:
  nicknames = []
  clients = []
  sequence_numbers = []

  def __init__(self):
    self.server = socket.socket()
    self.server.bind((IP, PORT))
    self.server.listen()

    self.acknowledgements = {}
    self.window_size = 5

    self.window_size_lock = threading.Lock()
    self.sequence_number_lock = threading.Lock()

    self.receive()

  def increment_window_size(self):
    with self.window_size_lock:
        self.window_size += 1

  def broadcast(self, data):
    try:
      for client in self.clients:
          client.send(data)
      self.increment_window_size()
    except:
      print(traceback.print_exc())

  def receive(self):
     while True:
        conn, address = self.server.accept()
        print("Conectado com {}".format(str(address)))

        conn.send(headers({"message": "name", "window_size": self.window_size, "ack": 1}))
        data = conn.recv(1024)

        received_checksum = get_checksum(data)
        user = get_message(data)

        if received_checksum != compute_checksum(user):
          print("Ocorreu um erro no envio do apelido.")
        else:
          self.nicknames.append(user)
          self.clients.append(conn)
          self.sequence_numbers.append(0)

          print(f"{user} conectou.")

          conn.send(headers({"message": f"Bem-vindo {user}!", "window_size": self.window_size, "ack": 1}))
          print(self.window_size)
          self.broadcast(headers({"message": f"{user} entrou no chat!\n", "window_size": self.window_size, "ack": 1}))

# def server_program():
#     host = socket.gethostname()
#     port = 8000  # initiate port no above 1024

#     server_socket = socket.socket()  # get instance
#     server_socket.bind((host, port))  # bind host address and port together

#     # configure how many client the server can listen simultaneously
#     server_socket.listen(2)
#     conn, address = server_socket.accept()  # accept new connection
#     print("Connection from: " + str(address))
#     while True:
#         # receive data stream. it won't accept data packet greater than 1024 bytes
#         data = conn.recv(1024).decode()
#         if not data:
#             # if data is not received break
#             break
#         print("from connected user: " + str(data))
#         data = input(' -> ')
#         conn.send(data.encode())  # send data to the client

#     conn.close()  # close the connection

if __name__ == '__main__':
    server = Server()