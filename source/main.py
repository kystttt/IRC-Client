import asyncio
import sys
import websockets


async def irc_client():
    nick = sys.argv[1] if len(sys.argv) > 1 else "Default"
    channel = sys.argv[2] if len(sys.argv) > 2 else "test"
    uri = "wss://irc.oftc.net/irc"
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(f'NICK {nick}')
            await websocket.send(f'USER {nick} 0 :Python IRC Bot')
            await websocket.send(f'JOIN #{channel}')
            print("Connected! Type messages or 'exit' to quit.")

            while True:
                message = input("> ")
                if message.lower() == "exit":
                    break
                await websocket.send(f"PRIVMSG #test :{message}")
                response = await websocket.recv()
                print(f"< {response}")
    except Exception as e:
        print(f'Error: {e}')


asyncio.get_event_loop().run_until_complete(irc_client())