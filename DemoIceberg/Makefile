.PHONY: help up down restart logs clean demo query health shell-app shell-spark advanced ingest

help:
	@echo "Apache Iceberg Data Lake Demo - Available Commands"
	@echo "=================================================="
	@echo ""
	@echo "Setup & Management:"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make clean       - Stop services and remove all data"
	@echo ""
	@echo "Demo & Queries:"
	@echo "  make demo        - Run the full demo"
	@echo "  make query       - Start interactive query mode"
	@echo "  make health      - Check service health"
	@echo "  make advanced    - Run advanced features demo"
	@echo "  make ingest      - Add new products interactively"
	@echo ""
	@echo "Shell Access:"
	@echo "  make shell-app   - Open shell in app container"
	@echo "  make shell-spark - Open shell in Spark container"
	@echo ""

up:
	docker-compose up -d
	@echo ""
	@echo "✅ Services started! Wait 2-3 minutes for initialization."
	@echo "Run 'make health' to check status, then 'make demo' to start."

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf chroma-data ollama-data localstack-data
	@echo "✅ All data cleaned!"

demo:
	@echo "Running demo (this may take 5-10 minutes on first run)..."
	docker exec -it iceberg-app python /app/scripts/demo.py

query:
	docker exec -it iceberg-app python /app/scripts/query.py

health:
	docker exec -it iceberg-app python /app/scripts/health_check.py

shell-app:
	docker exec -it iceberg-app /bin/bash

shell-spark:
	docker exec -it spark-iceberg /bin/bash

advanced:
	@echo "Running advanced features demo..."
	docker exec -it iceberg-app python /app/scripts/advanced_features.py

ingest:
	@echo "Interactive data ingestion..."
	docker exec -it iceberg-app python /app/scripts/ingest_data.py
