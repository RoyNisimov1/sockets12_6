import socket
from threading import Thread
from tkinter import mainloop

from protocol import Protocol


class Client:
    SERVER = "127.0.0.1"
    PORT = 42069

    def __init__(self):
        self.sock = None
        self.disconnect = False


    def connect(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                self.sock = s
                self.sock.connect((Client.SERVER, Client.PORT))
                print(f"Connected to {Client.SERVER}")
                name = input("Username: ").encode()
                d = Protocol.create_msg(name)
                self.sock.send(d)
                listen_thread = Thread(target=self.listen, args=[s])
                listen_thread.start()
                self.mainloop(s)
        except Exception:
            ...

    def listen(self, s):
        while True:
            try:
                if self.disconnect: return
                msg = Protocol.get_msg(self.sock)
                print(msg.decode())
            except ConnectionError:
                return
            except Exception:
                ...

    def mainloop(self, s):
        while True:
            msg = input("").encode()
            if msg == b"quit":
                return
            d = Protocol.create_msg(msg)
            self.sock.send(d)


if __name__ == "__main__":
    c = Client()
    c.connect()