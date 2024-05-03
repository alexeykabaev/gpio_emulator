import time
import selectors
import socket
import types
from adaptor import Adaptor
from data import Gpio, RandomChanger

sel = selectors.DefaultSelector()

TIME_SLEEP = 0.2
MAX_SILENCE = 15
BUF = 1024


class Protocol:
    recv_time = None

    def __init__(self, sock: socket, dev: Gpio):
        self.sock = sock
        self.adaptor = Adaptor(dev)
        self.adaptor.pcol = self
        self._update_time()

    def _update_time(self):
        self.recv_time = int(time.time())

    def read(self):
        try:
            recv_data = self.sock.recv(BUF)
            if recv_data:
                self.adaptor.stream.parse(recv_data)
                self._update_time()
                print(recv_data)
                return True
        except socket.error as e:
            print(e)

    @property
    def is_silent(self):
        return int(time.time()) - self.recv_time > MAX_SILENCE

    def update_gpi(self):
        self.adaptor.send_gpi_state()

    def update_gpo(self):
        self.adaptor.send_gpo_state()


class Factory:
    addr = None

    def __init__(self, dev: Gpio):
        self.dev = dev
        self.s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def do_start(self, addr: str, port: int):
        self.addr = addr, port
        self.s_sock.bind(self.addr)
        self.s_sock.listen()
        print(f"Server started:{self.addr}")
        self.s_sock.setblocking(False)
        sel.register(self.s_sock, selectors.EVENT_READ, data=None)

    def build_protocol(self):
        sock, addr = self.s_sock.accept()
        print(f"Connection accepted:{addr}")
        sock.setblocking(False)
        pcol = Protocol(sock=sock, dev=self.dev)
        data = types.SimpleNamespace(pcol=pcol)
        sel.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)

    @staticmethod
    def check_clients():
        pcol_for_delete = []
        for _, obj in sel.get_map().items():
            if obj.data:
                if obj.data.pcol.is_silent:
                    pcol_for_delete.append(obj.data.pcol)
        for item in pcol_for_delete:
            print(f"Socket closed. Client is silent:{item.sock.getpeername()}")
            sel.unregister(item.sock)
            item.sock.close()


def main_loop(factory):
    changer = RandomChanger(factory.dev, period=1)
    try:
        while True:
            events = sel.select(timeout=TIME_SLEEP)

            for key, mask in events:

                if mask & selectors.EVENT_READ:
                    if key.data is None:
                        factory.build_protocol()
                    elif not key.data.pcol.read():
                        print(f"Connection lost:{key.data.pcol.sock.getpeername()}")
                        sel.unregister(key.data.pcol.sock)
                        key.data.pcol.sock.close()

            for key, mask in events:

                if mask & selectors.EVENT_WRITE:
                    if factory.dev.update_gpi_flag:
                        key.data.pcol.update_gpi()
                    if factory.dev.update_gpo_flag:
                        key.data.pcol.update_gpo()

            factory.dev.update_gpi_flag = False
            factory.dev.update_gpo_flag = False
            factory.check_clients()
            changer.do_change()

    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()


if __name__ == "__main__":
    dev = Gpio()
    factory = Factory(dev)
    factory.do_start("127.0.0.1", 805)

    main_loop(factory)
