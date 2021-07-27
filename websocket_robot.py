import websockets
import asyncio

async def hello(name):
    url = "ws://localhost:5000"

    async with websockets.connect(url) as ws:
        # name = input("What's your name ?")
        
        await ws.send(name)
        print(f"> {name}")
        
        greeting = await ws.recv()
        print(f"< {greeting}")


if __name__ == '__main__':
    
    while(True):
        name = input()
        hello(name)
        asyncio.get_event_loop().run_until_complete(hello(name))