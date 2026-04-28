import socket
import struct
import pickle
import cv2
import threading
from input_sender import start_input_capture
from tls_config import create_tls_context       

HOST = "127.0.0.1"
PORT = 5000

def receive_screen():
    context = create_tls_context()              

    raw_socket = socket.socket()
    secure_client = context.wrap_socket(
        raw_socket,
        server_hostname=HOST
    )

    secure_client.connect((HOST, PORT))

    
    token = secure_client.recv(1024).decode().strip()

    if token == "AUTH_FAIL":
        print("Access denied")
        return

    print("[+] Session token:", token)

    
    t = threading.Thread(
        target=start_input_capture,
        args=(token,)
    )
    t.daemon = True
    t.start()

    payload_size = struct.calcsize("Q")
    data = b""

    while True:
        while len(data) < payload_size:
            packet = secure_client.recv(4096)
            if not packet:
                return
            data += packet

        packed_size = data[:payload_size]
        data = data[payload_size:]

        msg_size = struct.unpack("Q", packed_size)[0]

        while len(data) < msg_size:
            data += secure_client.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        buffer = pickle.loads(frame_data)
        frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

        cv2.imshow("Remote Desktop", frame)

        if cv2.waitKey(1) == 27:
            break

    secure_client.close()

if __name__ == "__main__":
    receive_screen()