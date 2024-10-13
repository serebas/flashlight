import socket
import struct
from abc import ABC


class NetworkTCP(ABC):
    pass


class FCProtocol(NetworkTCP):
    """
    Flashlight Control Protocol - Протокол управления фонарем (v1)
    """
    def __init__(self) -> None:
        """
        :socket: - сокет, через который протокол работает по сети
        :available_commands: - словарь с командами, которые поддерживает протокол.
                               Ключами являются значениями поля type, передаваемого сообщения
        """
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.available_commands = {
            0x12: self.turn_on,
            0x13: self.turn_off,
            0x20: self.change_color
        }

    @staticmethod
    async def turn_on(device, value=None):
        await device.turn_on(value)

    @staticmethod
    async def turn_off(device, value=None):
        await device.turn_off(value)

    @staticmethod
    async def change_color(device, value=None):
        await device.change_color(value)


class TLVMessage:
    """
    Класс сообщения, передоваемого по сети
    """
    def __init__(
            self,
            raw_bytes: bytes,
            size_type: tuple = (1, 'B'),
            size_length: dict = (2, 'H'),
            byte_order: str = '>'
    ) -> None:
        """
        :raw_bytes: - данные передаваемые по сети закодированные в байты
        :size_type: - кортеж параметров поля type (размер поля type, формат поля)
        :size_length: - кортеж параметров поля length (размер поля length, формат поля)
        https://docs.python.org/3/library/struct.html#format-characters
        :byte_order: - символ управления порядком байтов (по умолчанию Big Endian)
        https://docs.python.org/3/library/struct.html#struct-alignment
        """
        self.buffer = raw_bytes
        self.size_type = size_type
        self.size_length = size_length
        self.byte_order = byte_order
        self.type = None
        self.length = None
        self.value = None

    def decode_fields(self) -> None:
        """
        Метод преобразования полей сообщения из байтов в объекты Python
        """
        header_size = self.size_type[0] + self.size_length[0]
        header_format = f'{self.byte_order}{self.size_type[1]}{self.size_length[1]}'
        self.type, self.length = struct.unpack(header_format, self.buffer[:header_size])
        if self.length:
            self.value = struct.unpack(f'{"b"*self.length}', self.buffer[header_size:])
