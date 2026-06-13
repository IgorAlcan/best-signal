# BestSignal

![CI](https://github.com/IgorAlcan/best-signal/actions/workflows/tests.yml/badge.svg)

BestSignal é uma demo de portfólio que simula um painel de análise de apostas de
valor, também chamadas de value bets ou EV+. O objetivo do projeto é mostrar,
para recrutadores e avaliadores técnicos, minha capacidade de organizar uma
aplicação Python com API, regra de negócio reutilizável, frontend, dashboard,
testes automatizados, Docker e CI.

O projeto trabalha com dados 100% simulados. Ele não faz scraping, não usa
tokens reais, não envia alertas externos e não representa recomendação
financeira, promessa de lucro ou incentivo a apostas reais.

![Interface web BestSignal](docs/web.png)

## Resumo para recrutadores

Este projeto demonstra uma aplicação pequena, mas completa, com foco em:

- Backend com FastAPI, Pydantic e endpoints documentados no Swagger.
- Regras de negócio isoladas em services reutilizados pela API, pela interface web
  e pelo dashboard Streamlit.
- Frontend em HTML, CSS e JavaScript puro, consumindo a própria API com `fetch`.
- Dashboard analítico em Streamlit com filtros, métricas, tabelas e gráficos.
- Testes automatizados offline cobrindo API, cálculo de EV, odds, alertas
  simulados e gestão de banca.
- Execução local simples, Docker Compose e GitHub Actions para CI.

Em uma entrevista, este repositório pode ser usado para discutir arquitetura,
validação de dados, separação de responsabilidades, testes, trade-offs de produto
e postura responsável ao lidar com um domínio sensível.

## O que o sistema faz

BestSignal carrega uma base mockada de eventos esportivos e odds, calcula o valor
esperado de cada oportunidade e destaca quais seleções passam de um EV mínimo.

Na prática, a aplicação permite:

- Listar odds simuladas enriquecidas com `implied_probability`, `ev_percent` e
  `is_value_bet`.
- Filtrar somente oportunidades com EV positivo acima de um limite configurável.
- Calcular EV para um par de odds enviado pelo usuário.
- Pré-visualizar mensagens de alerta simuladas, sem envio real.
- Sugerir stake com base em percentual fixo da banca.
- Visualizar os dados em uma interface web escura e em um dashboard Streamlit.

## Interfaces

### Interface web

A interface web fica em `web/` e é servida pela própria API em `/`.

Ela mostra:

- KPIs de eventos, sinais EV+, maior EV e esporte líder.
- Gráfico EV por odd da casa em SVG, sem biblioteca externa.
- Tabela de sinais EV+ ordenada por EV.
- Simulação de alertas.
- Calculadora simples de stake.
- Bloco explicando a fórmula e as limitações do modelo.

### Dashboard Streamlit

O dashboard fica em `dashboard.py` e consome os mesmos services do backend,
sem duplicar regra de negócio.

![Dashboard BestSignal](docs/dashboard.png)

## Arquitetura

```text
app/
├── api/                 # Rotas HTTP e schemas Pydantic
├── data/                # sample_odds.json com dados simulados
├── services/            # Regras de negócio e cálculos reutilizáveis
├── config.py            # Configuração por ambiente
├── main.py              # Aplicação FastAPI e servidor da interface web
└── models.py            # Modelos de domínio
docs/                    # Documentação e imagens da demo
tests/                   # Testes automatizados
web/                     # HTML, CSS e JS da interface web
dashboard.py             # Dashboard Streamlit
Dockerfile
docker-compose.yml
requirements.txt
```

A camada de rotas é intencionalmente fina: ela recebe a requisição HTTP, chama os
services e devolve a resposta. A regra de negócio fica concentrada em
`app/services`, o que facilita teste, manutenção e reuso.

## Endpoints principais

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/health` | Checagem de saúde da API |
| `GET` | `/odds` | Lista todos os eventos simulados com EV calculado |
| `GET` | `/value-bets?min_ev=3.0` | Retorna apenas sinais acima do EV mínimo |
| `POST` | `/calculate-ev` | Calcula EV para odds informadas no body |
| `GET` | `/alerts` | Mostra mensagens de alerta simuladas |
| `POST` | `/suggest-stake` | Sugere stake por percentual fixo da banca |

## Modelo de cálculo

O projeto usa a odd de uma casa sharp como referência simplificada de
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

Limite importante: esse modelo é uma simplificação. Odds sharp também carregam
margem da casa, então `1 / sharp_odds` pode superestimar a probabilidade real. Em
um produto real, o próximo passo seria remover a margem com um processo de
de-vig usando os dois lados do mercado.

## Tecnologias

- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn
- Streamlit
- Pandas
- Plotly
- Pytest
- HTML, CSS e JavaScript puro
- Docker e Docker Compose
- GitHub Actions

## Como rodar localmente

Crie o ambiente virtual e instale as dependências:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

Rode a API:

```bash
.venv/bin/uvicorn app.main:app --reload
```

Acesse:

- Interface web: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

Rode o dashboard:

```bash
.venv/bin/streamlit run dashboard.py
```

## Exemplos de uso da API

```bash
curl http://127.0.0.1:8000/health
```

```bash
curl "http://127.0.0.1:8000/value-bets?min_ev=3.0"
```

```bash
curl -X POST http://127.0.0.1:8000/calculate-ev \
  -H "Content-Type: application/json" \
  -d '{"bookmaker_odds":2.10,"sharp_odds":1.85}'
```

Resposta esperada:

```json
{
  "bookmaker_odds": 2.1,
  "sharp_odds": 1.85,
  "implied_probability": 0.4762,
  "ev_percent": 13.51,
  "is_value_bet": true
}
```

## Testes

```bash
.venv/bin/python -m pytest -q
```

A suite cobre:

- Cálculo de probabilidade implícita e EV.
- Validação de odds inválidas.
- Filtro de value bets.
- Endpoints principais da API.
- Alertas simulados.
- Sugestão de stake.

## Docker

```bash
docker compose up --build
```

Depois acesse:

- API e interface web: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## Pontos de decisão técnica

- Dados simulados para manter a demo reproduzível, segura e sem dependência de
  fornecedores externos.
- Services compartilhados para evitar regra de negócio duplicada entre API,
  frontend e dashboard.
- Pydantic para explicitar contratos e rejeitar entradas inválidas.
- Testes offline para permitir CI rápido e previsível.
- Frontend sem framework para demonstrar domínio de fundamentos de HTML, CSS,
  JavaScript e consumo de API.

## Roadmap

- Implementar de-vig com mercados completos para reduzir viés de margem.
- Persistir histórico local de sinais e resultados.
- Adicionar autenticação e rate limiting em endpoints sensíveis.
- Criar conectores mockáveis para fontes externas.
- Evoluir a interface com mais gráficos por esporte, mercado e faixa de EV.
