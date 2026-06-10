"""
API FastAPI do ValueBetAI Portfolio Demo.

Ponto de entrada da aplicação web. Monta o app e inclui as rotas definidas em
app/api/routes.py. A interface visual fica no dashboard Streamlit (dashboard.py),
que consome os mesmos services — não há lógica duplicada.

Rodar localmente:
    uvicorn app.main:app --reload
Documentação interativa (Swagger): http://localhost:8000/docs
"""

from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from app.config import PROJECT_NAME

app = FastAPI(
    title=f"{PROJECT_NAME} API",
    description=(
        "Demo educacional de portfólio: detecção de apostas de valor (EV+) em "
        "dados simulados. Não representa recomendação financeira, promessa de "
        "lucro ou incentivo a apostas reais."
    ),
    version="0.2.0",
)

app.include_router(router)
