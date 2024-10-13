import asyncio
import logging
from abc import ABC
from asyncio import AbstractEventLoop
from tkinter import Canvas, Tk
from typing import TypeVar

from transports import NetworkTCP, TLVMessage


T = TypeVar('T', bound=NetworkTCP)

class RemoteDevice(ABC):
    """
    Абстрактный класс дистанционного устройства
    """

    def __init__(self) -> None:
        self.is_on = False

    def connect(self, host, port) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def turn_on(self, value) -> None:
        pass

    def turn_off(self, value) -> None:
        pass


class Flashlight(RemoteDevice):
    """
    Класс реализуемого фонаря
    """
    def __init__(
            self,
            protocol: T,
            loop: AbstractEventLoop,
            color: tuple = (0, 0, 0)
    ) -> None:
        """
        :protocol: - протокол взаимодействия по сети, который использует фонарь
        :loop: - текущий цикл событий
        :color: - цвет фонаря (по умолчанию черный)
        """
        super().__init__()
        self.protocol: T = protocol
        self.loop: AbstractEventLoop = loop
        self.color: tuple = color

    def connect(self, host='127.0.0.1', port=9999) -> None:
        """
        Метод для подключения фонаря к серверу

        :host: - адрес сервера для подключения
        :port: - порт сервера для подключения
        """
        try:
            self.protocol.socket.connect((host, port))
        except ConnectionError as e:
            logging.error(e)
        else:
            logging.info('Соединение установлено')
            self.protocol.socket.setblocking(False)

    async def disconnect(self) -> None:
        self.protocol.socket.close()
        logging.info('Соединение закрыто')

    async def listen_commands(self) -> None:
        """
        Метод для приема команд фонаря от сервера
        """
        try:
            while data := await self.loop.sock_recv(self.protocol.socket, 1024):
                message = TLVMessage(data)
                message.decode_fields()
                available_commands = self.protocol.available_commands
                if message.type not in available_commands.keys():
                    logging.warning('Неизвестная команда')
                    continue
                asyncio.create_task(available_commands.get(message.type)(self, message.value))
        except Exception as e:
            logging.error(e)
        finally:
            await self.disconnect()

    async def turn_on(self, value: tuple | None) -> None:
        """
        Метод включения фонаря
        """
        if self.is_on:
            return
        self.is_on = True
        logging.info('Фонарь включен')
        await self.show_color()

    async def turn_off(self, value: tuple | None) -> None:
        """
        Метод выключения фонаря
        """
        self.is_on = False
        logging.info('Фонарь выключен')
        await self.disconnect()
        

    async def change_color(self, color: tuple) -> None:
        """
        Метод смены цвета фонаря
        """
        if not self.is_on:
            return
        self.color = color
        logging.info(f'Цвет фонаря изменен на {self.color}')
        await self.show_color()

    async def show_color(self) -> None:
        """
        Метод отображения текущего цвета фонаря
        """
        window = Tk()
        window.title("Новый цвет фонаря")

        canvas = Canvas(window, width=400, height=400)
        canvas.pack()

        hex_color = f'#{self.color[0]:02x}{self.color[1]:02x}{self.color[2]:02x}'

        x0, y0, x1, y1 = 100, 100, 300, 300
        canvas.create_oval(x0, y0, x1, y1, fill=hex_color, outline="")
        window.mainloop()