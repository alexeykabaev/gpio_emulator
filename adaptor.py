from data import Gpio, GPI_PREFIX, GPO_PREFIX, GPI, GPO
from stream import Stream
from util import dict_to_binary


class Adaptor:
    pcol = None

    def __init__(self, dev: Gpio):
        self.dev = dev
        self.stream = Stream(
            gpi_get_cb=self.send_gpi_state,
            gpo_get_cb=self.send_gpo_state,
            gpo_set_cb=self.set_gpo,
        )

    def _get_gpio(self, gpio_type: int):
        gpio, prefix = (
            (self.dev.gpi_state, GPI_PREFIX)
            if gpio_type
            else (self.dev.gpo_state, GPO_PREFIX)
        )

        binary = dict_to_binary(gpio)

        print(f"{prefix}={binary}\r\n".encode())
        if self.pcol:
            self.pcol.sock.send(f"{prefix}={binary}\r\n".encode())

    def send_gpi_state(self):
        self._get_gpio(GPI)

    def send_gpo_state(self):
        self._get_gpio(GPO)

    def set_gpo(self, pin: int, level: int):
        if self.dev.set_gpo(pin, level):
            self.send_gpo_state()


if __name__ == "__main__":
    dev = Gpio()
    adaptor = Adaptor(dev)
    adaptor.stream.parse(b"\r\n\n\n\nGPI_GET\r\nGPO_GET\r\nGPO_GET\rGPO_ET\r\n")
    adaptor.stream.parse(b"\r\nGPI_SET\r\nGPO1=1\r\nGPO2=10\rGPO_ET\r\n")
    adaptor.stream.parse(b"\r\nGPI_ET\r\nGPO1=1\r\nGPO2=10\rGPO_ET\r\n")
    adaptor.stream.parse(b"\r\nGPI_SET\r\nGPO1=q\r\nGPO2=50\rGPO_ET\r\n")
    adaptor.stream.parse(b"\r\nGPI_SET\r\nGPO100=0\r\nGPO2=\rGPO1a=0\r\n")
