import secrets
import time

SESSIONS = {}
TOKEN_LIFETIME = 600

def generate_session_token():
    return secrets.token_hex(32)

def create_session(client_id):
    token = generate_session_token()
    SESSIONS[token] = {
        "client": client_id,
        "expiry": time.time() + TOKEN_LIFETIME
    }
    return token

def validate_token(token):
    if token not in SESSIONS:
        return False
    if time.time() > SESSIONS[token]["expiry"]:
        del SESSIONS[token]
        return False
    return True