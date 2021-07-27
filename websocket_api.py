import asyncio
import websockets

"""
RECEIVE A MESSAGE AND SEND BACK A RESPONSE
"""

async def server(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name} !"

    await websocket.send(greeting)
    print(f"> {greeting}")

start_server = websockets.serve(server, "localhost", 5000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()