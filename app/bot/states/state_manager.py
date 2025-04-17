import logging

from .models import State

class FSM:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "current_state"):
            self.chats = {}
    
    def get_state(self, chat_id) -> State:
        self.chats[chat_id] = self.chats.get(chat_id, State())
        return self.chats[chat_id]
        
    def set_state(self, chat_id, state: State):
        logging.info(state)
        self.chats[chat_id] = state