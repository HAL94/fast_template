default: help

.PHONY: help
help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: format
format:
	uv run ruff format

.PHONY: mypy
mypy:
	uv run mypy --config-file mypy.ini --explicit-package-bases .

.PHONY: run-tests
run-tests:
	uv run pytest