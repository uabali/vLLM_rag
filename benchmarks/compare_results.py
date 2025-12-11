"""
GPU Benchmark Comparison Tool
==============================
Compare performance results from different GPUs.

Usage:
    python compare_results.py                              # Compare all results
    python compare_results.py file1.json file2.json        # Compare specific files
    python compare_results.py --csv                        # Export to CSV
"""

import json
import glob
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import os

# ═══════════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
REPORTS_DIR = SCRIPT_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════

def load_benchmark_results(results_dir: str = None) -> List[Dict]:
    """Load all benchmark JSON files"""
    if results_dir is None:
        results_dir = RESULTS_DIR
    
    json_files = glob.glob(str(Path(results_dir) / "benchmark_*.json"))
    results = []
    
    for file in json_files:
        with open(file, 'r') as f:
            data = json.load(f)
            results.append({
                'file': Path(file).name,
                'path': file,
                'data': data
            })
    
    # Sort by date
    results.sort(key=lambda x: x['data']['benchmark_info']['date'], reverse=True)
    
    return results

def load_specific_files(file_paths: List[str]) -> List[Dict]:
    """Load specific benchmark files"""
    results = []
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            # Try in results directory
            alt_path = RESULTS_DIR / file_path
            if alt_path.exists():
                file_path = str(alt_path)
            else:
                print(f"[WARN] File not found: {file_path}")
                continue
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            results.append({
                'file': Path(file_path).name,
                'path': file_path,
                'data': data
            })
    
    return results

