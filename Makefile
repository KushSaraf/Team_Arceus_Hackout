.PHONY: help train api clean install test

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

train: ## Train all ML models
	python oil_spill_train.py
	python algal_blooms_train.py
	python coastal_erosion_train.py

train-oil: ## Train oil spill model only
	python oil_spill_train.py

train-algal: ## Train algal bloom model only
	python algal_blooms_train.py

train-erosion: ## Train coastal erosion model only
	python coastal_erosion_train.py

api: ## Start the unified ML API server
	python api.py

tide-api: ## Start the tide monitoring API
	python tide_api.py

test: ## Run integration tests
	python test_integration.py

test-api: ## Test the unified ML API
	python test_api.py

clean: ## Clean up generated files
	rm -rf artifacts/*
	rm -rf models/*.pkl
	rm -rf __pycache__
	rm -rf *.pyc

setup: install train ## Full setup: install deps and train models

dev: ## Development mode - start API with auto-reload
	export FLASK_ENV=development && python api.py
