# RAG API with vLLM

Production-ready Retrieval Augmented Generation (RAG) API using vLLM for high-performance LLM inference.

---

## Why vLLM?

vLLM, LLM inference icin ozellikle tasarlanmis yuksek performansli bir servistir:

| Ozellik | vLLM | Ollama / HuggingFace |
|---------|------|----------------------|
| **Continuous Batching** | Var - birden fazla istegi dinamik olarak gruplar | Yok/Sinirli |
| **PagedAttention** | Var - GPU bellegini verimli kullanir | Yok |
| **Throughput** | Yuksek (10-24x daha hizli) | Dusuk |
| **Concurrent Users** | Cok iyi destekler | Sinirli |
| **OpenAI API Uyumu** | Tam uyumlu | Kismi |
| **GPU Utilization** | Optimize edilmis | Standart |

**Ozet:** Tek kullanici icin Ollama yeterli, ancak production ortaminda birden fazla kullanici varsa vLLM zorunlu.

---

## Professional Performance Metrics

Production sistemlerde olculen kritik metrikler:

### 1. Latency (Gecikme) Metrikleri

| Metrik | Aciklama | Hedef Deger |
|--------|----------|-------------|
| **P50 (Median)** | Isteklerin %50'si bu sureden kisa | Kullanici deneyimi icin onemli |
| **P95** | Isteklerin %95'i bu sureden kisa | SLA tanimlarinda kullanilir |
| **P99** | Isteklerin %99'u bu sureden kisa | En kotu durum senaryosu |
| **Avg** | Ortalama yanit suresi | Genel performans gostergesi |
| **Apdex** | Kullanici memnuniyeti skoru (0-1) | >0.9 mukemmel |

