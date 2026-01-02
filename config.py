# config.py

"""
Configuration file containing all fixed baseline parameters 
for the ARQ Simulator project.
"""

# --- Physical Layer Parameters ---
BIT_RATE = 10 * 10**6       # 10 Mbps (bits per second)
PROPAGATION_DELAY_FWD = 0.040  # 40 ms (Forward path)
PROPAGATION_DELAY_REV = 0.010  # 10 ms (Reverse path/ACK)
PROCESSING_DELAY = 0.002       # 2 ms (Per frame processing)

# --- Gilbert-Elliot Error Model Parameters ---
# P_G: Bit Error Rate (BER) in Good state
P_G = 1e-6          
# P_B: Bit Error Rate (BER) in Bad state
P_B = 5e-3          
# Transition probabilities
TRANS_G_TO_B = 0.002    # Probability of transition from Good to Bad
TRANS_B_TO_G = 0.05     # Probability of transition from Bad to Good

# --- Application Layer Constraints ---
FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB total data to send
RECEIVER_BUFFER_SIZE = 256 * 1024    # 256 KB receiver buffer limit

# --- Protocol Headers (Overhead) ---
TRANSPORT_HEADER_SIZE = 8  # bytes (Transport Layer)
LINK_HEADER_SIZE = 24      # bytes (Link Layer / ARQ)

# --- Simulation Settings ---
# Default timeout value (can be optimized later)
DEFAULT_TIMEOUT = 0.1 # 100 ms placeholder