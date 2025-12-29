import socket
from threading import Thread


class Server:

    ADDRESS = "0.0.0.0"
    PORT = 8820

    def __init__(self):
        self.clients = set()
        self.threads = []
        self.sock = None
        self.main()

    def main(self):
        with socket.socket() as self.sock:
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

    def handle_client(self, client):
        while True:
            ...