**Neden P95/P99 onemli?**
- Ortalama yanitici olabilir (outlier'lar etkiler)
- P99 = kullanicilarin %1'i bu kadar bekliyor
- SLA'lar genellikle P95 uzerinden tanimlanir

### 2. Throughput (Islem Hacmi)

| Metrik | Aciklama |
|--------|----------|
| **Requests/second** | Saniyede islenen istek sayisi |
| **Concurrent capacity** | Ayni anda desteklenen kullanici sayisi |

### 3. Reliability (Guvenilirlik)

| Metrik | Aciklama | Hedef |
|--------|----------|-------|
| **Success Rate** | Basarili istek orani | >99.9% |
| **Error Rate** | Hata orani | <0.1% |

### 4. Resource Utilization

| Metrik | Aciklama |
|--------|----------|
| **GPU Memory** | VRAM kullanimi |
| **GPU Utilization** | GPU islemci kullanimi |
| **CPU Usage** | Embedding ve preprocessing icin |

---

## System Architecture

```
                                 +------------------+
                                 |   Client/Test    |
                                 +--------+---------+
                                          |
                                          | HTTP POST /query
                                          v
+-------------------------------------------------------------------------+
|                           FastAPI Server (Port 8000)                     |
|                                                                          |
|  +------------------+    +------------------+    +------------------+    |
|  |   Embedding      |    |    Retrieval     |    |   LLM Call       |    |
|  |   (bge-m3)       |--->|    (Qdrant)      |--->|   (vLLM)         |    |
|  +------------------+    +------------------+    +------------------+    |
|         |                        |                       |               |
|         v                        v                       v               |
|      CPU/GPU              Vector Search           HTTP to vLLM           |
+-------------------------------------------------------------------------+
                                          |
                                          | HTTP POST /v1/chat
                                          v
                               +--------------------+
                               |   vLLM Server      |
                               |   (Port 8080)      |
                               |                    |
                               | Qwen2.5-3B-Instruct|
                               +--------------------+
                                          |
                                          v
                                        GPU
```

---

## File Structure

```
vLLM_rag/
├── main.py                    # FastAPI RAG server (vLLM + Qwen)
├── requirements.txt           # Python dependencies
├── qdrant_db/                 # Qdrant vector database
├── data/                      # PDF documents
├── rag_api.log                # API logs
│
└── benchmarks/                # Performance testing suite
    ├── benchmark.py           # GPU benchmark (standardized)
    ├── concurrent_test.py     # Quick concurrent test
    ├── visualize_results.py   # Result visualization
    ├── results/               # JSON test results
    │   ├── benchmark_*.json
    │   └── test_results_*.json
    └── reports/               # PNG chart outputs
        └── *_report.png
```

---

## Running the System

### Prerequisites

```bash
# 1. Python environment
cd /home/abali/GithubCode/vLLM_rag
source vllm-env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

### Step-by-Step Execution

#### Terminal 1: Start vLLM Server

```bash
cd /home/abali/GithubCode/vLLM_rag
source vllm-env/bin/activate

vllm serve Qwen/Qwen2.5-3B-Instruct \
    --port 8080 \
    --gpu-memory-utilization 0.85
```

Wait until you see:
```
INFO:     Uvicorn running on http://0.0.0.0:8080
```

#### Terminal 2: Start RAG API Server

```bash
cd /home/abali/GithubCode/vLLM_rag
source vllm-env/bin/activate

python main.py
```

Wait until you see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Terminal 3: Run Tests

```bash
cd /home/abali/GithubCode/vLLM_rag
source vllm-env/bin/activate

# Quick single query test
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Yazilim muhendisligi nedir?"}'

# Navigate to benchmarks folder
cd benchmarks

# Quick concurrent test
python concurrent_test.py

# GPU benchmark (recommended)
python benchmark.py --test-type load

# Visualize results
python visualize_results.py
```

### Indexing PDFs into Qdrant (first run)

If `/stats` shows `total_documents: 0`, Qdrant is empty and retrieval will return no docs. Index your PDFs:

```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"pdf_folder":"data","glob_pattern":"*.pdf","chunk_size":800,"chunk_overlap":120,"reset_collection":false}'
```

Then verify:

```bash
curl http://localhost:8000/stats
```

---

## GPU Benchmark Suite

`benchmark.py` farkli GPU'lari karsilastirmak icin standartlastirilmis test suitidir.

### Test Tipleri

| Test Type | Kullanici Sayilari | Amac |
|-----------|-------------------|------|
| `smoke` | 1, 2 | Hizli calisma kontrolu |
| `load` | 5, 10, 20, 30 | Normal yuk testi **(onerilen)** |
| `stress` | 50, 75, 100 | Maksimum kapasite testi |
| `spike` | 150, 200 | Ani trafik artisi testi |

### Kullanim

```bash
cd benchmarks

# Standart load testi (GPU otomatik algilanir)
python benchmark.py --test-type load

# GPU ismini manuel belirt
python benchmark.py --gpu-name "RTX 4090" --test-type load

# Stress testi
python benchmark.py --test-type stress
```

### Cikti Dosyalari

```
benchmarks/
├── results/
│   └── benchmark_{GPU_ADI}_{TEST_TIPI}_{TARIH}.json
└── reports/
    └── benchmark_{GPU_ADI}_{TEST_TIPI}_{TARIH}_report.png
```

Ornek: `results/benchmark_NVIDIA_GeForce_RTX_4090_load_20251210_153045.json`

### Benchmark Ozellikleri

- **Otomatik GPU Algilama**: nvidia-smi ile GPU bilgisi otomatik alinir
- **3x Tekrar**: Her yuk seviyesi 3 kez test edilir (istatistiksel guvenilirlik)
- **Warmup**: Test oncesi sistem isindirilir
- **Cooldown**: Testler arasi bekleme suresi
- **Apdex Skoru**: Kullanici memnuniyeti metrigi (0-1 arasi)

---

## Farkli GPU'lari Karsilastirma

### Workflow

```bash
# ===== GPU 1 (ornek: RTX 3090) =====
# Terminal 1: vLLM server
vllm serve Qwen/Qwen2.5-3B-Instruct --port 8080

