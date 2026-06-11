"""
Configuração da aplicação, lida de variáveis de ambiente com valores padrão.

Mantemos simples (sem dependência de dotenv): `os.getenv` com defaults seguros.
Os valores padrão permitem rodar a demo SEM nenhum arquivo .env. Veja
`.env.example` para a lista de variáveis suportadas.

Segurança: NENHUM segredo fica no código. Tokens/segredos (se um dia existirem)
viriam do ambiente, nunca commitados.
"""

from __future__ import annotations

import os

# Nome do projeto, exposto na API e no dashboard.
PROJECT_NAME: str = "BestSignal Portfolio Demo"

# Ambiente: development (padrão) / production etc.
APP_ENV: str = os.getenv("APP_ENV", "development")

# EV mínimo (em %) para considerar uma aposta como "de valor".
MIN_EV_PERCENT: float = float(os.getenv("MIN_EV_PERCENT", "3.0"))
