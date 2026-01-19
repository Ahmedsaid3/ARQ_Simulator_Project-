# src/packet.py
import config

class TransportSegment:
    """
    Represents a segment created by the Transport Layer.
    Structure: [Transport Header (8B)] + [Payload (Data)]
    """
    def __init__(self, seq_num, data):
        self.seq_num = seq_num
        self.data = data # The actual file chunk
        
        # Size Calculation: Data Length + 8 Bytes Header [cite: 17]
        self.size_bytes = len(data) + config.TRANSPORT_HEADER_SIZE

class LinkFrame:
    """
    Represents a frame created by the Link Layer (ARQ).
    Structure: [Link Header (24B)] + [TransportSegment OR None]
    """
    def __init__(self, seq_num, type_flag, payload=None):
        self.seq_num = seq_num
        self.type = type_flag   # 'DATA' or 'ACK'
        self.payload = payload  # This is the TransportSegment object
        self.retry_count = 0    # For tracking retransmissions
        
        # Size Calculation[cite: 31]:
        # Base overhead is 24 bytes.
        # If carrying data, add the payload's TOTAL size (which includes Transport Header).
        self.size_bytes = config.LINK_HEADER_SIZE
        if self.payload:
            self.size_bytes += self.payload.size_bytes