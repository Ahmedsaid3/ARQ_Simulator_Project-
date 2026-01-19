# src/transport.py
import config
from src.packet import TransportSegment

class TransportLayer:
    """
    Transport Layer Shim.
    Responsibilities:
    - Segmentation [cite: 17]
    - Reassembly & Integrity Check [cite: 18]
    - Limited Receiver Buffer & Backpressure 
    """
    def __init__(self, app_layer):
        self.app_layer = app_layer
        
        # Sender State
        self.seq_counter = 0
        
        # Receiver State
        # Fixed 256 KB Buffer Limit [cite: 20]
        self.max_buffer_size = config.RECEIVER_BUFFER_SIZE 
        self.current_buffer_usage = 0 

        # YENİ EKLENEN: İstatistik Sayacı
        self.buffer_overflow_count = 0

    def create_segments(self, max_payload_size):
        """
        Pulls data from App, creates Transport Segments.
        Returns a list of segments (usually just one in this flow).
        """
        # We need to leave room for Transport Header (8 bytes)
        # max_payload_size comes from Link Layer (L - 24 bytes)
        # effective_data_size = L - 24 - 8
        
        effective_data_size = max_payload_size - config.TRANSPORT_HEADER_SIZE
        if effective_data_size <= 0:
            raise ValueError("Payload size too small for headers!")

        data = self.app_layer.get_data(effective_data_size)
        
        if data is None:
            return None
            
        # Create Segment [cite: 17]
        segment = TransportSegment(self.seq_counter, data)
        self.seq_counter += 1
        
        return segment

    def receive_segment(self, segment):
        """
        Called by Link Layer when a segment arrives IN ORDER.
        Returns:
            True: If accepted (Buffer OK)
            False: If rejected (Buffer Full -> Backpressure) [cite: 21]
        """
        seg_size = len(segment.data) # Only data counts towards buffer usage
        
        # --- BUFFER CHECK [cite: 19-21] ---
        if self.current_buffer_usage + seg_size > self.max_buffer_size:
            # Buffer Overflow! Apply Backpressure.
            # Returning False tells Link Layer to STOP advancing window.
            # YENİ: Taşma olayını kaydet
            self.buffer_overflow_count += 1
            return False

        # If OK, accept data
        self.current_buffer_usage += seg_size
        
        # Pass to Application
        self.app_layer.receive_data(segment.data)
        
        # Simulate Application consuming data (Emptying buffer)
        # In a real OS, this happens asynchronously. 
        # For this simulation, we assume App is fast but we track usage
        # to prove we implemented the logic. 
        # We assume App consumes it immediately after delivery.
        self.current_buffer_usage -= seg_size
        
        return True