from web import game_pack_data
import socket
import threading
import pickle


class SocketServer:
    pack_data = game_pack_data.FirstConnectData()

    def __init__(self):
        self.port = 1145
        self.host = socket.gethostname()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print(f'Server started on {self.host}:{self.port}')

    @staticmethod
    def command_handler(recv_data: bytes) -> bytes:
        return f'Decoded {recv_data.decode()}'.encode()

    @staticmethod
    def socket_handle(conn: socket.socket):
        conn.send(pickle.dumps(SocketServer.pack_data))
        while True:
            recv = conn.recv(1024)
            response = SocketServer.command_handler(recv)
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
