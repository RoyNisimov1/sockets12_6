import os
import socket
import json

class Protocol:

    KICK = b"KICK"

    @staticmethod
    def create_msg(data: bytes) -> bytes:
        len_data = len(data)
        l = Protocol.convert_base(len_data, 256)
        if len(l) > 4: raise Exception(f"Data {data} is too big to send in one packet!")
        for _ in range(4 - len(l)):
            l.insert(0, 0)
        prepending_bytes = b"".join([l[i].to_bytes(1, "little") for i in range(4)])
        return prepending_bytes + data

    @staticmethod
    def get_msg(working_socket: socket.socket):
        prepending_bytes = working_socket.recv(4)
        l = [b for b in prepending_bytes]
        len_of_msg = Protocol.convert_to_base10(l, 256)
        return working_socket.recv(len_of_msg)


    @staticmethod
    def convert_base(n, b):
        if n == 0:
            return [0]
        digits = []
        while n:
            digits.append(int(n % b))
            n //= b
        return digits[::-1]

    @staticmethod
    def convert_to_base10(n, b):
        s = 0
        n.reverse()
        for p in range(len(n)):
            s += n[p] * pow(b, p)
        return s


    @staticmethod
    def send_file(working_socket: socket.socket, file_path: str):
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                b = f.read()
            working_socket.send(Protocol.create_msg(str(len(b)).encode()))
            working_socket.sendall(b)
        else:
            working_socket.send(Protocol.create_msg(b"Failed to send!"))

    @staticmethod
    def recv_file(working_socket: socket.socket):
        size = int(Protocol.get_msg(working_socket).decode())
        s = 0
        b = b""
        while s < size:
            data = working_socket.recv(size)
            b += data
            s += len(data)
        return b

    @staticmethod
    def broadcast(msg: bytes, clients: set):
        data = Protocol.create_msg(msg)
        for client in clients:
            try:
                client.send(data)
            except:
                ...

    @staticmethod
    def send_command(client_id: bytes, cmd: int, params, sock: socket.socket):
        length_of_name = len(client_id.decode())
        if length_of_name >= 10: return
        if cmd >= 10: return
        j = json.dumps(params).encode()
        s = str(length_of_name).encode() + client_id + str(cmd).encode() + j
        data_to_send = Protocol.create_msg(s)
        sock.send(data_to_send)

    @staticmethod
    def recv_command(sock):
        data = Protocol.get_msg(sock)
        l = int(data[0].to_bytes(1, "little").decode())
        client_id = data[1: l+1]
        cmd = int(data[l+1].to_bytes(1, "little").decode())
        j = data[l+2:].decode()
        params = json.loads(j)
        return client_id, cmd, params
