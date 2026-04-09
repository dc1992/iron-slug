.PHONY: run install clean

run: install
	.venv/bin/python3 main.py

install: .venv/bin/python
	.venv/bin/pip install -r requirements.txt -q

.venv/bin/python:
	python3.13 -m venv .venv

clean:
	rm -rf .venv
