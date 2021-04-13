import socket

RECV_BUFFER = 4096

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

msg = bytes('Hello this is Client'.encode('utf-8'))
client_socket.sendto(msg, ('127.0.0.1', 12345))
data, addr = client_socket.recvfrom(RECV_BUFFER)
print(str(data))
msg = bytes('Exit'.encode('utf-8'))
client_socket.sendto(msg, ('127.0.0.1', 12345))
client_socket.close()