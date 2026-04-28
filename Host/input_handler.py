import socket
import json
import pyautogui

from session import validate_token
from tls_config import create_tls_context        

HOST = "0.0.0.0"
PORT = 5001

def start_input_server():
    context = create_tls_context()               

    server = socket.socket()
    server.bind((HOST, PORT))
    server.listen(1)

    print("[+] Input server listening...")

    conn, addr = server.accept()
    print("[+] Input client:", addr)

    secure_conn = context.wrap_socket(conn, server_side=True)

    
    token = secure_conn.recv(1024).decode().strip()
    print("[INPUT AUTH] Token:", token)

    if not validate_token(token):
        print("Invalid session")
        secure_conn.close()
        return

    print("[+] Input session valid")

    buffer = ""

    while True:
        try:
            data = secure_conn.recv(4096).decode()
            if not data:
                break

            buffer += data

            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)
                event = json.loads(msg)

                if event.get("token") != token:
                    continue

                if event["type"] == "mouse_move":
                    pyautogui.moveTo(event["x"], event["y"])

                elif event["type"] == "click":
                    pyautogui.click()

                elif event["type"] == "key":
                    pyautogui.write(event["key"])

        except Exception as e:
            print("INPUT ERROR:", e)
            break

    secure_conn.close()