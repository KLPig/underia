import socket
import asyncio
import pickle
from web import game_pack_data
from underia import game


class Client:
    def __init__(self, addr, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((addr, port))
        self.player_datas = {}
        self.started = False
        self.player_id = 0
        self.displays = {}

    def recv(self):
        s = None
        while not s:
            s = self.client_socket.recv(1024)
        return s

    async def start(self):
        self.started = True
        print('Client started')
        loop = asyncio.get_event_loop()
        while True:
            data = await loop.sock_recv(self.client_socket, 32767)
            if not data:
                continue
            data = pickle.loads(data)
            t, data = data
            if t == 'player':
                players: dict[int, game_pack_data.SinglePlayerData] = data
                for player in players.values():
                    self.player_datas[player.player_id] = player
            elif t == 'display':
                self.displays = data.display
            res = game_pack_data.SinglePlayerData(self.player_id, game.get_game().player)
            await loop.sock_sendall(self.client_socket, pickle.dumps(res))
            await asyncio.sleep(0.05)


