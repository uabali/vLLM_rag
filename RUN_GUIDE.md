# Running Guide (End-to-End)

Bu dokuman, projeyi **en bastan en sona** calistirmak ve GPU benchmark/test almak icin adim adim rehberdir.

## 0) Kurulum

```bash
cd /home/abali/GithubCode/vLLM_rag
source vllm-env/bin/activate
pip install -r requirements.txt
```

## 1) vLLM Server (Terminal 1)

Qwen modelini vLLM ile calistirir (LLM inference servisi).

```bash
cd /home/abali/GithubCode/vLLM_rag
source vllm-env/bin/activate

vllm serve Qwen/Qwen2.5-3B-Instruct \
  --port 8082 \
  --gpu-memory-utilization 0.85
```

Bekle (ornektir):
```
Uvicorn running on http://0.0.0.0:8082
```

## 2) RAG API (Terminal 2)

FastAPI RAG servisini baslatir (Retrieval + Prompt + vLLM cagrisi).

```bash
cd /home/abali/GithubCode/vLLM_rag
source vllm-env/bin/activate

python main.py
```

Bekle (ornektir):
```
Uvicorn running on http://0.0.0.0:8000
```

## 3) Health Check

```bash
make health
```

Alternatif:

```bash
curl http://localhost:8000/health
curl http://localhost:8082/health
```

## 4) Qdrant’da dokuman var mi kontrol et

```bash
curl http://localhost:8000/stats
```

- `total_documents = 0` ise Qdrant collection bos demektir.
- Bu durumda retrieval bos donebilir ve yanit “Answer not found in context.” olabilir.

> Not: Qdrant `./qdrant_db` altina **diskte** persist eder; ama dokumanlar sisteme eklenmediyse (indexleme yoksa) arama bos doner.

## 4.1) PDF'leri Qdrant'a indexle (ilk kurulum)

**NOT:** `main.py` basladiginda otomatik olarak:
- Qdrant bos ise VE `data/` klasorunde PDF varsa → **otomatik indexleme yapilir**
- Qdrant zaten dolu ise → indexleme atlanir

Manuel indexleme istiyorsan (ornek: farkli chunk ayarlariyla):

```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"pdf_folder":"data","glob_pattern":"*.pdf","chunk_size":800,"chunk_overlap":120,"reset_collection":false}'
```

Indexleme bittikten sonra tekrar kontrol:

```bash
curl http://localhost:8000/stats
```

> Not: `reset_collection=true` dersen mevcut collection silinip sifirdan indexlenir.

## 5) Tek sorgu testi

```bash
make query
```

Alternatif:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Agile nedir?"}'
```

## 6) Hizli concurrency testi (kaba kontrol)

```bash
make test
```

Bu test `benchmarks/concurrent_test.py` ile su concurrent user seviyelerini dener:
- 3, 9, 27, 82, 100

## 7) Benchmark (GPU karsilastirma icin)

Normal yuk (onerilen temel karsilastirma):

```bash
make load
```

`make benchmark` ile aynidir:

```bash
make benchmark
```

Kapasite siniri:

```bash
make stress
```

Ani trafik (opsiyonel):

```bash
make spike
```

> Not: `benchmarks/benchmark.py` icinde `REPEAT_COUNT = 3` oldugu icin her user seviyesi **3 kez** kosulur. Ayrica `WARMUP_REQUESTS = 3` ile test oncesi isinma yapilir.

## 8) Sonuclari gorsellestir / karsilastir

```bash
make visualize
make compare
make compare-visual
make export-csv
```

Sonuclar:
- JSON: `benchmarks/results/`
- PNG/CSV raporlar: `benchmarks/reports/`