# Terminal 2: RAG API
python main.py

# Terminal 3: Benchmark
cd benchmarks
python benchmark.py --test-type load
# Cikti: results/benchmark_NVIDIA_GeForce_RTX_3090_load_XXXXXX.json


# ===== GPU 2 (ornek: RTX 4090) =====
# Ayni adimlari tekrarla
python benchmark.py --test-type load
# Cikti: results/benchmark_NVIDIA_GeForce_RTX_4090_load_XXXXXX.json


# ===== Sonuclari Karsilastir =====
python visualize_results.py results/benchmark_NVIDIA_GeForce_RTX_3090_load_XXXXXX.json
python visualize_results.py results/benchmark_NVIDIA_GeForce_RTX_4090_load_XXXXXX.json
# Grafikler: reports/ klasorune kaydedilir
```

### Ornek Cikti

```
======================================================================
BENCHMARK: LOAD TEST
======================================================================
GPU: NVIDIA GeForce RTX 4090
Date: 2024-12-10 15:30:45
Questions: 6
Repeats: 3

----------------------------------------------------------------------
COMPARISON TABLE
----------------------------------------------------------------------
 Users |   Throughput |      Avg |      P50 |      P95 |      P99 |  Apdex
----------------------------------------------------------------------
     5 |       2.45/s |    1.85s |    1.72s |    2.34s |    2.51s |  0.950
    10 |       3.12/s |    2.95s |    2.81s |    3.67s |    4.02s |  0.875
    20 |       3.45/s |    5.21s |    4.95s |    6.82s |    7.45s |  0.725
    30 |       3.28/s |    8.42s |    7.89s |   11.23s |   12.67s |  0.550
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Submit a question, get RAG answer |
| `/health` | GET | Health check |
| `/metrics` | GET | Performance metrics |
| `/stats` | GET | Vectorstore statistics |

### Example Request

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Agile nedir?"}'
```

### Example Response

```json
{
  "answer": "Agile, yazilim gelistirme surecinde...",
  "metrics": {
    "retrieval_time": 0.234,
    "llm_time": 1.456,
    "total_time": 1.690
  }
}
```

---

## Port Summary

| Service | Port | Purpose |
|---------|------|---------|
| vLLM Server | 8080 | LLM inference |
| FastAPI RAG | 8000 | RAG API |

---

## Troubleshooting

### GPU Memory Error
```bash
# Reduce memory utilization
vllm serve Qwen/Qwen2.5-3B-Instruct --port 8080 --gpu-memory-utilization 0.80
```

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000
lsof -i :8080

# Kill the process
kill -9 <PID>
```

### Check GPU Status
```bash
nvidia-smi
```

---

## Performance Tuning

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_workers` | 50 | ThreadPoolExecutor workers in main.py |
| `gpu-memory-utilization` | 0.85 | vLLM GPU memory usage |
| `k` | 6 | Number of documents to retrieve |
| `score_threshold` | 0.2 | Minimum similarity score |
| `max_tokens` | 512 | Maximum LLM output tokens |

---

## Test Scripts Karsilastirmasi

| Script | Amac | Cikti |
|--------|------|-------|
| `benchmarks/concurrent_test.py` | Hizli performans testi | `results/test_results_*.json` |
| `benchmarks/benchmark.py` | Standartlastirilmis GPU karsilastirmasi | `results/benchmark_*.json` |
| `benchmarks/visualize_results.py` | Her iki formati da gorsellestir | `reports/*_report.png` |

## Klasor Yapisi

```
benchmarks/
├── benchmark.py           # Ana benchmark scripti
├── concurrent_test.py     # Hizli test scripti
├── visualize_results.py   # Gorsellestirme scripti
├── results/               # Tum JSON sonuclari burada
│   ├── benchmark_*.json
│   └── test_results_*.json
└── reports/               # Tum PNG grafikleri burada
    └── *_report.png
```
