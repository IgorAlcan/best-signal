# Plano de testes

> **Aviso obrigatório:** Este projeto é uma demonstração educacional de portfólio e não representa recomendação financeira, promessa de lucro ou incentivo a apostas reais.

## Objetivo

Garantir que a demo rode de forma reprodutível, offline e sem regressões nos
cálculos, services, API e dashboard.

## Escopo

- Cálculo de probabilidade implícita e EV.
- Classificação de value bets por EV mínimo.
- Carregamento e enriquecimento de `sample_odds.json`.
- Serviço de alerta simulado.
- Sugestão de stake por percentual de banca.
- Endpoints FastAPI.
- Dashboard Streamlit importando os services diretamente.
- Configuração Docker, Compose e CI.

## Casos automatizados

Rodar:

```bash
.venv/bin/python -m pytest -q
```

Cobertura esperada:

- odds inválidas são rejeitadas.
- `calculate_ev(2.10, 1.85)` retorna `13.51`.
- `implied_probability(2.10)` retorna `0.4762`.
- enriquecimento adiciona `implied_probability`, `ev_percent` e `is_value_bet`.
- enriquecimento não altera os dicts originais.
- `/health` retorna status ok.
- `/odds` retorna lista enriquecida.
- `/value-bets` respeita `min_ev`.
- `/calculate-ev` valida entrada e retorna o contrato esperado.

## Casos manuais

API:

```bash
.venv/bin/uvicorn app.main:app --reload
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/odds
curl "http://127.0.0.1:8000/value-bets?min_ev=10"
curl -X POST http://127.0.0.1:8000/calculate-ev \
  -H "Content-Type: application/json" \
  -d '{"bookmaker_odds":2.10,"sharp_odds":1.85}'
```

Dashboard:

```bash
.venv/bin/streamlit run dashboard.py
```

Verificar:

- aviso educacional visível.
- seletor de esporte funciona para todos/tennis/football/basketball.
- slider de EV altera a contagem de value bets.
- tabela completa mostra todos os eventos do recorte.
- tabela final mostra apenas eventos com `EV >= min_ev`.
- bloco de fórmula inclui a limitação do vig.

Docker:

```bash
docker compose up --build
curl http://localhost:8000/health
```

## Cenários positivos

- Instalação limpa com `pip install -r requirements.txt`.
- Testes passando localmente.
- API disponível em `/docs`.
- Dashboard abrindo sem depender de API HTTP local.
- Compose expondo a API em `localhost:8000`.

## Cenários negativos

- Odds `<= 1` devem falhar por validação.
- `min_ev` alto pode retornar lista vazia sem erro.
- Filtro de esporte sem value bet deve mostrar estado vazio no dashboard.
- Ausência de `.env` não pode impedir a execução.

## Critérios de aceite

- `pytest` passa 100%.
- Nenhum teste depende de rede, API externa, token, Telegram ou banco externo.
- O aviso educacional aparece no README, dashboard e docs.
- Rotas `/health`, `/odds`, `/value-bets`, `/calculate-ev` e `/docs` funcionam.
- Docker Compose sobe a API.
