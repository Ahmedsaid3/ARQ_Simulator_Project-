# main.py
import csv
import random
import time
import os
import config

# Import our modules
from src.event_manager import EventManager
from src.physical import PhysicalLayer
from src.link import LinkLayer
from src.transport import TransportLayer
from src.application import ApplicationLayer


def run_simulation(window_size, payload_size, seed, run_id):
    """
    Runs a SINGLE simulation with specific parameters.
    Returns: Stats dictionary (Goodput, etc.)
    """
    # 1. Setup Random Seed [cite: 61]
    random.seed(seed)
    
    # 2. Initialize Layers
    event_manager = EventManager()
    
    # Application
    app_sender = ApplicationLayer(role='SENDER')
    app_receiver = ApplicationLayer(role='RECEIVER')
    
    # Transport
    transport_sender = TransportLayer(app_sender)
    transport_receiver = TransportLayer(app_receiver)
    
    # Physical (Shared Channel)
    physical_layer = PhysicalLayer(event_manager)
    
    # Link (ARQ)
    # Note: Window Size is configurable [cite: 58]
    link_sender = LinkLayer(physical_layer, event_manager, transport_sender, window_size=window_size)
    link_receiver = LinkLayer(physical_layer, event_manager, transport_receiver, window_size=window_size)
    
    # 3. Wire them together
    # Sender Link -> Receiver Link (via Physical)
    link_sender.set_peer_callback(link_receiver.receive_frame_from_physical)
    
    # Receiver Link -> Sender Link (ACK path via Physical)
    link_receiver.set_peer_callback(link_sender.receive_frame_from_physical)
    
    # 4. Start Simulation Loop
    # Strategy: Sender Link Layer keeps pulling from Transport as long as window is open
    
    # Initial Kickstart: Try to send initial window
    # To do this, we need a driving loop or periodic check.
    # In Event-Driven, we can schedule a "Send More" event loop or just call it initially.
    
    def try_send_more():
        # L = Payload Size (Frame Payload).
        # Transport needs to fit into L - 24 bytes.
        # So we ask Transport for segments that fit into 'payload_size' (which is L).
        
        # As long as window is not full...
        while link_sender.next_seq_num < link_sender.send_base + link_sender.window_size:
            segment = transport_sender.create_segments(max_payload_size=payload_size)
            if segment is None:
                break # No more data
            
            link_sender.send(segment)
        
        # If we still have data, schedule next check
        if not app_receiver.is_finished():
             # Check again every 1ms (simulated polling)
            event_manager.schedule(0.001, try_send_more)

    # Start the sending process
    event_manager.schedule(0.0, try_send_more)
    
    # Run the Engine!
    start_real_time = time.time()
    
    # Limit simulation to avoid infinite loops (e.g., if Goodput is 0)
    # 100MB at 10Mbps takes ~80 seconds min. Let's give it 1000 simulated seconds max.
    MAX_SIM_TIME = 1000.0
    
    while event_manager.event_queue:
        event_manager.run_step() # We need to expose a single-step or check time
        # Since our event_manager.run() is a loop, we can't easily interrupt unless we modify it.
        # Let's rely on app_receiver.is_finished() inside handlers or events.
        
        # Better approach: Standard event_manager.run() runs until empty.
        # But "try_send_more" keeps refilling it. We need a stop condition.
        if app_receiver.is_finished():
            break
        
        if event_manager.current_time > MAX_SIM_TIME:
            break

    # --- Metrics Calculation [cite: 45-53] ---
    sim_duration = event_manager.current_time
    total_bytes = app_receiver.bytes_received
    
    # Goodput (Mbps) = (Bits Delivered) / (Time in Seconds) / 10^6
    goodput_mbps = (total_bytes * 8) / sim_duration / 1e6 if sim_duration > 0 else 0
    
    # YENİ: Detaylı Metrikler
    # Retransmission: Sender Link Layer'dan alıyoruz
    retransmissions = link_sender.total_retransmissions
    
    # Avg RTT: Sender Link Layer'dan ortalama alıyoruz
    avg_rtt = 0
    if link_sender.rtt_samples:
        avg_rtt = sum(link_sender.rtt_samples) / len(link_sender.rtt_samples)
        
    # Buffer Events: Receiver Transport Layer'dan alıyoruz
    buffer_events = transport_receiver.buffer_overflow_count
    
    # Utilization: (Goodput / Capacity) * 100 basit bir yaklaşımdır.
    # Kapasite 10 Mbps.
    utilization = (goodput_mbps / 10.0) * 100

    return {
        'W': window_size,
        'L': payload_size,
        'run_id': run_id,
        'goodput_mbps': goodput_mbps,
        # Yeni sütunlar:
        'retransmissions': retransmissions,
        'avg_rtt': avg_rtt,
        'utilization': utilization,
        'buffer_events': buffer_events,
        'duration': sim_duration
    }

# --- Main Execution Block ---
if __name__ == "__main__":
    # Parameters from [cite: 58-60]
    W_VALUES = [2, 4, 8, 16, 32, 64]
    L_VALUES = [128, 256, 512, 1024, 2048, 4096]    

    # Recommendation: Test W in [64, 128, 256]
    # Recommendation: Focus on L in [256, 512, 1024]
    # W_VALUES = [64, 128, 256]
    # L_VALUES = [256, 512, 1024]

    RUNS_PER_CONFIG = 10 # [cite: 61]
    
    results = []
    
    print("Starting Simulation... (This may take a while)")
    
    # Create results directory
    os.makedirs("results", exist_ok=True)
    
    total_sims = len(W_VALUES) * len(L_VALUES) * RUNS_PER_CONFIG
    current_sim = 0
    
    with open('results/simulation_data_test.csv', 'w', newline='') as csvfile:
        fieldnames = ['W', 'L', 'run_id', 'goodput_mbps', 'retransmissions', 'avg_rtt', 'utilization', 'buffer_events', 'duration']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for W in W_VALUES:
            for L in L_VALUES:
                for run_id in range(RUNS_PER_CONFIG):
                    current_sim += 1
                    # Use a deterministic seed for reproducibility
                    seed = (W * 10000) + (L * 100) + run_id
                    
                    stats = run_simulation(W, L, seed, run_id)
                    results.append(stats)
                    writer.writerow(stats)
                    
                    print(f"[{current_sim}/{total_sims}] W={W}, L={L} -> Goodput={stats['goodput_mbps']:.3f} Mbps")

    print("Simulation Complete. Results saved to results/simulation_data_test.csv")