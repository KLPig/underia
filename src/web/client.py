import socket


class Client:
    def __init__(self, addr, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((addr, port))