# ═══════════════════════════════════════════════════════════════════
# COMPARISON FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def compare_two_gpus(result1: Dict, result2: Dict):
    """Compare two GPU benchmark results"""
    data1 = result1['data']
    data2 = result2['data']
    
    gpu1_name = data1['benchmark_info']['gpu_name'].replace('NVIDIA GeForce ', '')
    gpu2_name = data2['benchmark_info']['gpu_name'].replace('NVIDIA GeForce ', '')
    
    print("\n" + "="*100)
    print(f"GPU COMPARISON: {gpu1_name} vs {gpu2_name}")
    print("="*100)
    
    # GPU Hardware Info
    print(f"\n{'─'*100}")
    print("HARDWARE SPECIFICATIONS")
    print(f"{'─'*100}")
    
    gpu1_info = data1['gpu_info']
    gpu2_info = data2['gpu_info']
    
    print(f"{'Specification':<30} | {gpu1_name:>30} | {gpu2_name:>30}")
    print(f"{'-'*30}-+-{'-'*30}-+-{'-'*30}")
    print(f"{'Memory (GB)':<30} | {gpu1_info['memory_total_mb']/1024:>29.1f} | {gpu2_info['memory_total_mb']/1024:>29.1f}")
    print(f"{'Memory Used (GB)':<30} | {gpu1_info['memory_used_mb']/1024:>29.1f} | {gpu2_info['memory_used_mb']/1024:>29.1f}")
    print(f"{'Start Temperature (°C)':<30} | {gpu1_info['temperature_c']:>29d} | {gpu2_info['temperature_c']:>29d}")
    print(f"{'Start Power (W)':<30} | {gpu1_info['power_watts']:>29.1f} | {gpu2_info['power_watts']:>29.1f}")
    
    gpu1_after = data1['gpu_after_test']
    gpu2_after = data2['gpu_after_test']
    print(f"{'End Temperature (°C)':<30} | {gpu1_after['temperature_c']:>29d} | {gpu2_after['temperature_c']:>29d}")
    print(f"{'End Power (W)':<30} | {gpu1_after['power_watts']:>29.1f} | {gpu2_after['power_watts']:>29.1f}")
    
    # Performance Comparison by User Count
    print(f"\n{'─'*100}")
    print("PERFORMANCE COMPARISON")
    print(f"{'─'*100}")
    
    # Get common user counts
    users1 = {r['user_count']: r for r in data1['results']}
    users2 = {r['user_count']: r for r in data2['results']}
    common_users = sorted(set(users1.keys()) & set(users2.keys()))
    
    for user_count in common_users:
        r1 = users1[user_count]['metrics']
        r2 = users2[user_count]['metrics']
        
        print(f"\n{'─'*100}")
        print(f"📊 {user_count} CONCURRENT USERS")
        print(f"{'─'*100}")
        
        # Throughput
        tp1 = r1['throughput_rps']
        tp2 = r2['throughput_rps']
        winner = "🥇" if tp1 > tp2 else "🥈"
        diff = abs(tp1 - tp2) / max(tp1, tp2) * 100
        print(f"{'Throughput (req/s)':<30} | {tp1:>14.2f} {winner if tp1 > tp2 else '🥈':>14} | {tp2:>14.2f} {'🥇' if tp2 > tp1 else '🥈':>14} | Diff: {diff:>5.1f}%")
        
        # Latency
        lat1 = r1['avg_latency_s']
        lat2 = r2['avg_latency_s']
        winner = "🥇" if lat1 < lat2 else "🥈"
        diff = abs(lat1 - lat2) / max(lat1, lat2) * 100
        print(f"{'Avg Latency (s)':<30} | {lat1:>14.2f} {winner if lat1 < lat2 else '🥈':>14} | {lat2:>14.2f} {'🥇' if lat2 < lat1 else '🥈':>14} | Diff: {diff:>5.1f}%")
        
        # P50
        p50_1 = r1['p50_s']
        p50_2 = r2['p50_s']
        print(f"{'P50 Latency (s)':<30} | {p50_1:>29.2f} | {p50_2:>29.2f}")
        
        # P95
        p95_1 = r1['p95_s']
        p95_2 = r2['p95_s']
        print(f"{'P95 Latency (s)':<30} | {p95_1:>29.2f} | {p95_2:>29.2f}")
        
        # P99
        p99_1 = r1['p99_s']
        p99_2 = r2['p99_s']
        print(f"{'P99 Latency (s)':<30} | {p99_1:>29.2f} | {p99_2:>29.2f}")
        
        # Apdex
        apdex1 = r1['apdex_score']
        apdex2 = r2['apdex_score']
        print(f"{'Apdex Score':<30} | {apdex1:>29.3f} | {apdex2:>29.3f}")
        
        # Concurrency Factor
        cf1 = r1['concurrency_factor']
        cf2 = r2['concurrency_factor']
        print(f"{'Concurrency Factor':<30} | {cf1:>29.2f} | {cf2:>29.2f}")
    
    # Summary Comparison
    print(f"\n{'─'*100}")
    print("OVERALL SUMMARY")
    print(f"{'─'*100}")
    
    sum1 = data1['summary']
    sum2 = data2['summary']
    
    print(f"{'Metric':<30} | {gpu1_name:>30} | {gpu2_name:>30}")
    print(f"{'-'*30}-+-{'-'*30}-+-{'-'*30}")
    print(f"{'Peak Throughput (req/s)':<30} | {sum1['peak_throughput_rps']:>29.2f} | {sum2['peak_throughput_rps']:>29.2f}")
    print(f"{'  at Users':<30} | {sum1['peak_throughput_at_users']:>29d} | {sum2['peak_throughput_at_users']:>29d}")
    print(f"{'Best Latency (s)':<30} | {sum1['best_latency_s']:>29.2f} | {sum2['best_latency_s']:>29.2f}")
    print(f"{'  at Users':<30} | {sum1['best_latency_at_users']:>29d} | {sum2['best_latency_at_users']:>29d}")
    print(f"{'Latency Degradation (%)':<30} | {sum1['latency_degradation_pct']:>29.1f} | {sum2['latency_degradation_pct']:>29.1f}")
    print(f"{'Throughput Scaling (%)':<30} | {sum1['throughput_scaling_pct']:>29.1f} | {sum2['throughput_scaling_pct']:>29.1f}")
    
    # Winner Analysis
    print(f"\n{'─'*100}")
    print("🏆 WINNER ANALYSIS")
    print(f"{'─'*100}")
    
    scores = {'gpu1': 0, 'gpu2': 0}
    
    # Throughput winner
    if sum1['peak_throughput_rps'] > sum2['peak_throughput_rps']:
        print(f"✓ Throughput:      {gpu1_name}")
        scores['gpu1'] += 1
    else:
        print(f"✓ Throughput:      {gpu2_name}")
        scores['gpu2'] += 1
    
    # Latency winner
    if sum1['best_latency_s'] < sum2['best_latency_s']:
        print(f"✓ Best Latency:    {gpu1_name}")
        scores['gpu1'] += 1
    else:
        print(f"✓ Best Latency:    {gpu2_name}")
        scores['gpu2'] += 1
    
    # Stability (lower degradation is better)
    if sum1['latency_degradation_pct'] < sum2['latency_degradation_pct']:
        print(f"✓ Stability:       {gpu1_name}")
        scores['gpu1'] += 1
    else:
        print(f"✓ Stability:       {gpu2_name}")
        scores['gpu2'] += 1
    
    # Power efficiency (lower temp increase)
    temp_increase1 = gpu1_after['temperature_c'] - gpu1_info['temperature_c']
    temp_increase2 = gpu2_after['temperature_c'] - gpu2_info['temperature_c']
    if temp_increase1 < temp_increase2:
        print(f"✓ Cooling:         {gpu1_name}")
        scores['gpu1'] += 1
    else:
        print(f"✓ Cooling:         {gpu2_name}")
        scores['gpu2'] += 1
    
    print(f"\n{'─'*100}")
    if scores['gpu1'] > scores['gpu2']:
        print(f"🏆 OVERALL WINNER: {gpu1_name} ({scores['gpu1']}/{scores['gpu1']+scores['gpu2']} categories)")
    elif scores['gpu2'] > scores['gpu1']:
        print(f"🏆 OVERALL WINNER: {gpu2_name} ({scores['gpu2']}/{scores['gpu1']+scores['gpu2']} categories)")
    else:
        print(f"🤝 TIE: Both GPUs performed equally well")
    print(f"{'─'*100}\n")

