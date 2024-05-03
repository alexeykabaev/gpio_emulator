import time
from typing import Union
from random import randrange

GPI_PINS = 8
GPO_PINS = 12
GPI = 1
GPO = 0
GPI_PREFIX = "GPI"
GPO_PREFIX = "GPO"
HIGH = 1
LOW = 0


class Pin:
    def __init__(self, number: int, level: int, is_input: int):
        self.number = number
        self.level = level
        self.is_input = is_input

    def __repr__(self):
        return f"{GPI_PREFIX if self.is_input else GPO_PREFIX}{self.number + 1}={self.level}"


class GpioBase:
    update_gpi_flag = False
    update_gpo_flag = False

    def __init__(self, gpi_count: int, gpo_count: int):
        self.gpi_count = gpi_count
        self.gpo_count = gpo_count
        self._gpi_dct = {i + 1: Pin(i, HIGH, GPI) for i in range(gpi_count)}
        self._gpo_dct = {i + 1: Pin(i, LOW, GPO) for i in range(gpo_count)}

    def __repr__(self):
        return f"{self._gpi_dct}\r\n{self._gpo_dct}\r\n"

    def _get_state(self, gpio_type: int):
        items = self._gpi_dct if gpio_type else self._gpo_dct
        return {key: value.level for key, value in items.items()}

    @property
    def gpi_state(self):
        return self._get_state(GPI)

    @property
    def gpo_state(self):
        return self._get_state(GPO)

    def _set_level(self, gpio_type: int, pin: int, level: Union[int, bool, None]):
        level = 1 if level else 0
        if gpio_type:
            if self._gpi_dct.get(pin):
                self._gpi_dct.get(pin).level = level
                self.update_gpi_flag = True
        else:
            if self._gpo_dct.get(pin):
                self._gpo_dct.get(pin).level = level
                self.update_gpo_flag = True

    def set_gpi(self, pin: int, level: Union[int, bool, None]):
        self._set_level(GPI, pin, level)

    def get_gpi(self, pin: int) -> int:
        return self._gpi_dct[pin].level

    def set_gpo(self, pin: int, level: Union[int, bool, None]):
        self._set_level(GPO, pin, level)

    def get_gpo(self, pin: int) -> int:
        return self._gpo_dct[pin].level


class Gpio(GpioBase):
    def __init__(self):
        gpi_count = GPI_PINS
        gpo_count = GPO_PINS
        super().__init__(gpi_count, gpo_count)


class RandomChanger:
    _flip_flop = True

    def __init__(self, dev: Gpio, period: int = 10):
        self.dev = dev
        self.period = period
        self.last_time_change = int(time.time())

    def do_change(self):
        now = int(time.time())
        if now - self.last_time_change > self.period:
            self.last_time_change = now
            self._change_level(self._flip_flop)
            self._flip_flop = not self._flip_flop

    def _change_level(self, gpio_type: int):
        if gpio_type:
            pin = randrange(self.dev.gpi_count) + 1
            level = self.dev.get_gpi(pin)
            self.dev.set_gpi(pin, not level)
        else:
            pin = randrange(self.dev.gpo_count) + 1
            level = self.dev.get_gpo(pin)
            self.dev.set_gpo(pin, not level)


if __name__ == "__main__":
    dev = Gpio()
    print(dev)
    dev.set_gpi(pin=1, level=LOW)
    dev.set_gpi(pin=2, level=False)
    dev.set_gpi(pin=8, level=None)
    dev.set_gpi(pin=-1, level=None)
    dev.set_gpo(pin=1, level=HIGH)
    dev.set_gpo(pin=12, level=True)
    dev.set_gpo(pin=13, level=True)
    print(dev)
    changer = RandomChanger(dev)
    changer._change_level(GPI)
    changer._change_level(GPO)
    print(dev)
    changer._change_level(GPI)
    changer._change_level(GPO)
    print(dev)
