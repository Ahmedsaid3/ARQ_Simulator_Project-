# src/application.py
import config

class ApplicationLayer:
    """
    Simulates the Application Layer.
    Requirements:
    - Generate 100 MB of data [cite: 16]
    - Consume received data
    """
    def __init__(self, role):
        self.role = role # 'SENDER' or 'RECEIVER'
        
        # Sender Variables
        self.total_data_to_send = config.FILE_SIZE_BYTES
        self.bytes_generated = 0
        
        # Receiver Variables
        self.bytes_received = 0
        self.finish_time = None # To calculate Goodput

    def get_data(self, size):
        """
        Called by Transport Layer to get the next chunk of data.
        """
        if self.bytes_generated >= self.total_data_to_send:
            return None # End of File
            
        remaining = self.total_data_to_send - self.bytes_generated
        actual_size = min(size, remaining)
        
        # Create dummy data (e.g., repeating bytes)
        # We don't need real content, just correct size.
        data = b'A' * actual_size 
        
        self.bytes_generated += actual_size
        return data

    def receive_data(self, data):
        """
        Called by Transport Layer when data is delivered.
        """
        self.bytes_received += len(data)
        
        # Note: In a real system, we would write to disk here.
        # For simulation, we just count bytes.

    def is_finished(self):
        """
        Checks if the transfer is complete.
        """
        if self.role == 'SENDER':
            return False # Sender never "finishes" receiving
        return self.bytes_received >= self.total_data_to_send