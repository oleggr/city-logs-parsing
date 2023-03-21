PROJECT_NAME ?= city-logs-parsing
PROJECT_NAMESPACE ?= oleggr
REGISTRY_IMAGE ?= $(PROJECT_NAMESPACE)/$(PROJECT_NAME)

all:
	@echo "make parse    - Run parsing"
	@exit 0

parse:
	python3 worker.py --parse v1
