# BestSignal Portfolio Demo

Demo educacional de detecção de value bets com FastAPI, Streamlit e dados 100%
simulados. O projeto mostra uma arquitetura simples para carregar odds mockadas,
calcular EV em porcentagem, expor uma API documentada e visualizar oportunidades
em um dashboard sem depender de serviços externos.

> **Aviso obrigatório:** Este projeto é uma demonstração educacional de portfólio e não representa recomendação financeira, promessa de lucro ou incentivo a apostas reais.

## Funcionalidades

- API FastAPI com endpoints de saúde, odds enriquecidas, value bets e cálculo de EV.
- Dashboard Streamlit que importa os services diretamente, sem chamada HTTP interna.
- Dados offline em `app/data/sample_odds.json`, com eventos simulados de tennis,
  football e basketball.
- Cálculo de probabilidade implícita, EV em porcentagem e filtro por EV mínimo.
- Serviço de alerta apenas simulado, sem Telegram real, token ou rede.
- Sugestão de stake por percentual fixo da banca.
- Testes automatizados para services e API.
- Dockerfile, Docker Compose e workflow de CI para rodar testes.

## Tecnologias

- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn
- Streamlit
- Pandas
- Pytest
- Docker e Docker Compose

## Estrutura

```text
app/
├── api/                 # Rotas e schemas HTTP
├── data/                # sample_odds.json com dados simulados
├── services/            # Regras de negócio e cálculos reutilizáveis
├── config.py            # Configuração por ambiente com defaults seguros
├── main.py              # Aplicação FastAPI
└── models.py            # Modelos Pydantic de domínio
docs/
├── architecture.md
├── business_rules.md
├── demo_walkthrough.md
└── test_plan.md
tests/                   # Testes automatizados
dashboard.py             # Dashboard Streamlit
Dockerfile
docker-compose.yml
pytest.ini
requirements.txt
```

## Fórmula de EV

O projeto usa a odd de uma casa sharp como referência aproximada de
probabilidade:

```text
probabilidade estimada = 1 / sharp_odds
EV (%) = (probabilidade estimada * bookmaker_odds - 1) * 100
```

Exemplo:

```text
bookmaker_odds = 2.10
sharp_odds = 1.85
EV = ((1 / 1.85) * 2.10 - 1) * 100 = 13.51%
```

A resposta também exibe `implied_probability`, que neste projeto é a
probabilidade implícita da odd da casa comum: `1 / bookmaker_odds`.

Limitação metodológica: `1 / sharp_odds` é uma simplificação. Odds sharp também
embutem margem da casa, o vig ou overround. Isso pode superestimar a
probabilidade real e inflar o EV calculado. Em um produto real, o caminho seria
remover essa margem com de-vig usando os dois lados do mercado antes de tratar a
probabilidade como estimativa justa.

## Instalação

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

Não é necessário criar `.env`. A demo funciona com os defaults de `app/config.py`.
O arquivo `.env.example` existe apenas como referência para evolução futura.

## Rodar a API

```bash
.venv/bin/uvicorn app.main:app --reload
```

Endpoints principais:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## Exemplos de chamadas

```bash
curl http://127.0.0.1:8000/health
```

```bash
curl http://127.0.0.1:8000/odds
```

```bash
curl "http://127.0.0.1:8000/value-bets?min_ev=3.0"
```

```bash
curl -X POST http://127.0.0.1:8000/calculate-ev \
  -H "Content-Type: application/json" \
  -d '{"bookmaker_odds":2.10,"sharp_odds":1.85}'
```

Resposta esperada para o último exemplo:

```json
{
  "bookmaker_odds": 2.1,
  "sharp_odds": 1.85,
  "implied_probability": 0.4762,
  "ev_percent": 13.51,
  "is_value_bet": true
}
```

## Rodar o dashboard

```bash
.venv/bin/streamlit run dashboard.py
```

O dashboard carrega `app/data/sample_odds.json` por meio de
`app.services.odds_service`, aplica os filtros localmente e mostra métricas,
tabela completa e tabela de value bets.

## Rodar testes

```bash
.venv/bin/python -m pytest -q
```

## Rodar com Docker

```bash
docker compose up --build
```

Depois acesse:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## O que o projeto demonstra para recrutadores

- Separação entre API, services, data, dashboard e testes.
- Regras de negócio reutilizadas sem duplicação entre API e dashboard.
- Uso responsável de dados simulados e ausência de dependências externas reais.
- Contratos HTTP documentados com FastAPI e Pydantic.
- Testes automatizados offline adequados para CI.
- Entrega operável localmente com venv ou Docker.

## Roadmap futuro

- Implementar de-vig com mercados completos para reduzir viés de margem.
- Persistir histórico local de sinais e resultados.
- Adicionar autenticação e rate limiting se houver endpoints sensíveis.
- Criar conectores mockáveis para fontes externas sem quebrar o modo offline.
- Evoluir o dashboard com gráficos de distribuição de EV por esporte e mercado.
