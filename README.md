Harika bir proje ortaya çıkardın, bunu GitHub'da sunarken profesyonel ve anlaşılır bir README dosyası projenin kalitesini doğrudan yansıtır.

Senin için **BLG 337E** standartlarına uygun, hem teknik detayları içeren hem de "nasıl çalıştırılır" kısmını adım adım anlatan bir `README.md` hazırladım.

Bunu kopyalayıp projenin ana dizinine `README.md` ismiyle kaydetmen yeterli.

---

```markdown
# Cross-Layer Performance Optimization of a Custom ARQ Protocol
**BLG 337E: Principles of Computer Communication - Assignment 2**

This project implements a discrete-event simulation of a **Selective Repeat ARQ** protocol over a link with **Gilbert-Elliot burst errors**. The primary goal is to optimize the "Goodput" metric under high-latency and high-bandwidth conditions using **AI-assisted engineering**.

## 🚀 Features

* **Custom Network Simulation:** Implements Transport Layer segmentation, Link Layer ARQ, and Physical Layer error modeling from scratch.
* **Gilbert-Elliot Channel:** Simulates realistic burst error conditions ($P_{bad} \approx 10^{-2}$).
* **AI-Assisted Optimization:** Includes an **Adaptive Timeout (Jacobson's Algorithm)** mechanism developed with AI assistance to solve "Premature Timeout" issues at high window sizes.
* **Performance Analysis:** Generates heatmaps and CSV logs comparing Baseline (Fixed Timeout) vs. Optimized (Adaptive Timeout) protocols.

## 📂 Project Structure

```text
.
├── src/
│   ├── __init__.py
│   ├── link.py          # Link Layer logic (ARQ, Adaptive Timeout)
│   ├── packet.py        # Frame and Segment definitions
│   ├── physical.py      # Gilbert-Elliot Error Model
│   ├── transport.py     # Transport Layer (Flow control, Segmentation)
│   └── utils.py         # Event Manager & Helper classes
├── results/             # Simulation output (CSVs and Plots)
├── config.py            # Global simulation parameters (W, L, Bandwidth, RTT)
├── main.py              # Entry point to run simulations
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation

```

## 🛠️ Installation & Setup

1. **Clone the Repository**
```bash
git clone [https://github.com/KULLANICI_ADIN/REPO_ISMIN.git](https://github.com/KULLANICI_ADIN/REPO_ISMIN.git)
cd REPO_ISMIN

```


2. **Create a Virtual Environment (Optional but Recommended)**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

```


3. **Install Dependencies**
This project requires `matplotlib` and `pandas` for data visualization.
```bash
pip install -r requirements.txt

```


*(If `requirements.txt` is missing, run: `pip install matplotlib pandas numpy`)*

## ▶️ How to Run

To run the simulation and generate performance results:

1. **Configure Parameters:**
Open `config.py` (or `main.py` depending on your setup) to adjust simulation settings:
* `WINDOW_SIZES`: List of window sizes to test (e.g., `[64, 128, 256]`).
* `PAYLOAD_SIZES`: List of payload sizes (e.g., `[256, 512, 1024]`).


2. **Run the Simulation:**
Make sure you are in the root directory of the project:
```bash
python main.py

```


3. **View Results:**
After the simulation completes, check the `results/` folder for:
* `simulation_results.csv`: Raw data (Goodput, RTT, Retransmissions).
* `heatmap.png`: Visual representation of performance.



## 📊 Optimization Results

The project compares two phases:

* **Phase 1 (Baseline):** Uses a fixed timeout. Performance collapses at  due to queuing delays.
* **Phase 2 (Optimized):** Uses **Adaptive Timeout**. Successfully recovers throughput at  (Goodput improved by >6000%).

## 👥 Authors

* **Ahmed Said Gülşen** - *Istanbul Technical University*
* **Furkan Yalçın** - *Istanbul Technical University*

## 📜 License

This project is developed for educational purposes within the scope of BLG 337E course.

```

*(Bunu yaparken venv aktif olsun, yoksa bilgisayarındaki gereksiz her şeyi listeye ekler. Sadece `matplotlib`, `pandas`, `numpy` eklesen de yeter elle.)*
