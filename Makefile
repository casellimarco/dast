.PHONY: lint
lint:
	pylint dast --max-line-length=120
	mypy . --ignore-missing-imports
