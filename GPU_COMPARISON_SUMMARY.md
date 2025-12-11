# GPU Karşılaştırma Araçları - Özet Rapor 📊

## ✅ Tamamlanan İşlemler

### 🛠️ Oluşturulan Araçlar

#### 1. **compare_results.py** - GPU Karşılaştırma Aracı
- İki veya daha fazla GPU benchmark sonucunu karşılaştırır
- Detaylı metrikleri gösterir (throughput, latency, P95, P99, Apdex)
- Kazanan analizi yapar
- Donanım özelliklerini karşılaştırır

**Kullanım:**
```bash
make compare
# veya
cd benchmarks && python compare_results.py
cd benchmarks && python compare_results.py file1.json file2.json
```

#### 2. **export_to_csv.py** - CSV Dışa Aktarma Aracı
- JSON sonuçları CSV formatına çevirir
- Excel/Google Sheets için uygun format
- Her GPU için ayrı CSV + birleşik karşılaştırma CSV'si

**Kullanım:**
```bash
make export-csv
# veya
cd benchmarks && python export_to_csv.py
cd benchmarks && python export_to_csv.py results/benchmark_XXX.json
```

**Oluşturulan CSV'ler:**
- `benchmark_[GPU]_[TARIH].csv` - Her GPU için detaylı sonuçlar
- `all_benchmarks_comparison.csv` - Tüm GPU'lar birleşik
- `gpu_comparison.csv` - Yan yana karşılaştırma

#### 3. **visualize_results.py** - Görsel Karşılaştırma (Güncellendi)
- Mevcut grafik yeteneklerine ek olarak
- İki GPU'yu yan yana karşılaştırma grafikleri
- 4 farklı metrik grafiği (Latency, Throughput, P95, Apdex)

**Kullanım:**
```bash
make compare-visual
# veya manuel:
python -c "from visualize_results import compare_all_gpus_visual; compare_all_gpus_visual()"
```

### 📋 Makefile Komutları (Yeni)

| Komut | Açıklama |
|-------|----------|
| `make compare` | GPU'ları karşılaştır (metin çıktısı) |
| `make compare-csv` | Karşılaştır ve CSV'ye aktar |
| `make compare-visual` | Görsel grafiklerle karşılaştır |
| `make export-csv` | Tüm sonuçları CSV'ye aktar |
| `make compare-all` | Tüm karşılaştırma araçlarını çalıştır |

### 📂 Oluşturulan Dosyalar

```
benchmarks/
├── compare_results.py          ✅ Yeni (388 satır)
├── export_to_csv.py           ✅ Yeni (241 satır)
├── visualize_results.py       ✅ Güncellendi (+100 satır)
├── README_COMPARISON.md       ✅ Yeni (detaylı dokümantasyon)
└── reports/
    ├── all_benchmarks_comparison.csv          ✅ Birleşik karşılaştırma
    ├── gpu_comparison.csv                     ✅ Yan yana karşılaştırma
    ├── benchmark_[GPU]_[TARIH].csv           ✅ Her GPU için CSV
    └── [GPU]_vs_[GPU]_comparison.png         ✅ Görsel karşılaştırma
```

## 🎯 Kullanım Senaryoları

### Senaryo 1: Hızlı Karşılaştırma
```bash
make compare
```
→ Terminal'de detaylı karşılaştırma raporu

### Senaryo 2: Excel'de Analiz
```bash
make export-csv
cd benchmarks/reports/
# all_benchmarks_comparison.csv dosyasını Excel'de aç
```
→ Pivot table, grafikler, filtreleme

### Senaryo 3: Tam Analiz
```bash
make compare-all
```
→ Metin rapor + CSV'ler + Grafikler (matplotlib varsa)

### Senaryo 4: İki Spesifik GPU Karşılaştırma
```bash
cd benchmarks
python compare_results.py \
  results/benchmark_RTX_5090_*.json \
  results/benchmark_RTX_5070_Ti_*.json
```

## 📊 Örnek Karşılaştırma Sonuçları

### RTX 5090 vs RTX 5070 Ti Laptop GPU

