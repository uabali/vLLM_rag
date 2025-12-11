# ════════════════════════════════════════════════════════════════════
# RAG API with vLLM - Makefile
# ════════════════════════════════════════════════════════════════════
# Usage:
#   make vllm        - Start vLLM server
#   make api         - Start RAG API server
#   make test        - Run quick concurrent test
#   make benchmark   - Run full GPU benchmark
#   make visualize   - Visualize latest results
#   make all-tests   - Run all tests
#   make clean       - Clean generated files
# ════════════════════════════════════════════════════════════════════

# Use bash instead of sh (for 'source' command)
SHELL := /bin/bash

.PHONY: help vllm api test benchmark visualize all-tests clean health smoke load stress spike compare compare-csv compare-visual export-csv compare-all

# Default target
help:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  RAG API with vLLM - Available Commands"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  Servers:"
	@echo "    make vllm          Start vLLM server (Terminal 1)"
	@echo "    make api           Start RAG API server (Terminal 2)"
	@echo ""
	@echo "  Tests:"
	@echo "    make health        Health check"
	@echo "    make test          Quick concurrent test"
	@echo "    make benchmark     Full GPU benchmark (load test)"
	@echo "    make smoke         Smoke test (1-2 users)"
	@echo "    make load          Load test (5-30 users)"
	@echo "    make stress        Stress test (50-100 users)"
	@echo "    make spike         Spike test (150-200 users)"
	@echo "    make all-tests     Run concurrent + benchmark"
	@echo ""
	@echo "  Results:"
	@echo "    make visualize     Visualize latest results"
	@echo "    make results       Show results folder"
	@echo ""
	@echo "  Comparison:"
	@echo "    make compare       Compare GPU results (text)"
	@echo "    make compare-csv   Compare and export to CSV"
	@echo "    make compare-visual Compare GPUs (visual charts)"
	@echo "    make export-csv    Export all results to CSV"
	@echo "    make compare-all   Run all comparisons"
	@echo ""
	@echo "  Other:"
	@echo "    make clean         Clean generated files"
	@echo "    make gpu           Show GPU status"
	@echo ""
	@echo "════════════════════════════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────
PYTHON = python
VENV = source vllm-env/bin/activate &&
BENCHMARK_DIR = benchmarks

# ─────────────────────────────────────────────────────────────────────
# Servers
# ─────────────────────────────────────────────────────────────────────
vllm:
	@echo "Starting vLLM server on port 8080..."
	$(VENV) vllm serve Qwen/Qwen2.5-3B-Instruct \
		--port 8080 \
		--gpu-memory-utilization 0.85

api:
	@echo "Starting RAG API server on port 8000..."
	$(VENV) $(PYTHON) api_server.py

# ─────────────────────────────────────────────────────────────────────
# Health & Status
# ─────────────────────────────────────────────────────────────────────
health:
	@echo "Checking health..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "API not running"
	@echo ""
	@curl -s http://localhost:8080/health | python -m json.tool || echo "vLLM not running"

gpu:
	@nvidia-smi

# ─────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────
test:
	@echo "Running quick concurrent test..."
	$(VENV) cd $(BENCHMARK_DIR) && $(PYTHON) concurrent_test.py

benchmark: load

smoke:
	@echo "Running smoke test (1-2 users)..."
	$(VENV) cd $(BENCHMARK_DIR) && $(PYTHON) benchmark.py --test-type smoke

load:
	@echo "Running load test (5-30 users)..."
	$(VENV) cd $(BENCHMARK_DIR) && $(PYTHON) benchmark.py --test-type load

stress:
	@echo "Running stress test (50-100 users)..."
	$(VENV) cd $(BENCHMARK_DIR) && $(PYTHON) benchmark.py --test-type stress

spike:
	@echo "Running spike test (150-200 users)..."
	$(VENV) cd $(BENCHMARK_DIR) && $(PYTHON) benchmark.py --test-type spike

all-tests: test load
	@echo ""
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  All tests completed!"
	@echo "════════════════════════════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────────────
# Results & Visualization
# ─────────────────────────────────────────────────────────────────────
visualize:
	@echo "Visualizing latest results..."
	$(VENV) cd $(BENCHMARK_DIR) && $(PYTHON) visualize_results.py

results:
	@echo "Test Results:"
	@ls -la $(BENCHMARK_DIR)/results/ 2>/dev/null || echo "No results yet"
	@echo ""
	@echo "Reports:"
	@ls -la $(BENCHMARK_DIR)/reports/ 2>/dev/null || echo "No reports yet"

# ─────────────────────────────────────────────────────────────────────
# GPU Comparison & Export
# ─────────────────────────────────────────────────────────────────────
compare:
	@echo "Comparing GPU benchmark results..."
	$(VENV) cd $(BENCHMARK_DIR) && $(PYTHON) compare_results.py

compare-csv:
	@echo "Comparing and exporting to CSV..."
	$(VENV) cd $(BENCHMARK_DIR) && $(PYTHON) compare_results.py --csv

compare-visual:
	@echo "Creating visual GPU comparison..."
	$(VENV) cd $(BENCHMARK_DIR) && $(PYTHON) -c "from visualize_results import compare_all_gpus_visual; compare_all_gpus_visual()"

export-csv:
	@echo "Exporting results to CSV..."
	$(VENV) cd $(BENCHMARK_DIR) && $(PYTHON) export_to_csv.py

compare-all: compare compare-csv compare-visual
	@echo ""
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  All comparisons complete!"
	@echo "  Check $(BENCHMARK_DIR)/reports/ for outputs"
	@echo "════════════════════════════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────────────
# Single Query Test
# ─────────────────────────────────────────────────────────────────────
query:
	@echo "Sending test query..."
	@curl -s -X POST http://localhost:8000/query \
		-H "Content-Type: application/json" \
		-d '{"question": "Yazilim muhendisligi nedir?"}' | python -m json.tool

# ─────────────────────────────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────────────────────────────
clean:
	@echo "Cleaning generated files..."
	rm -rf $(BENCHMARK_DIR)/results/*.json
	rm -rf $(BENCHMARK_DIR)/reports/*.png
	rm -rf __pycache__ $(BENCHMARK_DIR)/__pycache__
	rm -f rag_api.log
	@echo "Done!"

clean-results:
	@echo "Cleaning test results..."
	rm -rf $(BENCHMARK_DIR)/results/*.json
	rm -rf $(BENCHMARK_DIR)/reports/*.png
	@echo "Done!"

