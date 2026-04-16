from ..utils import Logger
from typing import Any
import json
import os

log = Logger('ConfigStore')

class _TrackedList(list):
    def __init__(self, values, save_callback):
        super().__init__(values)
        self._save_callback = save_callback

    def _save(self):
        self._save_callback()

    def append(self, value):
        super().append(value)
        self._save()

    def extend(self, values):
        super().extend(values)
        self._save()

    def insert(self, index, value):
        super().insert(index, value)
        self._save()

    def remove(self, value):
        super().remove(value)
        self._save()

    def pop(self, index=-1, /):
        value = super().pop(index)
        self._save()
        return value

    def clear(self):
        super().clear()
        self._save()

    def sort(self, *args, **kwargs):
        super().sort(*args, **kwargs)
        self._save()

    def reverse(self):
        super().reverse()
        self._save()

    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self._save()

    def __delitem__(self, index):
        super().__delitem__(index)
        self._save()

class ConfigStore(dict):
    def __init__(self, file="config.json", values=None):
        log.trace(f'ConfigStore({file=},{values=})')
        super().__init__()
        self.file = file
        self._save_enabled = False

        if values:
            self.update(values)

        if not os.path.exists(self.file):
            if os.path.dirname(self.file):
                os.makedirs(os.path.dirname(self.file), exist_ok=True)
            self._save_enabled = True
            self._save()
            return

        with open(self.file, 'rb') as f:
            self.update(json.load(f))

        self._save_enabled = True

    def _wrap_value(self, value: Any):
        if isinstance(value, list):
            return _TrackedList(value, self._save)
        return value

    def _save(self):
        with open(self.file, 'w') as f:
            json.dump(self, f)

    def __setitem__(self, key: Any, value: Any):
        super().__setitem__(key, self._wrap_value(value))
        if self._save_enabled:
            self._save()

    def update(self, *args, **kwargs):
        other = dict(*args, **kwargs)
        for key, value in other.items():
            super().__setitem__(key, self._wrap_value(value))
        if self._save_enabled:
            self._save()
