import asyncio

import settings
from devices import Flashlight
from transports import FCProtocol


async def main() -> None:
    current_loop = asyncio.get_running_loop()
    protocol = FCProtocol()
    flashlight = Flashlight(protocol=protocol, loop=current_loop)
    flashlight.connect()
    await flashlight.listen_commands()

loop = asyncio.new_event_loop()
try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    exit(1)