def compare_all_results(results: List[Dict]):
    """Compare all available results"""
    if len(results) < 2:
        print("[ERROR] Need at least 2 benchmark results to compare")
        return
    
    print(f"\nFound {len(results)} benchmark results:")
    for i, r in enumerate(results, 1):
        info = r['data']['benchmark_info']
        gpu_name = info['gpu_name'].replace('NVIDIA GeForce ', '')
        print(f"  {i}. {gpu_name} - {info['date']} ({r['file']})")
    
    # Compare each pair
    for i in range(len(results) - 1):
        compare_two_gpus(results[i], results[i + 1])

def export_to_csv(results: List[Dict]):
    """Export comparison to CSV file"""
    try:
        import csv
    except ImportError:
        print("[ERROR] CSV module not available")
        return
    
    csv_file = REPORTS_DIR / "gpu_comparison.csv"
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'GPU', 'Date', 'Users', 'Throughput (req/s)', 'Avg Latency (s)',
            'P50 (s)', 'P95 (s)', 'P99 (s)', 'Success Rate (%)', 'Apdex Score',
            'Concurrency Factor', 'Memory (GB)', 'Temp (°C)'
        ])
        
        # Data
        for result in results:
            data = result['data']
            info = data['benchmark_info']
            gpu_info = data['gpu_info']
            gpu_name = info['gpu_name'].replace('NVIDIA GeForce ', '')
            
            for test_result in data['results']:
                m = test_result['metrics']
                writer.writerow([
                    gpu_name,
                    info['date'],
                    test_result['user_count'],
                    f"{m['throughput_rps']:.2f}",
                    f"{m['avg_latency_s']:.2f}",
                    f"{m['p50_s']:.2f}",
                    f"{m['p95_s']:.2f}",
                    f"{m['p99_s']:.2f}",
                    f"{m['success_rate_pct']:.1f}",
                    f"{m['apdex_score']:.3f}",
                    f"{m['concurrency_factor']:.2f}",
                    f"{gpu_info['memory_total_mb']/1024:.1f}",
                    gpu_info['temperature_c']
                ])
    
    print(f"\n✓ CSV exported to: {csv_file}")

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    # Check for CSV export flag
    export_csv = '--csv' in sys.argv
    args = [arg for arg in sys.argv[1:] if arg != '--csv']
    
    # Load results
    if len(args) >= 2:
        # Specific files provided
        results = load_specific_files(args)
    else:
        # Load all results
        results = load_benchmark_results()
    
    if not results:
        print("[ERROR] No benchmark results found")
        print("        Run 'make load' or 'make benchmark' first")
        return
    
    # Export to CSV if requested
    if export_csv:
        export_to_csv(results)
    
    # Compare results
    if len(args) == 2:
        # Compare specific two files
        compare_two_gpus(results[0], results[1])
    else:
        # Compare all
        compare_all_results(results)

if __name__ == "__main__":
    main()

