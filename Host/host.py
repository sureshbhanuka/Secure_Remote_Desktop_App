import socket
import struct
import pickle
import cv2
import mss
import numpy as np
import threading

from session import create_session, validate_token
from tls_config import create_tls_context
from input_handler import start_input_server

HOST = "0.0.0.0"
PORT = 5000

def stream_screen():
    context = create_tls_context()

    server = socket.socket()
    server.bind((HOST, PORT))
    server.listen(1)

    print("[+] Waiting for client...")

    conn, addr = server.accept()
    print("[+] Client connected:", addr)

    secure_conn = context.wrap_socket(conn, server_side=True)

    # mTLS verified — auto create session, no manual auth needed
    token = create_session("client001")
    print("[+] Auto session created:", token)
    secure_conn.send((token + "\n").encode())

    print("[TLS]", secure_conn.cipher())

    with mss.mss() as sct:
        monitor = sct.monitors[1]

        while True:
            img = np.array(sct.grab(monitor))
            img = cv2.resize(img, (1280, 720))

            _, buffer = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
            data = pickle.dumps(buffer)
            msg = struct.pack("Q", len(data)) + data

            if not validate_token(token):
                print("Session expired")
                break

            try:
                secure_conn.sendall(msg)
            except:
                break

    secure_conn.close()
    server.close()

if __name__ == "__main__":
    t = threading.Thread(target=start_input_server)
    t.start()

    stream_screen()