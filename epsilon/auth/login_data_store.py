from ..utils import CachedDict, Logger
import keyring
import json

log = Logger('LoginDataStore')

class LoginData(CachedDict):
    def __init__(self):
        super().__init__(getter=self._get_login_data, setter=self._set_login_data)
        log.debug(f'Initialized LoginData')

    def _get_login_data(self, username):
        log.debug(f'Requesting {username} from LoginDataStore')
        cred = keyring.get_credential('epsilon_login_data', username)
        psw = getattr(cred, 'password', None)
        if psw:
            return json.loads(psw)

    def _set_login_data(self, username, login_data):
        log.debug(f'Setting {username} in LoginDataStore')
        data = json.dumps(login_data)
        keyring.set_password('epsilon_login_data', username, data)
