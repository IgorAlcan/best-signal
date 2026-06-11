.PHONY: help install test api dashboard docker

PYTHON := .venv/bin/python
PIP := .venv/bin/pip
UVICORN := .venv/bin/uvicorn
STREAMLIT := .venv/bin/streamlit

help:
	@echo "Comandos disponíveis:"
	@echo "  make install    Instala as dependências"
	@echo "  make test       Roda os testes"
	@echo "  make api        Sobe a API em http://127.0.0.1:8000"
	@echo "  make dashboard  Sobe o dashboard em http://localhost:8501"
	@echo "  make docker     Sobe a API com Docker Compose"

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -q

api:
	$(UVICORN) app.main:app --reload

dashboard:
	$(STREAMLIT) run dashboard.py

docker:
	docker compose up --build
