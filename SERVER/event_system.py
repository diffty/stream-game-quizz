from typing import Callable


class EventSystem:
    _instance = None

    signals = {}

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def connect(self, signal_name, callback):
        if not callable(callback):
            raise Exception(f"Callback argument is not a callable (Type: {type(callback)})")
        
        if signal_name not in EventSystem.signals:
            EventSystem.signals[signal_name] = []

        EventSystem.signals[signal_name].append(callback)
        
    def emit(self, signal_name, *args):
        for callback in EventSystem.signals.get(signal_name, []):
            callback(*args)
