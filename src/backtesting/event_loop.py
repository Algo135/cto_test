from datetime import datetime
from typing import Callable, List
from collections import deque


class Event:
    def __init__(self, event_type: str, data: dict, timestamp: datetime):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp
    
    def __repr__(self):
        return f"Event({self.event_type}, {self.timestamp})"


class EventLoop:
    def __init__(self):
        self.event_queue = deque()
        self.handlers = {}
        self.is_running = False
    
    def register_handler(self, event_type: str, handler: Callable):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def put_event(self, event: Event):
        self.event_queue.append(event)
    
    def process_events(self):
        self.is_running = True
        
        while self.event_queue and self.is_running:
            event = self.event_queue.popleft()
            
            if event.event_type in self.handlers:
                for handler in self.handlers[event.event_type]:
                    handler(event)
    
    def stop(self):
        self.is_running = False
    
    def clear(self):
        self.event_queue.clear()
        self.handlers.clear()
