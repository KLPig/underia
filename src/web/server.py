from web import game_pack_data
from underia import game
import socket
import pickle
import asyncio


class SocketServer:

    def __init__(self):
        self.port = 1145
        self.host = socket.gethostname()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.player_count = 1
        self.players: dict[int, game_pack_data.SinglePlayerData] = {0: game_pack_data.SinglePlayerData(0, game.get_game().player)}

    def command_handler(self, recv_data: bytes) -> bytes:
        data = pickle.loads(recv_data)
        if type(data) is game_pack_data.SinglePlayerData:
            self.players[data.player_id] = data
            return pickle.dumps(('player', self.players))
        return b'gotten'

    async def send_displays(self, client: socket.socket):
        loop = asyncio.get_event_loop()
        print(self.host, self.port)
        while True:
            await loop.sock_sendall(client, pickle.dumps(('display', game_pack_data.EntityDisplays())))
            await asyncio.sleep(0.06)

    async def socket_handle(self, client: socket.socket):
        loop = asyncio.get_event_loop()
        print(self.host, self.port)
        pack_data = game_pack_data.FirstConnectData(self.player_count, game.get_game().player.profile.dump())
        await loop.sock_sendall(client, pickle.dumps(('first', pack_data)))
        self.player_count += 1
        await loop.sock_sendall(client, pickle.dumps(('player', self.players)))
        loop.create_task(self.send_displays(client))
        while True:
            recv = await loop.sock_recv(client, 32767)
            if not recv:
                break
            response = self.command_handler(recv)
            await loop.sock_sendall(client, response)
            await asyncio.sleep(0.04)
        client.close()

    async def start_server(self):
        loop = asyncio.get_event_loop()
        print('Server started')
        self.sock.bind((self.host, self.port))
        self.sock.setblocking(False)
        self.sock.listen(8)

        print(f'Server started on {self.host}:{self.port}')
        while True:
            client, _ = await loop.sock_accept(self.sock)
            loop.create_task(self.socket_handle(client))

    def update(self):
        self.players[0].pos << game.get_game().player.obj.pos


if __name__ == '__main__':
    server = SocketServer()
    asyncio.run(server.start_server())
