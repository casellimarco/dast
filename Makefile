.PHONY: lint
lint:
	pylint dast --max-line-length=120
	mypy . --ignore-missing-imports

.PHONY: test
test:
	python -m doctest -v dast/lcs.py
	pytest tests

.PHONY: tag
tag:
	python version.py
