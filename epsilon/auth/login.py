from urllib.parse import urlparse, parse_qs
from .login_data_store import LoginData
from ..utils import ConfigStore, Logger
import minecraft_launcher_lib as mcl
import webbrowser
import socket

CLIENT_ID = "35292a04-c714-4fac-92e0-82c3ea360278"
REDIRECT_URI = "http://localhost:8000/completeLogin"

login_data_store:dict[str, mcl.microsoft_types.CompleteLoginResponse] = LoginData()
config = ConfigStore('accounts.json', values={"accounts": []})

log = Logger("LOGIN")

class LoginFailedException(Exception): ...

def login(username:str='') -> tuple[str, mcl.microsoft_types.CompleteLoginResponse]:
    log.trace(f'login({username=})')
    if not username and config['accounts']:
        username = config['accounts'][0]
        log.trace(f'Picked default account in config: {username}')

    # Check if has cached value
    if username in login_data_store:
        # Cached value is valid, return it
        if login_data_store[username]:
            log.debug('Using cached login data')
            return username, login_data_store[username]

        # Cached value is None, ignore it
        login_data_store.pop(username)

    username, login_data = _full_login()

    login_data_store[username] = login_data

    if username not in config["accounts"]:
        log.debug(f"Adding username to accounts config: {username}")
        config["accounts"].append(username)

    return username, login_data

def _get_auth_code(url):
    log.trace(f'_get_auth_code({url=})')
    webbrowser.open(url)
    return _get_code_server()

def _get_code_server():
    log.trace('_get_code_server()')
    s = socket.socket()
    s.bind(('127.0.0.1', 8000))
    s.listen(5)
    s.settimeout(240)

    try:
        cs, addr = s.accept()
        path = cs.recv(2048).decode().split(' ')[1]
    except socket.timeout:
        return None

    code = parse_qs(urlparse(path).query).get('code')

    log.trace(f'Conn from {addr=}, req {path=}.')
    log.debug("Got code, ", len=len(code) if code else None)

    cs.send(b"HTTP/1.1 200 OK\r\n\r\n<h1>Login success\r\n")
    s.close()

    return None if not code else code[0]

def _full_login():
    log.trace('_full_login()')
    # Generate random state
    state = mcl.microsoft_account.generate_state()

    url, state, code_verifier = mcl.microsoft_account.get_secure_login_data(CLIENT_ID, REDIRECT_URI, state)

    code = _get_auth_code(url)

    if not code:
        log.fatal(f'User cancelled login. ({code=})')
        raise LoginFailedException("User cancelled login.")

    login_data = mcl.microsoft_account.complete_login(CLIENT_ID, None, REDIRECT_URI, code, code_verifier)

    log.debug('Login complete')

    return login_data["name"], login_data
