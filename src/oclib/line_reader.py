from pathlib import Path
from queue import Queue


class LineBuffer:
    """
    Line buffer
    """

    def __init__(self, max_size: int):
        self.__queue = Queue(max_size)

    def add_byte(self, one_byte: bytes):
        data_size = len(one_byte)
        if data_size != 1:
            raise ValueError('len(one_byte) != 1')
        if self.__queue.full():
            self.__queue.get()
        self.__queue.put(int(one_byte[0]))

    def get_bytes(self) -> bytes:
        return bytes(self.__queue.queue)

    def clear(self):
        self.__queue.queue.clear()


class LineReader:
    r"""
    Line reader

    constructor:
        file (pathlib.Path): File path.
        max_line_len (int): Maximum length of the line.
        sep (bytes): Separate byte, default is b'\n'.
    usage:
        with LineReader(file, max_line, sep) as reader:
            # line is <class 'bytes'>
            for line in reader:
                if line:
                    print(line)
                elif line == b'':
                    print('empty line.')
                else:
                    print('line is too long.')
    """

    def __init__(self, file: Path, max_line_len: int, sep: bytes = b'\n'):
        if len(sep) != 1:
            raise ValueError('len(sep) != 1')
        self.__file = file
        self.__max_line = max_line_len
        self.__sep = sep
        self.__line_buffer = LineBuffer(max_line_len)
        self.__pos = 0
        self.__start_line = 0
        self.__file_obj = None
        self.__is_finished = False

    def open(self):
        if not self.__file_obj:
            self.__file_obj = open(self.__file, 'rb')

    def close(self):
        if self.__file_obj:
            self.__file_obj.close()
            self.__line_buffer.clear()
            self.__pos = 0
            self.__start_line = 0
            self.__file_obj = None
            self.__is_finished = False

    def reset(self):
        self.__line_buffer.clear()
        self.__pos = 0
        self.__start_line = 0
        self.__is_finished = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __read(self, one_byte: bytes) -> bytes:
        self.__pos += 1
        line_len = self.__pos - self.__start_line - 1
        result = None
        if one_byte != self.__sep:
            if line_len <= self.__max_line:
                self.__line_buffer.add_byte(one_byte)
        else:
            if line_len <= self.__max_line:
                result = self.__line_buffer.get_bytes()
                self.__line_buffer.clear()
                self.__start_line = self.__pos
            else:
                self.__line_buffer.clear()
                self.__start_line = self.__pos
                result = None
        return result

    def __next__(self) -> bytes:
        if self.__is_finished:
            raise StopIteration
        while True:
            self.__file_obj.seek(self.__pos)
            one_byte = self.__file_obj.read(1)
            if one_byte:
                if one_byte == self.__sep:
                    return self.__read(one_byte)
                else:
                    self.__read(one_byte)
            else:
                self.__is_finished = True
                return self.__read(self.__sep)

    def __iter__(self):
        return self
