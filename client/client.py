import socket

SERVER = "127.0.0.1"
PORT = 6666

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
print('Polaczono!')

while True:
    server_message = client.recv(1024)
    print('Wiadomosc z serwera:', server_message.decode())
    client_message = str(input())
    client.sendall(bytes(client_message, 'UTF-8'))
    if client_message == '' or client_message == 'wyjdz':
        break
client.close()
print('Rozlaczono z serwerem.')
