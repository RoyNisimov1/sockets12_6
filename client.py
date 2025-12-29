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
        self.name = b""

    def connect(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                self.sock = s
                self.sock.connect((Client.SERVER, Client.PORT))
                print(f"Connected to {Client.SERVER}")
                self.name = input("Username: ").encode()
                d = Protocol.create_msg(self.name)
                self.sock.send(d)
                msg_code = Protocol.get_msg(self.sock)
                if msg_code == b"NO":
                    return
                elif msg_code == b"OK":
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
                GREEN = '\033[32m'
                RESET = '\033[0m'
                print(GREEN)
                print(msg.decode())
                print(RESET)

            except ConnectionError:
                self.disconnect = True
                return
            except Exception:
                ...

    def mainloop(self, s):
        cmds = """
        1: Send chat message to the chat
        2: Appoint manager (managers only) - manager to appoint (id)
        3: Kick users (managers only) - user to kick (id)
        4: Silence (managers only) - user to silence (id)
        5: Private chatting - user to chat to (id)
        quit
"""
        while True:
            try:
                if self.disconnect:
                    return
                cmd = input(cmds)
                if cmd == "quit":
                    self.disconnect = True
                    Protocol.send_command(self.name, 9, {}, self.sock)

                cmd = int(cmd)
                if cmd == 1:
                    msg = input("Message: ")
                    Protocol.send_command(self.name, cmd, {"msg": msg}, self.sock)
                if cmd == 2:
                    managerID = input("Manager id: ")
                    Protocol.send_command(self.name, cmd, {"manid": managerID}, self.sock)
                if cmd == 3:
                    clientID = input("Client id: ")
                    Protocol.send_command(self.name, cmd, {"client_id": clientID}, self.sock)
                if cmd == 4:
                    clientID = input("Client id: ")
                    Protocol.send_command(self.name, cmd, {"client_id": clientID}, self.sock)
                if cmd == 5:
                    clientID = input("Client id: ")
                    msg = input("Message: ")
                    Protocol.send_command(self.name, cmd, {"client_id": clientID, "msg": msg}, self.sock)


            except:
                ...


if __name__ == "__main__":
    c = Client()
    c.connect()