import socket
import threading


class SocketServer:
    def __init__(self):
        self.port = 1145
        self.host = socket.gethostname()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print(f'Server started on {self.host}:{self.port}')

    def command_handler(self, recv_data: bytes) -> bytes:
        return f'Decoded {recv_data.decode()}'.encode()

    def socket_handle(self, conn):
        while True:
            recv = conn.recv(1024)
            response = self.command_handler(recv)
            conn.send(response)
            if not recv:
                break
        conn.close()

    def listen(self):
        conn, addr = self.sock.accept()
        threading.Thread(target=self.socket_handle, args=(conn,)).start()


if __name__ == '__main__':
    server = SocketServer()
    while True:
        server.listen()
