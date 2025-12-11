# GPU Benchmark Comparison Tools 🚀

This directory contains tools for comparing GPU benchmark results and exporting them to various formats.

## 📁 Files

- **`compare_results.py`** - Compare GPU benchmark results (text output)
- **`export_to_csv.py`** - Export results to CSV for Excel/Google Sheets
- **`visualize_results.py`** - Generate visual charts and GPU comparisons
- **`benchmark.py`** - Run performance benchmarks
- **`concurrent_test.py`** - Quick concurrent tests

## 🎯 Quick Start

### 1. Compare GPU Results (Text)

```bash
make compare
```

This will:
- Find all benchmark results in `results/`
- Compare them pairwise
- Show detailed performance metrics
- Display winner analysis

**Output:**
```
📊 30 CONCURRENT USERS
────────────────────────────────────────────────────────────────
Throughput (req/s)    |  1.90 🥈 |  2.76 🥇 | Diff: 31.2%
Avg Latency (s)       | 14.09 🥈 |  6.68 🥇 | Diff: 52.6%
```

### 2. Export to CSV

```bash
make export-csv
```

Creates:
- Individual CSV files for each benchmark
- `all_benchmarks_comparison.csv` - Combined comparison
- Saved to `reports/` directory

**CSV Columns:**
- GPU, Date, Users, Throughput, Latency, P50/P95/P99
- Success Rate, Apdex Score, Memory, Temperature

### 3. Compare with CSV Export

```bash
make compare-csv
```

Combines text comparison + CSV export in one command.

### 4. Visual Comparison (Charts)

```bash
make compare-visual
```

Generates comparison charts (requires matplotlib):
- Latency comparison
- Throughput comparison
- P95 latency comparison
- Apdex score comparison

### 5. Run All Comparisons

```bash
make compare-all
```

Runs:
1. Text comparison
2. CSV export
3. Visual charts

All outputs saved to `reports/` directory.

## 📊 Available Commands

| Command | Description |
|---------|-------------|
| `make compare` | Compare GPU results (text) |
| `make compare-csv` | Compare and export to CSV |
| `make compare-visual` | Generate visual comparison charts |
| `make export-csv` | Export all results to CSV |
| `make compare-all` | Run all comparison tools |
| `make visualize` | Visualize latest single result |
| `make results` | List available results |

## 🔍 Manual Usage

### Compare Specific Files

```bash
cd benchmarks
python compare_results.py result1.json result2.json
```

### Export Specific File

```bash
cd benchmarks
python export_to_csv.py results/benchmark_XXX.json
```

### Visual Comparison

```python
from visualize_results import compare_two_gpus_visual
compare_two_gpus_visual('result1.json', 'result2.json')
```

## 📈 Understanding the Results

### Key Metrics

**Throughput (req/s)**
- Higher is better
- Measures requests processed per second
- Shows GPU's ability to handle load

**Latency (s)**
- Lower is better
- Average response time
- P95/P99 show tail latencies

**Apdex Score** (0.0 - 1.0)
- 0.94+ = Excellent
- 0.85+ = Good
- 0.70+ = Fair
- <0.70 = Poor

**Concurrency Factor**
- Actual concurrent requests
- Higher = better parallelization

### Winner Categories

1. **Throughput** - Peak req/s
2. **Best Latency** - Lowest avg latency
3. **Stability** - Lowest latency degradation
4. **Cooling** - Smallest temperature increase

## 📂 Output Formats

### 1. Text Report (Console)
- Detailed comparison tables
- Winner analysis
- Hardware specifications
- Performance by user count

### 2. CSV Files

**Individual CSVs:**
```
benchmark_GPU_NAME_DATE.csv
- Benchmark info
- GPU specs (start/end)
- Performance results
- Summary metrics
```

**Combined CSV:**
```
all_benchmarks_comparison.csv
- All GPUs in one file
- Easy pivot tables
- Time series analysis
```

**Comparison CSV:**
```
gpu_comparison.csv
- Side-by-side comparison
- All user counts
- All metrics
```

### 3. Visual Charts (PNG)

**Comparison Charts:**
- 4 subplots per comparison
- Latency vs Users
- Throughput vs Users
- P95 Latency
- Apdex Score

**Individual Reports:**
- Throughput bar chart
- Response time with percentiles
- Success rate
- Min/Avg/Max range

## 🎨 Example Workflow

```bash
# 1. Run benchmark on GPU 1
make load

# 2. Run benchmark on GPU 2 (different machine)
make load

# 3. Copy results to one machine
# (results/*.json files)

# 4. Compare results
make compare-all

# 5. Open results
cd benchmarks/reports/
# - Open CSV in Excel
# - View PNG charts
```

## 📊 Real Example

### RTX 5090 vs RTX 5070 Ti Laptop

**Key Findings:**
- 5070 Ti has **45% better throughput** at 30 users
- 5090 has **20% better latency** at 5 users
- 5070 Ti has **74% lower latency degradation**
- 5090 has **2.7x more memory** (32GB vs 12GB)

**Conclusion:**
- 5090: Better for low-load, low-latency scenarios
- 5070 Ti: Better for high-load, high-throughput scenarios
- Model size (Qwen2.5-3B) fits both GPUs well

## 🛠️ Dependencies

**Required:**
- Python 3.8+
- Standard library (json, csv, glob, pathlib)

**Optional:**
- matplotlib (for visual charts)
  ```bash
  pip install matplotlib
  ```

**Install:**
```bash
source vllm-env/bin/activate
pip install matplotlib
```

## 📝 CSV Import to Excel/Google Sheets

### Excel
1. Open Excel
2. File → Open → Select CSV
3. Data will auto-parse
4. Create pivot tables/charts

### Google Sheets
1. File → Import → Upload CSV
2. Select "Replace current sheet" or "Insert new sheet"
3. Data imports automatically

### Recommended Analysis
- Pivot table by GPU + Users
- Line chart: Latency vs Users (grouped by GPU)
- Bar chart: Throughput comparison
- Conditional formatting for best values

## 🎯 Tips

1. **Run multiple times** - Use `repeat_count` for statistical confidence
2. **Control temperature** - Wait for GPU to cool between tests
3. **Consistent environment** - Same model, questions, settings
4. **Document changes** - Note any config changes
5. **Track over time** - Keep historical results

## 🐛 Troubleshooting

**"No benchmark results found"**
```bash
# Run a benchmark first
make load
```

**"matplotlib not installed"**
```bash
# Install matplotlib
source vllm-env/bin/activate
pip install matplotlib
```

**"File not found"**
```bash
# Check results directory
ls -la benchmarks/results/
```

## 📧 Questions?

Check the main README or run:
```bash
make help
```

---

**Created:** December 2025  
**Last Updated:** December 11, 2025  
**Version:** 1.0

