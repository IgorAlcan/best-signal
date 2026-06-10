# Arquitetura

> **Aviso obrigatório:** Este projeto é uma demonstração educacional de portfólio e não representa recomendação financeira, promessa de lucro ou incentivo a apostas reais.

## Visão geral

O ValueBetAI Portfolio Demo é dividido em camadas pequenas para manter a regra de
negócio testável e reutilizável. A API e o dashboard usam os mesmos services; o
dashboard não chama HTTP nem recalcula EV por conta própria.

```text
app/data/sample_odds.json
        |
        v
app/services/odds_service.py ---> app/services/ev_calculator.py
        |                                  |
        |                                  v
        |                         cálculo de probabilidade,
        |                         EV e classificação EV+
        |
        +--> app/api/routes.py ---> FastAPI/Swagger
        |
        +--> dashboard.py -------> Streamlit

tests/ validam services e API com dados locais
```

## Responsabilidade de cada pasta

`app/api/`: define os contratos HTTP. `routes.py` mantém endpoints finos e chama
os services; `schemas.py` define entrada e saída do POST `/calculate-ev`.

`app/data/`: contém `sample_odds.json`, a fonte única de dados simulados. Não há
scraping, API externa, banco remoto ou chave.

`app/services/`: concentra regras de negócio. `ev_calculator.py` calcula
probabilidade e EV; `odds_service.py` carrega e enriquece os dados;
`alert_service.py` monta alerta simulado; `bankroll_service.py` sugere stake por
percentual fixo.

`app/config.py`: lê configurações simples por ambiente, com defaults seguros. A
demo roda sem `.env`.

`dashboard.py`: interface Streamlit para explorar os dados enriquecidos. Importa
`odds_service` e `config` diretamente.

`tests/`: cobre os cálculos, services auxiliares e endpoints FastAPI.

`docs/`: explica arquitetura, regras de negócio, plano de testes e roteiro de
demonstração.

## Fluxo dos dados

1. `odds_service.load_sample_odds()` lê `app/data/sample_odds.json`.
2. `odds_service.enrich_odds_with_ev()` cria cópias dos eventos e adiciona
   `implied_probability`, `ev_percent` e `is_value_bet`.
3. `ev_calculator.calculate_ev()` estima o EV em porcentagem usando
   `bookmaker_odds` e `sharp_odds`.
4. A API devolve JSON em `/odds`, `/value-bets` e `/calculate-ev`.
5. O dashboard aplica filtros de esporte e EV mínimo sobre os dados enriquecidos.
6. Os testes exercitam esse fluxo sem rede e sem serviços externos.

## Separação das camadas

A API é uma camada de transporte. Ela valida entrada, chama services e devolve
resposta.

Os services são a camada de regra de negócio. Eles não dependem de FastAPI nem de
Streamlit.

O dashboard é uma camada de apresentação. Ele usa os services diretamente para
evitar duplicação de lógica e manter os mesmos números da API.

Os dados são determinísticos e versionados no repositório para que testes, demo e
CI sejam reprodutíveis.

## Fora de escopo

- Coleta real de odds.
- Envio real para Telegram.
- Banco externo.
- Segredos, tokens ou credenciais.
- Recomendação financeira ou incentivo a apostas reais.
