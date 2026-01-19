# config.py

"""
Global Configuration Parameters based on Assignment Specification.
Reference: BLG 337E Assignment 2 PDF
"""

# --- SYSTEM CONSTRAINTS ---
# "Accepts a large data file (fixed at 100 MB)" [cite: 16]
FILE_SIZE_BYTES = 100 * 1024 * 1024 

# "Application-side buffer capacity is fixed at 256 KB" [cite: 20]
RECEIVER_BUFFER_SIZE = 256 * 1024 

# --- PROTOCOL OVERHEADS ---
# "Transport header size fixed at 8 bytes" [cite: 17]
TRANSPORT_HEADER_SIZE = 8

# "Link Layer header overhead fixed at 24 bytes per frame" [cite: 31]
LINK_HEADER_SIZE = 24

# --- PHYSICAL LAYER (BASELINE PARAMETERS) ---
# "Bit Rate: R = 10 Mbps" [cite: 34]
BIT_RATE = 10 * 10**6  

# Delays from Table 1 [cite: 36-37]
PROPAGATION_DELAY_FWD = 0.040  # 40 ms (Forward path)
PROPAGATION_DELAY_REV = 0.010  # 10 ms (Reverse path/ACK)
PROCESSING_DELAY = 0.002       # 2 ms (Per frame)

# --- ERROR MODEL (GILBERT-ELLIOT) ---
# Parameters from Table 2 [cite: 39-40]
P_G = 1e-6           # Good-state BER
P_B = 5e-3           # Bad-state BER
TRANS_G_TO_B = 0.002 # P(G->B)
TRANS_B_TO_G = 0.05  # P(B->G)