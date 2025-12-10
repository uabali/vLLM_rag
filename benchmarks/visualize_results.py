"""
Performance Test Results Visualization
======================================
Generates charts and reports from test results.

Usage:
    python visualize_results.py
    python visualize_results.py results/test_results_YYYYMMDD_HHMMSS.json
"""

import json
import sys
import os
from datetime import datetime
import glob
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
REPORTS_DIR = SCRIPT_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════
# FILE DISCOVERY
# ═══════════════════════════════════════════════════════════════════

def find_latest_results():
    """Find the most recent test results file (supports both formats)"""
    patterns = [
        str(RESULTS_DIR / "test_results_*.json"),
        str(RESULTS_DIR / "benchmark_*.json"),
    ]
    
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def load_results(filename):
    """Load test results from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# ═══════════════════════════════════════════════════════════════════
# TEXT REPORT
# ═══════════════════════════════════════════════════════════════════

def print_text_report(data, filename):
    """Generate a text-based report (no matplotlib required)"""
    print("\n" + "="*70)
    print("PERFORMANCE TEST REPORT")
    print("="*70)
    
    # Handle both concurrent_test.py and benchmark.py formats
    is_benchmark = 'benchmark_info' in data
    
    if is_benchmark:
        info = data['benchmark_info']
        print(f"Test Date: {info['date']}")
        print(f"GPU: {info['gpu_name']}")
        print(f"Test Type: {info['test_type']}")
        print(f"Repeats: {info['repeat_count']}")
    else:
        print(f"Test Date: {data['date']}")
    print(f"File: {filename}")
    
    if 'summary' in data:
        summary = data['summary']
        print(f"\n{'-'*70}")
        print("OVERALL SUMMARY")
        print(f"{'-'*70}")
        if is_benchmark:
            print(f"  Peak Throughput:     {summary['peak_throughput_rps']} req/s @ {summary['peak_throughput_at_users']} users")
            print(f"  Best Latency:        {summary['best_latency_s']}s @ {summary['best_latency_at_users']} users")
            print(f"  Latency Degradation: {summary['latency_degradation_pct']}%")
            print(f"  All Tests Passed:    {'Yes' if summary['all_tests_passed'] else 'No'}")
        else:
            print(f"  Total Tests:         {summary['total_tests']}")
            print(f"  Total Requests:      {summary['total_requests']}")
            print(f"  Total Successful:    {summary['total_successful']}")
            print(f"  Success Rate:        {summary['overall_success_rate']}%")
            print(f"  Avg Throughput:      {summary['avg_throughput']} req/s")
    
    # Get tests array (different key for benchmark.py)
    tests = data.get('results', data.get('tests', []))
    
    # Helper function to get metric from either format
    def get_metric(t, key, alt_key=None):
        """Get metric from test dict, checking both formats"""
        if 'metrics' in t:
            # benchmark.py format
            m = t['metrics']
            key_map = {
                'throughput': 'throughput_rps',
                'avg_response_time': 'avg_latency_s',
                'p50': 'p50_s',
                'p95': 'p95_s', 
                'p99': 'p99_s',
                'max_time': 'max_latency_s',
                'success_rate': 'success_rate_pct'
            }
            return m.get(key_map.get(key, key), 0)
        else:
            # concurrent_test.py format
            return t.get(key, t.get(alt_key, 0) if alt_key else 0)
    
    # Throughput Chart (ASCII)
    print(f"\n{'-'*70}")
    print("THROUGHPUT vs CONCURRENT USERS")
    print(f"{'-'*70}")
    max_throughput = max(get_metric(t, 'throughput') for t in tests)
    for t in tests:
        throughput = get_metric(t, 'throughput')
        bar_length = int(throughput / max_throughput * 40) if max_throughput > 0 else 0
        bar = "#" * bar_length
        print(f"  {t['user_count']:>3} users | {bar:<40} {throughput:.2f} req/s")
    
    # Response Time Chart (ASCII)
    print(f"\n{'-'*70}")
    print("RESPONSE TIME vs CONCURRENT USERS")
    print(f"{'-'*70}")
    max_time = max(get_metric(t, 'avg_response_time') for t in tests)
    for t in tests:
        avg_time = get_metric(t, 'avg_response_time')
        bar_length = int(avg_time / max_time * 40) if max_time > 0 else 0
        bar = "=" * bar_length
        print(f"  {t['user_count']:>3} users | {bar:<40} {avg_time:.2f}s")
    
    # Percentiles Table
    print(f"\n{'-'*70}")
    print("LATENCY PERCENTILES")
    print(f"{'-'*70}")
    print(f"  {'Users':>6} | {'P50':>8} | {'P95':>8} | {'P99':>8} | {'Max':>8}")
    print(f"  {'-'*6}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}")
    for t in tests:
        p50 = get_metric(t, 'p50')
        p95 = get_metric(t, 'p95')
        p99 = get_metric(t, 'p99')
        max_t = get_metric(t, 'max_time')
        print(f"  {t['user_count']:>6} | {p50:>7.2f}s | {p95:>7.2f}s | {p99:>7.2f}s | {max_t:>7.2f}s")
    
    # Success Rate
    print(f"\n{'-'*70}")
    print("SUCCESS RATE")
    print(f"{'-'*70}")
    for t in tests:
        rate = get_metric(t, 'success_rate')
        if rate == 0 and 'successful' in t:
            rate = t['successful']/t['user_count']*100
        bar_length = int(rate / 100 * 40)
        bar = "*" * bar_length + "." * (40 - bar_length)
        print(f"  {t['user_count']:>3} users | {bar} {rate:.1f}%")
    
    print(f"\n{'='*70}")
    print("ANALYSIS")
    print(f"{'='*70}")
    
    # Find optimal load (using helper function)
    best_throughput = max(tests, key=lambda x: get_metric(x, 'throughput'))
    best_tp = get_metric(best_throughput, 'throughput')
    print(f"  Best Throughput:     {best_tp:.2f} req/s @ {best_throughput['user_count']} users")
    
    fastest = min(tests, key=lambda x: get_metric(x, 'avg_response_time'))
    fastest_time = get_metric(fastest, 'avg_response_time')
    print(f"  Fastest Response:    {fastest_time:.2f}s @ {fastest['user_count']} users")
    
    # Check for degradation
    if len(tests) > 1:
        last_test = tests[-1]
        first_test = tests[0]
        last_time = get_metric(last_test, 'avg_response_time')
        first_time = get_metric(first_test, 'avg_response_time')
        degradation = (last_time - first_time) / first_time * 100 if first_time > 0 else 0
        print(f"  Response Degradation: {degradation:.1f}% ({first_test['user_count']} -> {last_test['user_count']} users)")
    
    # Recommendations
    print(f"\n{'-'*70}")
    print("RECOMMENDATIONS")
    print(f"{'-'*70}")
    
    all_success = all(t.get('success_rate', 100) == 100 or t.get('failed', 0) == 0 for t in tests)
    if all_success:
        print("  [OK] All tests passed with 100% success rate")
    else:
        failed_tests = [t for t in tests if t.get('failed', 0) > 0]
        print(f"  [WARN] {len(failed_tests)} test(s) had failures - consider reducing max_workers")
    
    # P99 analysis
    high_p99 = [t for t in tests if get_metric(t, 'p99') > 30]
    if high_p99:
        print(f"  [WARN] P99 > 30s in {len(high_p99)} test(s) - consider caching frequent queries")
    
    print(f"\n{'='*70}\n")

# ═══════════════════════════════════════════════════════════════════
# MATPLOTLIB CHARTS
# ═══════════════════════════════════════════════════════════════════

def generate_matplotlib_charts(data, filename):
    """Generate charts using matplotlib (if available)"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
    except ImportError:
        print("[INFO] matplotlib not installed. Install with: pip install matplotlib")
        print("       Showing text-based report instead.\n")
        return False
    
    # Handle both formats
    is_benchmark = 'benchmark_info' in data
    tests = data.get('results', data.get('tests', []))
    users = [t['user_count'] for t in tests]
    
    # Helper for getting metrics
    def get_metric(t, key):
        if 'metrics' in t:
            key_map = {
                'throughput': 'throughput_rps',
                'avg_response_time': 'avg_latency_s',
                'p50': 'p50_s', 'p95': 'p95_s', 'p99': 'p99_s',
                'max_time': 'max_latency_s', 'min_time': 'min_latency_s',
                'success_rate': 'success_rate_pct'
            }
            return t['metrics'].get(key_map.get(key, key), 0)
        return t.get(key, 0)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    title = f"Performance Test Results"
    if is_benchmark:
        title += f" - {data['benchmark_info']['gpu_name']}"
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    # 1. Throughput
    throughput = [get_metric(t, 'throughput') for t in tests]
    axes[0,0].bar(users, throughput, color='steelblue', edgecolor='navy')
    axes[0,0].set_xlabel('Concurrent Users')
    axes[0,0].set_ylabel('Throughput (req/s)')
    axes[0,0].set_title('Throughput vs Concurrent Users')
    axes[0,0].grid(axis='y', alpha=0.3)
    for i, v in enumerate(throughput):
        axes[0,0].text(users[i], v + 0.05, f'{v:.2f}', ha='center', fontsize=9)
    
    # 2. Response Time with percentiles
    avg_times = [get_metric(t, 'avg_response_time') for t in tests]
    p50 = [get_metric(t, 'p50') for t in tests]
    p95 = [get_metric(t, 'p95') for t in tests]
    p99 = [get_metric(t, 'p99') for t in tests]
    
    axes[0,1].plot(users, avg_times, 'o-', label='Avg', linewidth=2, markersize=8)
    axes[0,1].plot(users, p50, 's--', label='P50', linewidth=1.5, markersize=6)
    axes[0,1].plot(users, p95, '^--', label='P95', linewidth=1.5, markersize=6)
    axes[0,1].plot(users, p99, 'd--', label='P99', linewidth=1.5, markersize=6)
    axes[0,1].set_xlabel('Concurrent Users')
    axes[0,1].set_ylabel('Response Time (s)')
    axes[0,1].set_title('Response Time vs Concurrent Users')
    axes[0,1].legend()
    axes[0,1].grid(alpha=0.3)
    
    # 3. Success Rate
    success_rates = [get_metric(t, 'success_rate') or t.get('successful', 0)/t['user_count']*100 for t in tests]
    colors = ['green' if r == 100 else 'orange' if r >= 95 else 'red' for r in success_rates]
    axes[1,0].bar(users, success_rates, color=colors, edgecolor='darkgray')
    axes[1,0].set_xlabel('Concurrent Users')
    axes[1,0].set_ylabel('Success Rate (%)')
    axes[1,0].set_title('Success Rate vs Concurrent Users')
    axes[1,0].set_ylim(0, 105)
    axes[1,0].axhline(y=100, color='green', linestyle='--', alpha=0.5)
    axes[1,0].axhline(y=95, color='orange', linestyle='--', alpha=0.5)
    axes[1,0].grid(axis='y', alpha=0.3)
    
    # 4. Response Time Distribution
    min_times = [get_metric(t, 'min_time') for t in tests]
    max_times = [get_metric(t, 'max_time') for t in tests]
    
    for i, u in enumerate(users):
        axes[1,1].plot([u, u], [min_times[i], max_times[i]], 'k-', linewidth=2)
        axes[1,1].plot(u, min_times[i], 'g^', markersize=8)
        axes[1,1].plot(u, max_times[i], 'rv', markersize=8)
        axes[1,1].plot(u, avg_times[i], 'bo', markersize=10)
    
    axes[1,1].set_xlabel('Concurrent Users')
    axes[1,1].set_ylabel('Response Time (s)')
    axes[1,1].set_title('Response Time Range (Min/Avg/Max)')
    axes[1,1].legend(['Range', 'Min', 'Max', 'Avg'], loc='upper left')
    axes[1,1].grid(alpha=0.3)
    
    plt.tight_layout()
    
    # Save to reports directory
    base_name = Path(filename).stem
    output_file = REPORTS_DIR / f"{base_name}_report.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Chart saved: {output_file}")
    
    return True

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    # Get filename
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        # Handle relative path
        if not os.path.isabs(filename):
            filename = SCRIPT_DIR / filename
    else:
        filename = find_latest_results()
        if not filename:
            print("[ERROR] No test results found in 'results/' directory.")
            print("        Run benchmark.py or concurrent_test.py first.")
            sys.exit(1)
        print(f"Using latest results: {filename}")
    
    if not os.path.exists(filename):
        print(f"[ERROR] File not found: {filename}")
        sys.exit(1)
    
    # Load data
    data = load_results(filename)
    
    # Generate matplotlib charts if available
    charts_generated = generate_matplotlib_charts(data, str(filename))
    
    # Always show text report
    print_text_report(data, str(filename))

if __name__ == "__main__":
    main()

