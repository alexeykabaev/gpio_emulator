GPI_GET = b"GPI_GET"
GPO_GET = b"GPO_GET"
GPI_SET = b"GPI_SET"
GPO_NUM = b"GPO"
DELIMITER = b"\r\n"
SEPARATOR = b"="
EMPTY = b""
BUF_SIZE = 1024


class Stream:
    _buf = EMPTY
    _set_gpi_flag = False

    def __init__(self, gpi_get_cb, gpo_get_cb, gpo_set_cb):
        self.handlers = {
            GPI_GET: gpi_get_cb,
            GPO_GET: gpo_get_cb,
            GPI_SET: lambda: True,
        }
        self.gpi_set_cb = gpo_set_cb

    def parse(self, data: bytes):
        self._buf += data

        #clear buffer if full
        if self._buf.__len__() > BUF_SIZE:
            self._buf = EMPTY

        while True:
            try:
                message, self._buf = self._buf.split(sep=DELIMITER, maxsplit=1)
            except ValueError:
                return
            func = self.handlers.get(message.strip())
            if func:
                self._set_gpi_flag = func()
            else:
                if self._set_gpi_flag and message[:3] == GPO_NUM:
                    try:
                        pin, level = message[3:].split(sep=SEPARATOR, maxsplit=1)
                        self.gpi_set_cb(int(pin), int(level))
                        print(f"GPO{int(pin)}={int(level)}")
                    except Exception as e:
                        print("Set GPI, bad args:", e)
                else:
                    self._set_gpi_flag = False
