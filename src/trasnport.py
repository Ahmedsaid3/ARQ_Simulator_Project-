from packet import TransportSegment
import config

class TransportLayer:
    """
    Transport Layer Shim.
    Responsible for Segmentation, Reassembly, and Flow Control (Buffer).
    """
    def __init__(self, app_layer):
        self.app_layer = app_layer
        
        # Sender state
        self.next_seq_num = 0
        
        # Receiver state
        self.expected_seq_num = 0
        self.receiver_buffer = {}  # Buffer for out-of-order segments: {seq_num: data}
        self.current_buffer_usage = 0 # in bytes
        
    def create_segment(self, max_payload_size):
        """
        Fetches data from Application Layer and wraps it in a TransportSegment.
        """
        # Get data chunk from App (payload size limit)
        data = self.app_layer.get_chunk(max_payload_size)
        
        if data is None:
            return None # No more data to send
            
        # Create the segment
        segment = TransportSegment(self.next_seq_num, data)
        self.next_seq_num += 1
        
        return segment

    def receive_segment(self, segment):
        """
        Called by Link Layer when a segment arrives.
        Returns True if accepted, False if dropped (due to buffer overflow).
        """
        # 1. Check Buffer Space
        # Note: We consider the payload size for buffer usage
        seg_size = len(segment.data)
        
        if self.current_buffer_usage + seg_size > config.RECEIVER_BUFFER_SIZE:
            # Buffer Overflow! Drop the packet or signal backpressure.
            # In this simulation, we return False to indicate rejection.
            return False

        # 2. Process Segment
        if segment.seq_num == self.expected_seq_num:
            # Expected packet arrived. Pass to Application immediately.
            self.app_layer.receive_data(segment.data)
            self.expected_seq_num += 1
            
            # 3. Check buffered packets (if any filled the hole)
            while self.expected_seq_num in self.receiver_buffer:
                data = self.receiver_buffer.pop(self.expected_seq_num)
                self.app_layer.receive_data(data)
                self.current_buffer_usage -= len(data) # Remove from buffer accounting
                self.expected_seq_num += 1
                
        elif segment.seq_num > self.expected_seq_num:
            # Out-of-order packet. Store in buffer.
            if segment.seq_num not in self.receiver_buffer:
                self.receiver_buffer[segment.seq_num] = segment.data
                self.current_buffer_usage += seg_size
                
        # If seq_num < expected, it's a duplicate. We can ignore or ACK again.
        # Ideally, Link Layer handles ACKs, Transport just consumes data.
        
        return True

    def is_buffer_full(self):
        """
        Helper for Link Layer to check backpressure before forwarding.
        """
        # A simple threshold check. Maybe allow a small margin.
        return self.current_buffer_usage >= config.RECEIVER_BUFFER_SIZE