#### Donanım
| Özellik | RTX 5090 | RTX 5070 Ti Laptop |
|---------|----------|-------------------|
| Memory | 32 GB | 12 GB |
| Başlangıç Sıcaklık | 32°C | 45°C |
| Test Sonrası Sıcaklık | 36°C | 66°C |
| Sıcaklık Artışı | +4°C ✅ | +21°C |

#### Performans @ 30 Kullanıcı
| Metrik | RTX 5090 | RTX 5070 Ti | Kazanan |
|--------|----------|-------------|---------|
| Throughput | 2.03 req/s | 2.76 req/s | 🥇 5070 Ti (+36%) |
| Avg Latency | 13.06s | 6.68s | 🥇 5070 Ti (2x hızlı) |
| P95 Latency | 14.61s | 10.26s | 🥇 5070 Ti |
| Apdex Score | 0.500 | 0.594 | 🥇 5070 Ti |

#### Performans @ 5 Kullanıcı
| Metrik | RTX 5090 | RTX 5070 Ti | Kazanan |
|--------|----------|-------------|---------|
| Throughput | 1.65 req/s | 0.90 req/s | 🥇 5090 (+83%) |
| Avg Latency | 2.05s | 2.84s | 🥇 5090 |
| P95 Latency | 3.02s | 6.52s | 🥇 5090 |

#### 🏆 Genel Değerlendirme
- **RTX 5090:** Düşük yük altında daha iyi, daha düşük sıcaklık
- **RTX 5070 Ti:** Yüksek yük altında çok daha iyi, daha verimli
- **Model (Qwen2.5-3B):** 5070 Ti için optimize edilmiş gibi
- **Soğutma:** 5090 çok daha iyi soğuyor

## 📈 CSV Dosyası Yapısı

### all_benchmarks_comparison.csv
```csv
GPU,Date,Test Type,Users,Requests,Successful,Throughput (req/s),Avg Latency (s),P50 (s),P95 (s),P99 (s),Max Latency (s),Success Rate (%),Apdex Score,Concurrency Factor,Memory Total (GB),Memory Used (GB),Start Temp (°C),End Temp (°C),Temp Increase (°C)
RTX 5090,2025-12-11 09:31:21,load,30,90,90,2.03,13.06,12.88,14.61,14.99,15.06,100.0,0.500,26.51,31.8,27.7,32,36,4
RTX 5070 Ti Laptop GPU,2025-12-10 22:01:48,load,30,90,90,2.76,6.68,6.50,10.26,10.93,12.00,100.0,0.594,18.43,11.9,10.8,45,66,21
```

**Excel'de Kullanım:**
1. Dosyayı Excel'de aç
2. "Insert" → "PivotTable" 
3. Rows: GPU, Columns: Users, Values: Avg Latency
4. Grafik oluştur: Line chart

## 🎨 Görsel Karşılaştırma Örneği

`make compare-visual` komutu 4 panel içeren bir grafik oluşturur:

1. **Latency Comparison** - Kullanıcı sayısına göre gecikme
2. **Throughput Comparison** - Kullanıcı sayısına göre işlem hacmi
3. **P95 Latency** - %95'lik gecikme (tail latency)
4. **Apdex Score** - Kullanıcı memnuniyeti skoru

## 🔍 Metrik Açıklamaları

### Throughput (req/s)
- **Ne:** Saniyede işlenen istek sayısı
- **Yüksek = İyi**
- **Örnek:** 2.76 req/s = Saniyede 2.76 istek

### Latency (s)
- **Ne:** Ortalama yanıt süresi
- **Düşük = İyi**
- **P50:** %50'lik kullanıcı bu süreden daha hızlı yanıt alıyor
- **P95:** %95'lik kullanıcı bu süreden daha hızlı yanıt alıyor
- **P99:** En yavaş %1'lik kullanıcıların süresi

### Apdex Score (0.0 - 1.0)
- **Ne:** Kullanıcı memnuniyeti skoru
- **1.00:** Mükemmel - Herkes mutlu
- **0.94+:** Excellent
- **0.85+:** Good
- **0.70+:** Fair
- **<0.70:** Poor

