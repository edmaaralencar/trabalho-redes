import socket as s

def checksum(data):
    # calcula o checksum dos dados enviados
    byte_count = len(data)
    if byte_count % 2 == 1:
        data += b'\x00'
    checksum_value = 0
    # itera sobre os dados em pares de bytes
    for i in range(0, len(data), 2):
        # combina dois bytes em uma palavra de 16 bits e adiciona ao valor do checksum
        w = (data[i] << 8) + data[i + 1]
        checksum_value += w
        # se houver overflow, adiciona a parte excedente ao valor do checksum
        checksum_value = (checksum_value >> 16) + (checksum_value & 0xFFFF)
    # complementa o valor do checksum e o trunca para 16 bits
    checksum_value = ~checksum_value & 0xFFFF
    return checksum_value

if __name__ == "__main__":
    # obtem o endereço IP do host local e define a porta
    HOST = s.gethostbyname(s.gethostname())
    PORT = 8080
    # cria um socket UDP
    client = s.socket(s.AF_INET, s.SOCK_DGRAM)
    addr = (HOST, PORT)

    while True:
        # solicitação de nome ao usuario 
        data = input("Escolha seu nome: ")
        if not data:
            break
        # codifica a palavra
        data = data.encode("utf-8")

        # solicitação do modo de envio 
        send_mode = input("Digite [1] para modo de envio isolado e [2] para modo de envio em lote: ")

        if send_mode == "1":
            # calcula o checksum da palavra e o converte em bytes
            checksum_value = checksum(data)
            checksum_bytes = checksum_value.to_bytes(2, byteorder="big")
            # cria o pacote adicionando o checksum aos dados
            packet = checksum_bytes + data
            # envia o pacote para o endereço especificado
            client.sendto(packet, addr)
        elif send_mode == "2":
            # cria uma lista para armazenar os pacotes
            packets = []
            while True:
                # solicita ao usuário uma nova palavra ou finaliza
                additional_data = input("Digite uma palavra. Caso queira finalizar, deixe a linha vazia: ")
                if not additional_data:
                    break
                # codifica a palavra adicional 
                additional_data = additional_data.encode("utf-8")
                # calcula o checksum da palavra adicional e o converte em bytes
                checksum_value = checksum(additional_data)
                checksum_bytes = checksum_value.to_bytes(2, byteorder="big")
                # adiciona o checksum aos dados e armazena o pacote na lista
                packets.append(checksum_bytes + additional_data)

            for packet in packets:
                # envia cada pacote para o seu endereço 
                client.sendto(packet, addr)
                # espera por uma resposta do servidor
                response, _ = client.recvfrom(1024)
                response = response.decode("utf-8")
                # verifica se a resposta apresenta erro
                if response == "ERRO":
                    print("Falha de integridade detectada.")
                else:
                    # exibe o comprimento da resposta
                    print(f"Comprimento da resposta: {len(response)}")
        else:
            # mensagem de erro 
            print("Modo de envio não reconhecido.")

    # fecha o socket do cliente 
    client.close()