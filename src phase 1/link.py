# src/link.py
import config
from src.packet import LinkFrame

class LinkLayer:
    """
    Implements Selective Repeat ARQ Protocol.
    Reference: PDF Phase 1, Section 1 
    """
    def __init__(self, physical_layer, event_manager, transport_layer=None, window_size=4):
        self.physical = physical_layer
        self.event_manager = event_manager
        self.transport = transport_layer 
        self.window_size = window_size
        
        # --- SENDER STATE ---
        self.send_buffer = []       # Queue of segments waiting to be sent
        self.next_seq_num = 0       # Next sequence number to use
        self.send_base = 0          # Oldest unacknowledged frame
        self.sent_frames = {}       # Buffer of sent frames (for retransmission): {seq: frame}
        self.ack_received = set()   # Set of received ACKs
        self.timers = {}            # Active timers: {seq: event}
        
        # Timeout Value (Fixed for Phase 1, Adaptive for Phase 2)
        # 100ms is a safe start (RTT is ~50ms)
        self.timeout_interval = 0.1 

        # YENİ EKLENEN: İstatistikler
        self.total_retransmissions = 0
        self.rtt_samples = []       # RTT ölçümlerini saklayacağız
        self.send_times = {}        # {seq_num: timestamp} - Gönderim anı

        # --- RECEIVER STATE ---
        self.rcv_base = 0           # Expected sequence number
        self.rcv_buffer = {}        # Buffered out-of-order frames: {seq: payload}
        
        # To connect two link layers (Sender <-> Receiver)
        self.peer_receive_callback = None

    def set_peer_callback(self, callback_func):
        """
        Sets the function to call on the 'other side' when a packet arrives.
        """
        self.peer_receive_callback = callback_func

    # ==========================
    # SENDER LOGIC
    # ==========================

    def send(self, transport_segment):
        """
        Called by Transport Layer to send a segment.
        """
        self.send_buffer.append(transport_segment)
        self._process_send_buffer()


    def _process_send_buffer(self):
        """
        Sends frames as long as the window is open.
        Constraint: next_seq_num < send_base + window_size [cite: 30]
        """
        while self.send_buffer and (self.next_seq_num < self.send_base + self.window_size):
            segment = self.send_buffer.pop(0)
            seq = segment.seq_num
            
            # Create Link Frame (Overhead added automatically in Packet class)
            frame = LinkFrame(seq, type_flag='DATA', payload=segment)
            
            self.sent_frames[seq] = frame
            self.next_seq_num += 1
            
            self._transmit_frame(frame)

    def _transmit_frame(self, frame):
        """
        Helper to transmit a frame and start its timer.
        """

        # YENİ: İlk gönderimse zamanı kaydet (RTT için)
        if frame.seq_num not in self.send_times:
            self.send_times[frame.seq_num] = self.event_manager.current_time

        # Start Timer [cite: 27]
        self._start_timer(frame.seq_num)
        
        # Send via Physical Layer
        if self.peer_receive_callback:
            # Note: For simulation, we assume 'Forward' path. 
            # In a full duplex, we might need more logic.
            self.physical.transmit(frame, is_forward_path=True, receiver_callback=self.peer_receive_callback)

    def _start_timer(self, seq_num):
        """
        Schedules a timeout event for a specific frame.
        """
        # Cancel existing timer if any (for retransmissions)
        if seq_num in self.timers:
            self.event_manager.cancel_event(self.timers[seq_num])
            
        event = self.event_manager.schedule(
            self.timeout_interval, 
            self._handle_timeout, 
            args=(seq_num,)
        )
        self.timers[seq_num] = event

    def _handle_timeout(self, seq_num):
        """
        Callback when a timer expires.
        Resends ONLY the specific lost frame (Selective Repeat). [cite: 29]
        """
        if seq_num in self.ack_received:
            return # Already ACKed, ignore

        # Retransmit
        if seq_num in self.sent_frames:
            frame = self.sent_frames[seq_num]
            frame.retry_count += 1

            # YENİ: Retransmission sayacını artır
            self.total_retransmissions += 1

            self._transmit_frame(frame)

    def receive_ack(self, ack_seq_num):
        # YENİ: RTT Hesaplama
        # Eğer bu paket için gönderim zamanı kayıtlıysa
        if ack_seq_num in self.send_times:
            send_time = self.send_times[ack_seq_num]
            arrival_time = self.event_manager.current_time
            rtt = arrival_time - send_time
            self.rtt_samples.append(rtt)
            
            # Kaydı sil (tekrar hesaplamamak için)
            del self.send_times[ack_seq_num]


        self.ack_received.add(ack_seq_num)
        
        # Cancel timer for this frame
        if ack_seq_num in self.timers:
            self.event_manager.cancel_event(self.timers[ack_seq_num])
            del self.timers[ack_seq_num]

        # Slide Window [cite: 30]
        # If we ACKed the base, move base forward to the next unACKed frame
        if ack_seq_num == self.send_base:
            while self.send_base in self.ack_received:
                # Clean up memory
                if self.send_base in self.sent_frames:
                    del self.sent_frames[self.send_base]
                self.send_base += 1
            
            # Window moved, try to send more data
            self._process_send_buffer()

    # ==========================
    # RECEIVER LOGIC
    # ==========================

    def receive_frame_from_physical(self, packet, corrupted):
        """
        Called by Physical Layer when a packet arrives.
        """
        if corrupted:
            # In ARQ, corrupted frames are silently dropped.
            # Sender will timeout and retransmit.
            return 

        if packet.type == 'ACK':
            self.receive_ack(packet.seq_num)
            
        elif packet.type == 'DATA':
            self._handle_incoming_data(packet)

    def _handle_incoming_data(self, frame):
        seq = frame.seq_num
        
        # 1. Send ACK (Selective Repeat sends ACK for every correct frame)
        self._send_ack(seq)

        # 2. Check Window Validity
        # We accept frames within [rcv_base, rcv_base + window_size - 1]
        if self.rcv_base <= seq < (self.rcv_base + self.window_size):
            # Buffer the frame [cite: 28]
            if seq not in self.rcv_buffer:
                self.rcv_buffer[seq] = frame.payload
            
            # 3. Deliver In-Order Data to Transport
            while self.rcv_base in self.rcv_buffer:
                data_segment = self.rcv_buffer[self.rcv_base]
                
                # --- FLOW CONTROL / BACKPRESSURE CHECK [cite: 21-22] ---
                if self.transport:
                    accepted = self.transport.receive_segment(data_segment)
                    if not accepted:
                        # Transport buffer is full! 
                        # We cannot deliver this packet. 
                        # Strategy: Drop it (or don't remove from buffer & don't advance base).
                        # Effectively, we stop sliding the window.
                        break 
                
                # If accepted, remove from buffer and slide window
                del self.rcv_buffer[self.rcv_base]
                self.rcv_base += 1
                
        elif seq < self.rcv_base:
            # Duplicate/Old frame. We already ACKed it, but ACK might be lost.
            # So we ACK again (Step 1 handles this).
            pass

    def _send_ack(self, seq_num):
        ack_frame = LinkFrame(seq_num, type_flag='ACK')
        
        # Send back (Reverse path)
        if self.peer_receive_callback:
            self.physical.transmit(ack_frame, is_forward_path=False, receiver_callback=self.peer_receive_callback)