PYTHONPATH=src

.PHONY: test run-api run-cli

test:
	PYTHONPATH=$(PYTHONPATH) python -m unittest discover -s tests

run-api:
	PYTHONPATH=$(PYTHONPATH) python -m fireai.api

run-cli:
	PYTHONPATH=$(PYTHONPATH) python app.py
