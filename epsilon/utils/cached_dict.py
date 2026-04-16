from typing import Any

class CachedDict(dict):
    def __init__(self, values=None, getter=lambda k: None, setter=lambda k, v: None) -> None:
        if values is None:
            values = {}

        self._setter = setter
        self._getter = getter
        super().__init__()
        object.__setattr__(self, '_getter', getter)

    def __getattr__(self, name) -> Any:
        if dict.__contains__(self, name):
            return dict.__getitem__(self, name)

        value = self._getter(name)

        if value:
            dict.__setitem__(self, name, value)

        return value

    def __setitem__(self, name: str, value: Any) -> None:
        dict.__setitem__(self, name, value)
        self._setter(name, value)

    def __contains__(self, key: object) -> bool:
        if dict.__contains__(self, key):
            return True

        if not isinstance(key, str):
            return False

        value = self._getter(key)
        if value is None:
            return False

        dict.__setitem__(self, key, value)
        return True

