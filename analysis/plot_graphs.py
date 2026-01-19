# analysis/plot_graphs.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def plot_heatmap(csv_path, output_path):
    # 1. Veriyi Oku
    if not os.path.exists(csv_path):
        print(f"HATA: {csv_path} bulunamadı. Önce simülasyonu çalıştırın.")
        return

    df = pd.read_csv(csv_path)

    # 2. Veriyi Grupla ve Ortalamasını Al
    # Her (W, L) çifti için 10 farklı deneme (run_id) yapmıştık.
    # Analiz için bu 10 denemenin ortalamasını (mean) kullanıyoruz.
    pivot_table = df.pivot_table(
        index='W',             # Y Ekseninde Window Size olacak
        columns='L',           # X Ekseninde Payload Size olacak
        values='goodput_mbps', # Renkler Goodput değerini gösterecek
        aggfunc='mean'         # Ortalamasını al
    )

    # Veriyi görselleştirmeden önce konsola basalım (Kontrol için)
    print("--- Ortalama Goodput Değerleri (Mbps) ---")
    print(pivot_table)

    # 3. Heatmap Çiz
    plt.figure(figsize=(10, 8))
    
    # Seaborn Heatmap
    # annot=True: Kutucukların üzerine sayıları yazar
    # fmt=".3f": Sayıları virgülden sonra 3 basamak gösterir
    # cmap="viridis" veya "RdYlGn": Renk paleti (Kırmızı-Sarı-Yeşil iyidir)
    sns.heatmap(
        pivot_table, 
        annot=True, 
        fmt=".3f", 
        cmap="RdYlGn", 
        linewidths=.5,
        cbar_kws={'label': 'Goodput (Mbps)'}
    )

    # 4. Eksenleri ve Başlığı Ayarla
    # Ödevde grafik eksenlerinin W ve L olması isteniyor [cite: 67]
    plt.title('Goodput Performance Heatmap (Mbps)\nSelective Repeat ARQ Simulation', fontsize=14)
    plt.ylabel('Window Size (W)', fontsize=12)
    plt.xlabel('Payload Size (L) [Bytes]', fontsize=12)
    
    # Y eksenini ters çevir (Küçük W altta, Büyük W üstte olsun - genelde böyle istenir)
    plt.gca().invert_yaxis()

    # 5. Kaydet
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nGrafik başarıyla kaydedildi: {output_path}")
    
    # Ekranda göster (Eğer masaüstü ortamındaysan)
    # plt.show()

if __name__ == "__main__":
    # Dosya yollarını ayarla
    # main.py ana dizinde olduğu için results klasörü de ana dizindedir.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Bir üst dizine çıkıp results klasörünü buluyoruz
    project_root = os.path.dirname(current_dir) 
    
    csv_file = os.path.join(project_root, 'results', 'simulation_data.csv')
    output_image = os.path.join(project_root, 'results', 'figures', 'test.png')

    plot_heatmap(csv_file, output_image)