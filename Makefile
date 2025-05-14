# Variables
OLLAMA_MODEL = smollm2:360m
NUM_REQUESTS = 100  # default number of parallel requests for load testing

.PHONY: run
run:
	docker-compose up -d
	@echo "🚀 Services started!"
	@echo "📊 Dashboard: http://localhost:8501"
	@echo "🔌 API: http://localhost:8000"

.PHONY: stop
stop:
	docker-compose down

.PHONY: clean
clean:
	docker-compose down -v
	rm -rf __pycache__ .pytest_cache

.PHONY: build
build:
	docker-compose build --no-cache
	docker-compose up -d

# Individual services
.PHONY: dashboard
dashboard:
	cd dashboard && streamlit run main.py

.PHONY: api
api:
	cd api && uvicorn main:app --reload

# Ollama model management
.PHONY: pull-model
pull-model:
	docker-compose exec ollama ollama pull $(OLLAMA_MODEL)

# Metrics management
.PHONY: reset-metrics
reset-metrics:
	python -c "from audit_core.metrics.standard import StandardMetricsTracker; StandardMetricsTracker().reset_metrics()"

# Testing
.PHONY: test
test:
	pytest tests/

.PHONY: load-test
load-test:
	python test_loading/load_test.py --requests $(NUM_REQUESTS)