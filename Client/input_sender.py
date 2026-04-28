import socket
import json
from pynput import mouse, keyboard

from tls_config import create_tls_context        

HOST = "127.0.0.1"
PORT = 5001

def start_input_capture(session_token):
    context = create_tls_context()               

    sock = socket.socket()
    secure_socket = context.wrap_socket(
        sock,
        server_hostname=HOST
    )

    secure_socket.connect((HOST, PORT))

    
    secure_socket.sendall(
        (session_token + "\n").encode()
    )

    print("[INPUT AUTH OK]")
    print("[INPUT TLS]", secure_socket.cipher())

    def send_event(event):
        event["token"] = session_token
        secure_socket.sendall(
            (json.dumps(event) + "\n").encode()
        )

    def on_move(x, y):
        send_event({"type": "mouse_move", "x": x, "y": y})

    def on_click(x, y, button, pressed):
        if pressed:
            send_event({"type": "click"})

    def on_press(key):
        try:
            send_event({"type": "key", "key": key.char})
        except:
            pass

    mouse_listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click
    )
    keyboard_listener = keyboard.Listener(
        on_press=on_press
    )

    mouse_listener.start()
    keyboard_listener.start()
    mouse_listener.join()
    keyboard_listener.join()