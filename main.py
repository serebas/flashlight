import asyncio

import settings
from devices import Flashlight
from transports import FCProtocol


async def main() -> None:
    current_loop = asyncio.get_running_loop()
    protocol = FCProtocol()
    flashlight = Flashlight(protocol=protocol, loop=current_loop)

    creds = input('Введите адрес и порт сервера для подключения в формате <host:port>. \
Нажмите Enter чтобы использовать по-умолчанию (127.0.0.1:9999):').split(':')
    if len(creds) < 2:
        flashlight.connect()
    else:
        flashlight.connect(host=creds[0], port=int(creds[1]))

    await flashlight.listen_commands()

loop = asyncio.new_event_loop()
try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    exit(1)