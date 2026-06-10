# Arquitetura

Este documento explica **como o projeto é organizado** e **por que** cada peça
existe. A ideia central é separar responsabilidades em camadas, de modo que a
matemática possa ser testada sem subir um servidor e que a fonte de dados possa
ser trocada num ponto só.

## Visão geral em camadas

```
┌─────────────────────────────────────────────────────────────┐
│  web/index.html        — Dashboard (HTML + CSS + JS puro)    │
│  consome a API via fetch()                                   │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP (JSON)
┌───────────────────────────▼─────────────────────────────────┐
│  app/main.py           — API FastAPI (camada FINA)           │
│  só recebe a requisição, chama o serviço e devolve           │
└───────────────────────────┬─────────────────────────────────┘
                            │ chamada de função
┌───────────────────────────▼─────────────────────────────────┐
│  app/services/value_service.py — REGRAS DE NEGÓCIO           │
│  filtra (EV mínimo, faixa de odds), ranqueia, explica        │
└──────────────┬─────────────────────────────┬────────────────┘
               │                             │
┌──────────────▼──────────────┐  ┌───────────▼─────────────────┐
│ app/core/value.py           │  │ app/data/mock.py            │
│ MATEMÁTICA PURA             │  │ FONTE DE DADOS (mock)       │
│ EV, edge, Kelly, implícita  │  │ get_matches()               │
│ sem dependências do projeto │  │ 100% offline, sem API/chave │
└─────────────────────────────┘  └─────────────────────────────┘

         app/models/schemas.py — modelos Pydantic (usados por todos)
```

## Responsabilidade de cada módulo

### `app/core/value.py` — a matemática
Funções puras, sem nenhuma dependência do resto do projeto: `implied_probability`,
`edge`, `expected_value`, `kelly_fraction`, `is_value_bet`. Por serem puras
(entram números, saem números), são triviais de testar e de raciocinar.

### `app/models/schemas.py` — os modelos de dados
Modelos Pydantic. Separamos **entrada** (`Match`, `Outcome` — dado bruto) de
**saída** (`ValueBet` — resultado já calculado). Pydantic valida tudo e gera o
JSON da API automaticamente.

### `app/data/mock.py` — a fonte de dados
Devolve uma lista curada e **determinística** de jogos. Determinística de
propósito: a demo mostra sempre os mesmos números, o que é bom para screenshots,
testes e CI. **Não usa nenhuma API externa, chave ou serviço pago.** É o único
ponto de troca de fonte de dados.

### `app/services/value_service.py` — as regras de negócio
A "cola". Para cada resultado de cada jogo, chama o núcleo, aplica os filtros
(EV mínimo, faixa de odds), monta a explicação em português e ordena por EV. É
aqui que ficam as decisões de negócio — não na API nem no núcleo.

### `app/main.py` — a API
Camada **fina** de propósito: cada endpoint só traduz HTTP ↔ chamada de serviço.
Também serve o dashboard estático em `/`.

### `web/index.html` — o dashboard
Página única em JS puro que chama a API e renderiza os cartões. Sem framework e
sem etapa de build.

## Por que essa separação?

- **Testabilidade:** o núcleo e o serviço são testados sem subir servidor (a
  maioria dos 30 testes não toca HTTP).
- **Baixo acoplamento:** trocar a fonte de dados não afeta serviço nem API;
  mudar a API não afeta a matemática.
- **Clareza:** cada arquivo tem um motivo de existir e um motivo para mudar.

## Fluxo de uma requisição (passo a passo)

1. O dashboard faz `fetch("/api/value-bets?min_ev=0.05")`.
2. `main.py` recebe e chama `value_service.find_value_bets(min_ev=0.05)`.
3. O serviço pega os jogos de `mock.get_matches()`.
4. Para cada resultado, usa `core/value.py` para calcular EV/edge/Kelly.
5. Filtra os que têm valor, ordena por EV e monta cada `ValueBet` com explicação.
6. `main.py` devolve a lista como JSON.
7. O dashboard renderiza os cartões.

## Extensões possíveis (fora do escopo desta demo)

- Trocar `mock.get_matches()` por outra fonte de dados implementando a mesma
  assinatura — sem tocar no serviço nem na API.
- Substituir o `fair_prob` curado por um modelo estatístico de verdade.
- Persistir histórico de sinais e medir acerto ao longo do tempo.