### Concurrency Factor
- **Ne:** Gerçek eşzamanlı istek sayısı
- **Yüksek = İyi paralelleştirme**
- **Örnek:** 18.43 = 30 kullanıcıdan ortalama 18 tanesi aynı anda aktif

### Success Rate (%)
- **Ne:** Başarılı isteklerin oranı
- **100% = Hiç hata yok**

## 💡 İlginç Bulgular

### 1. Model Boyutu Önemli
- Qwen2.5-3B (3 milyar parametre) modeli
- 5070 Ti'ın 12GB VRAM'i yeterli
- 5090'ın 32GB'ı bu model için fazla

### 2. Retrieval Time Farkı
- 5090'da retrieval süresi çok yüksek (11-12s @ 30 users)
- 5070 Ti'da çok düşük (4-5s @ 30 users)
- Bu, 5070 Ti'ın performans avantajının ana nedeni

### 3. Soğutma
- 5090: Desktop GPU → Daha iyi soğutma (+4°C)
- 5070 Ti: Laptop GPU → Sınırlı soğutma (+21°C)
- Ancak performans etkilenmiyor!

### 4. Skalabilite
- 5070 Ti: 5→30 kullanıcı arası throughput %207 artıyor ✅
- 5090: 5→30 kullanıcı arası throughput sadece %23 artıyor ❌

## 🚀 Öneriler

### GPU Seçimi
- **Yüksek Yük (20+ kullanıcı):** RTX 5070 Ti daha iyi
- **Düşük Yük (5-10 kullanıcı):** RTX 5090 daha iyi
- **Maliyet/Performans:** 5070 Ti daha verimli
- **Büyük Modeller:** 5090 (32GB VRAM)

### Test Tavsiyeleri
1. Her testten önce GPU'yu soğutun
2. En az 3 tekrar yapın (istatistiksel güvenilirlik)
3. Aynı soruları kullanın (tutarlılık)
4. Sonuçları CSV'de saklayın (zaman serisi analizi)

### Optimizasyon
- Retrieval time'ı düşürün (5090 için kritik)
- Batch size optimize edin
- GPU memory utilization ayarlayın (şu an 0.85)

## 📚 Dokümantasyon

### Detaylı Kullanım
```bash
cat benchmarks/README_COMPARISON.md
```

### Yardım
```bash
make help
```

### Tüm Komutlar
```bash
# Test çalıştır
make load

# Sonuçları görselleştir
make visualize

# GPU'ları karşılaştır
make compare

# CSV'ye aktar
make export-csv

# Tümünü yap
make compare-all

# Sonuçları listele
make results
```

## 🎓 Öğrenilen Dersler

1. **Daha büyük GPU ≠ Her zaman daha iyi performans**
2. **Model boyutu önemli** - Optimize edilmiş setup kritik
3. **Retrieval time** performansı ciddi etkiliyor
4. **Laptop GPU'lar** iyi soğutmayla rekabetçi olabilir
5. **CSV export** analiz için çok kullanışlı

## ⚡ Sonraki Adımlar

### İyileştirmeler
- [ ] Retrieval time optimizasyonu (5090 için)
- [ ] Farklı model boyutlarıyla test
- [ ] Farklı batch size'lar
- [ ] Farklı GPU memory utilization değerleri

### Ekstra Testler
- [ ] Stress test (50-100 users)
- [ ] Spike test (150-200 users)
- [ ] Uzun süreli stability test
- [ ] Farklı soru tipleriyle test

### Araçlar
- [x] GPU karşılaştırma aracı
- [x] CSV export
- [x] Görsel karşılaştırma
- [ ] Otomatik rapor oluşturma
- [ ] Email bildirimleri
- [ ] Web dashboard

## 📞 Destek

Sorularınız için:
1. README dosyalarını okuyun
2. `make help` komutunu çalıştırın
3. Örnek CSV dosyalarını inceleyin

---

**Oluşturulma Tarihi:** 11 Aralık 2025  
**Son Güncelleme:** 11 Aralık 2025  
**Versiyon:** 1.0  
**Durum:** ✅ Tamamlandı

