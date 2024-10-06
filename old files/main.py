import asyncio
import json
from dropfarm import Dropfarm
import websockets

async def main():
    bot = Dropfarm()
    server = await websockets.serve(
        lambda ws, path: handle_websocket(ws, path, bot),
        "localhost",
        8765
    )
    await server.wait_closed()

async def handle_websocket(websocket, path, bot):
    async for message in websocket:
        data = json.loads(message)
        if data['command'] == 'start':
            await bot.start(data.get('token', 'GOATS'))
        elif data['command'] == 'stop':
            await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())