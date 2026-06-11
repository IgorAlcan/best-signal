"""
API FastAPI do BestSignal Portfolio Demo.

Ponto de entrada da aplicação web. Monta o app, inclui as rotas (app/api/routes.py)
e serve uma interface web estática (web/) que consome a própria API por HTTP.

Há duas interfaces, ambas sobre os mesmos services (sem lógica duplicada):
- web/ (HTML/CSS/JS puro) servida em "/" e consumindo a API via fetch.
- dashboard.py (Streamlit), rodado à parte.

Rodar localmente:
    uvicorn app.main:app --reload
Interface web: http://localhost:8000/
Documentação interativa (Swagger): http://localhost:8000/docs
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import PROJECT_NAME

# Pasta com a interface web estática (HTML/CSS/JS), na raiz do projeto.
_WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(
    title=f"{PROJECT_NAME} API",
    description=(
        "Demo educacional de portfólio: detecção de apostas de valor (EV+) em "
        "dados simulados. Não representa recomendação financeira, promessa de "
        "lucro ou incentivo a apostas reais."
    ),
    version="0.3.0",
)

app.include_router(router)

# Serve a interface web em "/". Precisa vir DEPOIS das rotas /api e do /docs
# (FastAPI registra essas antes); html=True faz "/" servir index.html.
app.mount("/", StaticFiles(directory=_WEB_DIR, html=True), name="web")
