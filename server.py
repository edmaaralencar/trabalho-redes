import socket
import random

def verify_checksum(data, checksum):
    """Verifica se o checksum calculado dos dados recebidos corresponde ao checksum enviado."""
    byte_count = len(data)
    print(f"Número de bytes: {byte_count}")
    
    # garante que os dados tenham um número par de bytes para o calculo do checksum
    if byte_count % 2 == 1:
        data += b'\x00'
        byte_count += 1

    checksum_value = 0

    # calcula o checksum 
    for i in range(0, byte_count, 2):
        w = (data[i] << 8) + data[i + 1]
        checksum_value += w
        checksum_value = (checksum_value >> 16) + (checksum_value & 0xFFFF)

    checksum_value = ~checksum_value & 0xFFFF

    # compara o checksum calculado com o enviado
    return checksum_value == checksum

if __name__ == "__main__":
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 8080
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))

    print(f"Server listening on {HOST}:{PORT}")

    while True:
        # recebe o checksum e os dados do cliente 
        message, addr = server.recvfrom(2048)  # checksum e dados enviados juntos
        if len(message) < 2:
            continue  # evita processar mensagens que não tenham pelo menos 2 bytes para o checksum

        # separa o checksum dos dados
        checksum_bytes = message[:2]
        data = message[2:].decode('utf-8')

        print("Cliente: Usuário")

        checksum = int.from_bytes(checksum_bytes, byteorder="big")

        # simula a possibilidade de erro de integridade nos dados
        integrity_error = random.randint(0, 100)
        if integrity_error <= 25:
            print("Pacote contém erro de integridade.")
            server.sendto(b"ERRO", addr)
        else:
            if verify_checksum(data.encode("utf-8"), checksum):
                print("Checksum é válido.")
                data = data.upper()
                server.sendto(data.encode("utf-8"), addr)
            else:
                print("Checksum é inválido.")
                server.sendto(b"ERRO", addr)