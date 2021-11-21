.PHONY: lint
lint:
	pylint dast --max-line-length=120
	mypy . --ignore-missing-imports --exclude=examples --show-error-codes

.PHONY: test
test:
	python -m doctest -v dast/lcs.py
	python -m doctest -v dast/pretty_diff.py

.PHONY: tag
tag:
	python version.py
