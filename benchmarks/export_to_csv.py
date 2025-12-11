"""
Export Benchmark Results to CSV
================================
Convert JSON benchmark results to CSV format for Excel/Google Sheets.

Usage:
    python export_to_csv.py                     # Export all results
    python export_to_csv.py result.json         # Export specific file
"""

import json
import csv
import glob
import sys
from pathlib import Path
import os

# ═══════════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
REPORTS_DIR = SCRIPT_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════
# EXPORT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def export_single_result_to_csv(json_file: str):
    """Export a single JSON result to CSV"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Create CSV filename
    base_name = Path(json_file).stem
    csv_file = REPORTS_DIR / f"{base_name}.csv"
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # ─────────────────────────────────────────────────────────────
        # Benchmark Info
        # ─────────────────────────────────────────────────────────────
        writer.writerow(['=== BENCHMARK INFO ===', ''])
        info = data['benchmark_info']
        writer.writerow(['Test Date', info['date']])
        writer.writerow(['GPU', info['gpu_name']])
        writer.writerow(['Test Type', info['test_type']])
        writer.writerow(['Repeat Count', info['repeat_count']])
        writer.writerow(['Warmup Requests', info['warmup_requests']])
        writer.writerow(['Question Count', info['question_count']])
        writer.writerow([''])
        
        # ─────────────────────────────────────────────────────────────
        # GPU Info (Before Test)
        # ─────────────────────────────────────────────────────────────
        writer.writerow(['=== GPU INFO (START) ===', ''])
        gpu_info = data['gpu_info']
        writer.writerow(['Memory Total (GB)', f"{gpu_info['memory_total_mb']/1024:.1f}"])
        writer.writerow(['Memory Used (GB)', f"{gpu_info['memory_used_mb']/1024:.1f}"])
        writer.writerow(['Memory Free (GB)', f"{gpu_info['memory_free_mb']/1024:.1f}"])
        writer.writerow(['Utilization (%)', gpu_info['utilization_percent']])
        writer.writerow(['Temperature (°C)', gpu_info['temperature_c']])
        writer.writerow(['Power (W)', gpu_info['power_watts']])
        writer.writerow([''])
        
        # ─────────────────────────────────────────────────────────────
        # GPU Info (After Test)
        # ─────────────────────────────────────────────────────────────
        writer.writerow(['=== GPU INFO (END) ===', ''])
        gpu_after = data['gpu_after_test']
        writer.writerow(['Temperature (°C)', gpu_after['temperature_c']])
        writer.writerow(['Power (W)', gpu_after['power_watts']])
        writer.writerow(['Temperature Increase (°C)', gpu_after['temperature_c'] - gpu_info['temperature_c']])
        writer.writerow([''])
        
        # ─────────────────────────────────────────────────────────────
        # Performance Results
        # ─────────────────────────────────────────────────────────────
        writer.writerow(['=== PERFORMANCE RESULTS ===', ''])
        writer.writerow([
            'Concurrent Users',
            'Total Requests',
            'Successful',
            'Throughput (req/s)',
            'Avg Latency (s)',
            'Min Latency (s)',
            'Max Latency (s)',
            'Std Dev (s)',
            'P50 (s)',
            'P75 (s)',
            'P90 (s)',
            'P95 (s)',
            'P99 (s)',
            'Success Rate (%)',
            'Apdex Score',
            'Concurrency Factor'
        ])
        
        for result in data['results']:
            m = result['metrics']
            writer.writerow([
                result['user_count'],
                result['total_requests'],
                result['total_successful'],
                f"{m['throughput_rps']:.2f}",
                f"{m['avg_latency_s']:.3f}",
                f"{m['min_latency_s']:.3f}",
                f"{m['max_latency_s']:.3f}",
                f"{m['std_dev_s']:.3f}",
                f"{m['p50_s']:.3f}",
                f"{m['p75_s']:.3f}",
                f"{m['p90_s']:.3f}",
                f"{m['p95_s']:.3f}",
                f"{m['p99_s']:.3f}",
                f"{m['success_rate_pct']:.1f}",
                f"{m['apdex_score']:.3f}",
                f"{m['concurrency_factor']:.2f}"
            ])
        
        writer.writerow([''])
        
        # ─────────────────────────────────────────────────────────────
        # Summary
        # ─────────────────────────────────────────────────────────────
        writer.writerow(['=== SUMMARY ===', ''])
        summary = data['summary']
        writer.writerow(['Peak Throughput (req/s)', summary['peak_throughput_rps']])
        writer.writerow(['Peak Throughput at Users', summary['peak_throughput_at_users']])
        writer.writerow(['Best Latency (s)', summary['best_latency_s']])
        writer.writerow(['Best Latency at Users', summary['best_latency_at_users']])
        writer.writerow(['Latency Degradation (%)', f"{summary['latency_degradation_pct']:.1f}"])
        writer.writerow(['Throughput Scaling (%)', f"{summary['throughput_scaling_pct']:.1f}"])
        writer.writerow(['Max Tested Users', summary['max_tested_users']])
        writer.writerow(['All Tests Passed', 'Yes' if summary['all_tests_passed'] else 'No'])
    
    print(f"✓ Exported: {csv_file}")
    return csv_file

def export_all_to_single_csv():
    """Export all results to a single comparison CSV"""
    json_files = glob.glob(str(RESULTS_DIR / "benchmark_*.json"))
    
    if not json_files:
        print("[ERROR] No benchmark results found")
        return
    
    csv_file = REPORTS_DIR / "all_benchmarks_comparison.csv"
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'GPU',
            'Date',
            'Test Type',
            'Users',
            'Requests',
            'Successful',
            'Throughput (req/s)',
            'Avg Latency (s)',
            'P50 (s)',
            'P95 (s)',
            'P99 (s)',
            'Max Latency (s)',
            'Success Rate (%)',
            'Apdex Score',
            'Concurrency Factor',
            'Memory Total (GB)',
            'Memory Used (GB)',
            'Start Temp (°C)',
            'End Temp (°C)',
            'Temp Increase (°C)'
        ])
        
        # Data from all files
        for json_file in sorted(json_files, key=os.path.getmtime, reverse=True):
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            info = data['benchmark_info']
            gpu_info = data['gpu_info']
            gpu_after = data['gpu_after_test']
            gpu_name = info['gpu_name'].replace('NVIDIA GeForce ', '')
            
            for result in data['results']:
                m = result['metrics']
                writer.writerow([
                    gpu_name,
                    info['date'],
                    info['test_type'],
                    result['user_count'],
                    result['total_requests'],
                    result['total_successful'],
                    f"{m['throughput_rps']:.2f}",
                    f"{m['avg_latency_s']:.2f}",
                    f"{m['p50_s']:.2f}",
                    f"{m['p95_s']:.2f}",
                    f"{m['p99_s']:.2f}",
                    f"{m['max_latency_s']:.2f}",
                    f"{m['success_rate_pct']:.1f}",
                    f"{m['apdex_score']:.3f}",
                    f"{m['concurrency_factor']:.2f}",
                    f"{gpu_info['memory_total_mb']/1024:.1f}",
                    f"{gpu_info['memory_used_mb']/1024:.1f}",
                    gpu_info['temperature_c'],
                    gpu_after['temperature_c'],
                    gpu_after['temperature_c'] - gpu_info['temperature_c']
                ])
    
    print(f"\n✓ All results exported to: {csv_file}")
    print(f"  {len(json_files)} benchmark files included")
    return csv_file

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    print("\n" + "="*70)
    print("BENCHMARK RESULTS → CSV EXPORT")
    print("="*70)
    
    if len(sys.argv) > 1:
        # Export specific file
        json_file = sys.argv[1]
        
        # Handle relative path
        if not os.path.isabs(json_file):
            if not os.path.exists(json_file):
                # Try in results directory
                alt_path = RESULTS_DIR / json_file
                if alt_path.exists():
                    json_file = str(alt_path)
        
        if not os.path.exists(json_file):
            print(f"[ERROR] File not found: {json_file}")
            return
        
        print(f"\nExporting: {json_file}")
        csv_file = export_single_result_to_csv(json_file)
        print(f"\n✓ Done! Open in Excel/Google Sheets:\n  {csv_file}\n")
    
    else:
        # Export all results individually
        json_files = glob.glob(str(RESULTS_DIR / "benchmark_*.json"))
        
        if not json_files:
            print("\n[ERROR] No benchmark results found in results/ directory")
            print("        Run 'make load' or 'make benchmark' first\n")
            return
        
        print(f"\nFound {len(json_files)} benchmark result(s)")
        print("\nExporting individual CSVs...")
        
        for json_file in json_files:
            export_single_result_to_csv(json_file)
        
        print("\nCreating combined comparison CSV...")
        export_all_to_single_csv()
        
        print(f"\n{'='*70}")
        print("✓ All exports complete!")
        print(f"{'='*70}")
        print(f"\nCSV files saved to: {REPORTS_DIR}")
        print("Open them in Excel, Google Sheets, or any spreadsheet software")
        print()

if __name__ == "__main__":
    main()

