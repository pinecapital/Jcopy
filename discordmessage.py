import websocket
import json
import time
import threading
from dotenv import load_dotenv
import os
import ssl

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE, "ssl_version": ssl.PROTOCOL_TLSv1_2, "context": ssl_context})

load_dotenv()  # take environment variables from .env.
token = os.getenv('DISCORD_TOKEN')
initial_url = "wss://gateway.discord.gg"
url = initial_url
session_id = ""
usernameofbot = "Sir Goldman Alerts"
interval = 0
seq = -1

payload = {
    "op": 2,
    "d": {
        "token": token,
        "intents": 33280,
        "properties": {
            "$os": 'linux',
            "$browser": 'chrome',
            "$device": 'chrome'
        }
    }
}

def heartbeat(ms):
    def send_heartbeat():
        while True:
            try:
                ws.send(json.dumps({
                    "op": 1,
                    "d": None
                }))
                time.sleep(ms / 1000)
            except websocket.WebSocketConnectionClosedException:
                print("Connection closed, retrying...")
                time.sleep(2.5)
                initialize_websocket()

    return threading.Thread(target=send_heartbeat)

def on_open(ws):
    if url != initial_url:
        resume_payload = {
            "op": 6,
            "d": {
                "token": token,
                "sessionId": session_id,
                "seq": seq,
            }
        }
        ws.send(json.dumps(resume_payload))

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_reason):
    print("Connection lost, attempting to reconnect")
    time.sleep(5)
    initialize_websocket(reconnect=True)  # Pass reconnect=True here


def on_message(ws, message):
    global url, session_id, seq, interval
    p = json.loads(message)
    op = p.get('op')
    t = p.get('t')
    d = p.get('d')
    s = p.get('s')

    if op == 10:
        heartbeat_interval = d.get('heartbeat_interval')
        interval = heartbeat(heartbeat_interval)
        interval.start()

        if url == initial_url:
            ws.send(json.dumps(payload))

    elif op == 0:
        seq = s

    if t == "READY":
        print("Gateway connection Ready")
        url = d.get('url')
        session_id = d.get('session_id')

    elif t == "RESUMED":
        print("Gateway connection resumed")

    elif t == "MESSAGE_CREATE":
        author = d.get('author').get('username')
        content = d.get('content')
        # print(f"[{author}]: {content}")
        if author == usernameofbot:
            embeds = d.get('embeds', [])
            for embed in embeds:
                title = embed.get('title')
                if title in ['ENTRY', 'COMMENT', 'SCALE', 'EXIT']:
                    description = embed.get('description')
                    print(f'[{title}]:[{description}]')

def initialize_websocket(reconnect=False):
    global ws, url, session_id, seq, interval
    backoff_time = 1  # start with 1 second
    while True:
        try:
            if reconnect:
                url = initial_url
                session_id = ""
                seq = -1
                interval = 0
            ws_url = url if url is not None else initial_url
            ws = websocket.WebSocketApp(ws_url + "/?v=10&encoding=json",
                                        on_open=on_open,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.run_forever()
            break  # if connection is successful, break the loop
        except websocket.WebSocketConnectionClosedException:
            print("Connection lost, attempting to reconnect in {} seconds".format(backoff_time))
            time.sleep(backoff_time)
            backoff_time *= 2  # double the backoff time
            if backoff_time > 60:  # limit the maximum backoff time to 60 seconds
                backoff_time = 60

def main():
    while True:
        try:
            initialize_websocket()
        except websocket.WebSocketConnectionClosedException:
            print("Connection lost, attempting to reconnect")
            time.sleep(5)
            initialize_websocket(reconnect=True) 

main()
