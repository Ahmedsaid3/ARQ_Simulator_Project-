# src/packet.py
import time

class Packet:
    """Base class for any data unit in the network."""
    def __init__(self, size_bytes):
        self.size_bytes = size_bytes
        self.creation_time = time.time()  # Useful for debugging, strictly simulation time will be used in event loop

class TransportSegment(Packet):
    """
    Represents a segment created by the Transport Layer.
    Consists of a header and a payload (application data).
    """
    def __init__(self, seq_num, data):
        # The size is the data length + fixed transport header (8 bytes)
        super().__init__(len(data) + 8) 
        self.seq_num = seq_num      # Sequence number for reassembly
        self.data = data            # The actual file chunk
        self.is_last = False        # Flag to indicate the end of the file

    def __repr__(self):
        return f"Seg(seq={self.seq_num}, size={self.size_bytes})"

class LinkFrame(Packet):
    """
    Represents a frame created by the Link Layer (ARQ).
    Wraps a TransportSegment or carries control info (ACK/NACK).
    """
    def __init__(self, seq_num, type_flag, payload=None):
        """
        seq_num: Frame sequence number (for ARQ sliding window)
        type_flag: 'DATA' or 'ACK'
        payload: The TransportSegment object (if DATA) or None (if ACK)
        """
        # Header size is fixed 24 bytes. 
        # If there is payload, add its size. If ACK, just header.
        total_size = 24 + (payload.size_bytes if payload else 0)
        super().__init__(total_size)
        
        self.seq_num = seq_num
        self.type = type_flag   # 'DATA' or 'ACK'
        self.payload = payload  # This contains the TransportSegment
        self.retry_count = 0    # How many times this frame has been retransmitted

    def __repr__(self):
        return f"Frame(seq={self.seq_num}, type={self.type}, retry={self.retry_count})"