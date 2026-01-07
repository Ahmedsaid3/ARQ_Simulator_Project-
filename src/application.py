import os

class ApplicationLayer:
    """
    Simulates the Application Layer.
    Sender: Provides data to the Transport Layer.
    Receiver: Consumes data from the Transport Layer.
    """
    def __init__(self, total_data_size):
        # Total size to send (e.g., 100 MB)
        self.total_data_to_send = total_data_size
        self.bytes_sent = 0
        self.bytes_received = 0
        
        # We will use a simple dummy data pattern
        self.dummy_data_pattern = b'ABCDEFGH' * 128  # 1 KB chunk pattern

    def get_chunk(self, size):
        """
        Called by Transport Layer to get the next chunk of data.
        Returns bytes or None if all data has been sent.
        """
        if self.bytes_sent >= self.total_data_to_send:
            return None
        
        # Calculate how much acts remains
        remaining = self.total_data_to_send - self.bytes_sent
        actual_size = min(size, remaining)
        
        # Create dummy data for this chunk
        # (In a real scenario, this would read from a file)
        chunk = self.dummy_data_pattern[:actual_size]
        
        # Should we pad it if it's shorter than pattern? 
        # For simulation, just repeating pattern is enough to fill size.
        while len(chunk) < actual_size:
            chunk += self.dummy_data_pattern
        chunk = chunk[:actual_size]

        self.bytes_sent += actual_size
        return chunk

    def receive_data(self, data):
        """
        Called by Transport Layer when data is delivered successfully.
        """
        self.bytes_received += len(data)
        # In a real app, we would write 'data' to a file here.
        
    def is_transfer_complete(self):
        return self.bytes_received >= self.total_data_to_send

    def get_progress(self):
        return (self.bytes_received / self.total_data_to_send) * 100