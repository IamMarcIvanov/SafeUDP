import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('127.0.0.1', 12345))

RECV_BUFFER = 4096
while True:
    data, addr = server_socket.recvfrom(RECV_BUFFER)
    print(str(data))
    if str(data) == 'Exit':
        break
    msg = bytes('Hello this is UDP server'.encode('utf-8'))
    server_socket.sendto(msg, addr)
server_socket.close()