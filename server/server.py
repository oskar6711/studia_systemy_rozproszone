import socket
from server_thread import ServerThread

LOCALHOST = '127.0.0.1'
PORT = 6666

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))

print('Serwer uruchomiony')
print('Oczekiwanie na klienta..')

while True:
    server.listen(5)
    client_socket, client_address = server.accept()
    thread = ServerThread(client_address, client_socket)
    thread.start()
