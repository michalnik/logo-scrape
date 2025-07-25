.PHONY: help venv install mypy isort lint clean build run

PYTHON = .venv/bin/python
PIP = .venv/bin/pip
VALIDATE = .venv/bin/validate-pyproject

help:
	@echo "Usage:"
	@echo "  make venv        - It'll create virtual environment (.venv), if it has not been created still"
	@echo "  make install     - Project installation in editable mode with dev dependencies"
	@echo "  make mypy        - It'll run mypy on collector"
	@echo "  make isort       - It'll run isort on collector"
	@echo "  make lint        - Run mypy and isort together"
	@echo "  make clean       - Deleting __pycache__ a .mypy_cache"
	@echo "  make run         - Running money collection :-)"
	@echo "  make build       - Validate and build a package"

venv:
	@if [ -d ".venv" ]; then \
		echo "Virtual environment .venv does exist."; \
	else \
		echo "I am creating virtual environment .venv with python3.13..."; \
		python3.13 -m venv .venv; \
		echo "Virtual environment created in .venv."; \
	fi

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	@echo "Project installed in editable mode with dev dependencies"

mypy:
	(cd logo_scrape && ../$(PYTHON) -m mypy .)

isort:
	(cd logo_scrape && ../$(PYTHON) -m isort .)

lint: mypy isort

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -vrf .mypy_cache dist *.egg-info
	@echo "Cleaned __pycache__ and .mypy_cache"

build:
	($(VALIDATE) pyproject.toml && $(PYTHON) -m build)

run: venv
	(cd logo_scrape && ../$(PYTHON) -m logo_scrape)
