# src/event_manager.py
import heapq

class Event:
    def __init__(self, timestamp, handler, args=()):
        self.timestamp = timestamp
        self.handler = handler  # Function to execute
        self.args = args        # Arguments for the function
        self.canceled = False   # To support timer cancellation

    # Comparison for Priority Queue (Min-Heap)
    def __lt__(self, other):
        return self.timestamp < other.timestamp

class EventManager:
    """
    Discrete Event Simulator Engine.
    Manages the global simulation clock and event queue.
    """
    def __init__(self):
        self.current_time = 0.0
        self.event_queue = []

    def schedule(self, delay, handler, args=()):
        """
        Schedules an event to run after 'delay' seconds.
        Returns the Event object (so it can be canceled if needed).
        """
        timestamp = self.current_time + delay
        event = Event(timestamp, handler, args)
        heapq.heappush(self.event_queue, event)
        return event

    def cancel_event(self, event):
        """
        Marks an event as canceled. It will be ignored when popped.
        """
        if event:
            event.canceled = True

    def run_step(self):
        """
        Executes a single event from the queue.
        Returns True if an event was executed, False if queue is empty.
        """
        if not self.event_queue:
            return False
            
        event = heapq.heappop(self.event_queue)
        
        if event.canceled:
            return True # Event processed (ignored), continue
            
        self.current_time = event.timestamp
        event.handler(*event.args)
        return True

    def run(self):
        """
        Runs until queue is empty.
        """
        while self.event_queue:
            self.run_step()