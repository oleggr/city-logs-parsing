PROJECT_NAME ?= city-logs-parsing
PROJECT_NAMESPACE ?= oleggr
REGISTRY_IMAGE ?= $(PROJECT_NAMESPACE)/$(PROJECT_NAME)

all:
	@echo "make parse    - Run parsing"
	@exit 0

parse_v1:
	python3 worker.py --parse v1 --files_dir=journals/v1/

parse_v2:
	python3 worker.py --parse v2 --files_dir=journals/v2/2020/Август/
