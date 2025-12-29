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
        self.threads = []
        self.sock = None
        self.main()

    def main(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                self.sock = s
                self.sock.bind((Server.ADDRESS, Server.PORT))
                self.sock.listen()
                print(f"Server is running and listening on port {Server.PORT}")
                while True:
                    conn, address = self.sock.accept()
                    print("Client is connected")
                    self.clients.add(conn)
                    thread = Thread(target=self.handle_client, args=[conn])
                    self.threads.append(thread)
                    thread.start()
        except Exception:
            ...

    def handle_client(self, client: socket.socket):
        name = Protocol.get_msg(client)
        self.clients_id[client] = name

        while True:
            try:
                data = Protocol.get_msg(client)
                if data == b"quit":
                    self.close(client)
                    return
                name = self.clients_id[client]
                now = datetime.now()
                time_now = now.strftime("%H:%M")
                data = time_now.encode() + b" " + name + b": " + data
                Protocol.broadcast(data, self.clients)
            except ConnectionError:
                self.close(client)
                return

    def close(self, client):
        name = self.clients_id[client]

        print("Disconnecting client: " + name.decode())
        self.clients_id.pop(client)
        self.clients.remove(client)
        client.close()
        Protocol.broadcast(b"Disconnecting client: " + name, self.clients_id)

if __name__ == "__main__":
    s = Server()

