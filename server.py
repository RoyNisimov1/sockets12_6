import socket
from threading import Thread
from protocol import Protocol
from datetime import datetime

class Server:

    ADDRESS = "0.0.0.0"
    PORT = 42069

    def __init__(self):
        self.clients = set()
        self.clients_id = {}
        self.silenced = set()
        self.threads = []
        self.sock = None
        self.managers = []
        with open("MANAGER_LIST.txt", "r") as f:
            self.managers = f.read().split("\n")
        self.managers = [m.encode() for m in self.managers]
        self.managers = set(self.managers)
        self.main()


    def main(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                self.sock = s
                self.sock.bind((Server.ADDRESS, Server.PORT))
                self.sock.listen()
                print(f"Server is running and listening on port {Server.PORT}")
                while True:
                    try:
                        conn, address = self.sock.accept()
                        print("Client is connected")
                        self.clients.add(conn)
                        thread = Thread(target=self.handle_client, args=[conn])
                        self.threads.append(thread)
                        thread.start()
                    except Exception:
                        ...
        except Exception:
            ...

    def handle_client(self, client: socket.socket):
        try:
            name = Protocol.get_msg(client)
            name = name.lstrip(b" ")
            if name[0] == b"@"[0]:
                print("Someone tried to impersonate a manager")
                d = Protocol.create_msg(b"NO")
                client.send(d)
                self.clients.remove(client)
                return
            if len(name) >= 10:
                print("username bigger than 10 chars")
                d = Protocol.create_msg(b"NO")
                client.send(d)
                self.clients.remove(client)
                return
            if name in self.clients_id.values():
                print(f"Someone tried to impersonate {name.decode()}")
                d = Protocol.create_msg(b"NO")
                client.send(d)
                self.clients.remove(client)
                return

            self.clients_id[client] = name

            d = Protocol.create_msg(b"OK")
            client.send(d)
            while True:
                try:
                    client_id, cmd, params = Protocol.recv_command(client)
                    if cmd == 9:
                        self.close(client)
                        return

                    if cmd == 1:
                        if name in self.silenced:
                            client.send(Protocol.create_msg(b"You cannot speak here"))
                            continue
                        name = self.clients_id[client]
                        now = datetime.now()
                        time_now = now.strftime("%H:%M")
                        show_name = name
                        if name in self.managers:
                            show_name = b"@" + show_name
                        data = time_now.encode() + b" " + show_name + b": " + params["msg"].encode()
                        Protocol.broadcast(data, self.clients)

                    if cmd == 2:
                        if client_id not in self.managers: continue
                        manager_to_be = params["manid"].encode()
                        if manager_to_be not in self.clients_id.values(): continue
                        self.managers.add(manager_to_be)

                    if cmd == 3:
                        if client_id not in self.managers: continue
                        man = client_id
                        client_id = params["client_id"].encode()
                        if client_id not in self.clients_id.values(): continue

                        kicked_client = self.get_client_from_id(client_id)
                        kicked_client.send(Protocol.create_msg(Protocol.KICK))
                        self.close(kicked_client)
                        Protocol.broadcast(f"{client_id.decode()} got kicked by {man.decode()}".encode(), self.clients)

                    if cmd == 4:
                        if client_id not in self.managers: continue
                        client_id_to_silence = params["client_id"].encode()
                        if client_id_to_silence not in self.clients_id.values(): continue
                        self.silenced.add(client_id_to_silence)
                        Protocol.broadcast(f"{client_id_to_silence.decode()} got silenced by {client_id.decode()}".encode(), self.clients)
                    if cmd == 5:
                        if name in self.silenced:
                            client.send(Protocol.create_msg(b"You cannot speak here"))
                            continue
                        client_id = params["client_id"].encode()
                        client_socket: socket.socket = self.get_client_from_id(client_id)
                        name = self.clients_id[client]
                        now = datetime.now()
                        time_now = now.strftime("%H:%M")
                        show_name = name
                        if name in self.managers:
                            show_name = b"@" + show_name
                        data = time_now.encode() + b" " + show_name + b": " + params["msg"].encode()

                        m = Protocol.create_msg(data)
                        client_socket.send(m)


                except ConnectionError:
                    self.close(client)
                    return
        except ConnectionError:
            self.close(client)
            return

    def get_client_from_id(self, identifier):
        return {v: k for k, v in self.clients_id.items()}[identifier]

    def close(self, client):
        try:
            name = self.clients_id[client]

            print("Disconnecting client: " + name.decode())
            self.clients_id.pop(client)
            self.clients.remove(client)
            client.close()
            Protocol.broadcast(name + b" has left the chat!", self.clients_id)
        except Exception:
            ...

if __name__ == "__main__":
    s = Server()

