# src/physical.py
import random
import numpy as np # Numpy eklendi
import config

class GilbertElliotChannel:
    STATE_GOOD = 0
    STATE_BAD = 1

    def __init__(self):
        self.current_state = self.STATE_GOOD
        self.p_g = config.P_G
        self.p_b = config.P_B
        self.trans_g_to_b = config.TRANS_G_TO_B
        self.trans_b_to_g = config.TRANS_B_TO_G

    def is_packet_corrupted(self, packet_size_bytes):
        """
        Simulates the Gilbert-Elliot model bit-by-bit using 
        Geometric Distribution for performance (Jump-Ahead).
        """
        remaining_bits = packet_size_bytes * 8
        is_corrupted = False
        
        while remaining_bits > 0:
            # 1. Şu anki durumda ne kadar kalacağız? (Geometric Distribution)
            # "Kaç bit sonra durum değişecek?"
            if self.current_state == self.STATE_GOOD:
                transition_prob = self.trans_g_to_b
                current_ber = self.p_g
                next_state = self.STATE_BAD
            else:
                transition_prob = self.trans_b_to_g
                current_ber = self.p_b
                next_state = self.STATE_GOOD
            
            # Numpy ile bir sonraki geçişe kadar kaç bit geçeceğini çekiyoruz
            # (+1 ekliyoruz çünkü geometric dağılım 1'den başlar, biz bit sayıyoruz)
            bits_until_transition = np.random.geometric(transition_prob)
            
            # Bu segmentin uzunluğu (Paket bitiyor mu yoksa durum mu değişiyor?)
            segment_bits = min(remaining_bits, bits_until_transition)
            
            # 2. Bu segmentte hata oldu mu?
            # P(Error) = 1 - (1 - BER)^bits
            if not is_corrupted:
                prob_error = 1.0 - (1.0 - current_ber) ** segment_bits
                if random.random() < prob_error:
                    is_corrupted = True
                    # Hata bulundu, ama döngüyü kırmıyoruz çünkü 
                    # State'in (self.current_state) paketin sonunda ne olacağını 
                    # doğru güncellememiz lazım ki bir sonraki paket oradan devam etsin.
            
            # 3. İlerlet
            remaining_bits -= segment_bits
            
            # Eğer segment bittiğinde durum değişimi gerçekleştiyse state'i güncelle
            if remaining_bits > 0 or segment_bits == bits_until_transition:
                 self.current_state = next_state
                 
        return is_corrupted

# PhysicalLayer sınıfında bir değişiklik yapmana gerek yok, 
# çünkü o sadece channel.is_packet_corrupted() çağırıyor.
class PhysicalLayer:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.channel = GilbertElliotChannel()
        
        # --- BOTTLENECKS ---
        self.tx_busy_until = 0.0 
        self.rx_busy_until = {True: 0.0, False: 0.0}

    def transmit(self, packet, is_forward_path, receiver_callback):
        # NOT: Artık update_state() fonksiyonunu manuel çağırmıyoruz,
        # is_packet_corrupted içinde otomatik yapılıyor.
        
        # 1. Check Errors (ve State Update)
        corrupted = self.channel.is_packet_corrupted(packet.size_bytes)
        
        # ... (Geri kalan transmit kodları AYNI kalacak) ...
        # Transmit delay, propagation delay vb. hesaplamaları değiştirme.
        
        trans_delay = (packet.size_bytes * 8) / config.BIT_RATE
        prop_delay = config.PROPAGATION_DELAY_FWD if is_forward_path else config.PROPAGATION_DELAY_REV
        proc_delay = config.PROCESSING_DELAY
        
        current_time = self.event_manager.current_time
        
        start_tx = max(current_time, self.tx_busy_until)
        end_tx = start_tx + trans_delay
        self.tx_busy_until = end_tx
        
        arrival_at_rx_input = end_tx + prop_delay
        
        rx_free_time = self.rx_busy_until[is_forward_path]
        start_proc = max(arrival_at_rx_input, rx_free_time)
        end_proc = start_proc + proc_delay
        self.rx_busy_until[is_forward_path] = end_proc
        
        delivery_time = end_proc
        
        delay_from_now = delivery_time - current_time
        self.event_manager.schedule(delay_from_now, receiver_callback, args=(packet, corrupted))