# Roteiro de demonstração

> **Aviso obrigatório:** Este projeto é uma demonstração educacional de portfólio e não representa recomendação financeira, promessa de lucro ou incentivo a apostas reais.

## Pitch curto

ValueBetAI Portfolio Demo é uma aplicação Python 100% offline que simula uma
esteira de análise de value bets. Ela carrega odds mockadas, calcula EV em
porcentagem, expõe uma API FastAPI e oferece um dashboard Streamlit que reutiliza
os mesmos services da API.

## Roteiro para entrevista

1. Abrir o README e destacar a postura responsável: dados simulados, sem tokens e
   sem promessa de resultado.
2. Mostrar `app/services/ev_calculator.py` para explicar a fórmula:
   `EV (%) = ((1 / sharp_odds) * bookmaker_odds - 1) * 100`.
3. Explicar a limitação do vig: a odd sharp não é probabilidade pura, então um
   produto real precisaria de de-vig.
4. Mostrar `app/services/odds_service.py`: a API e o dashboard compartilham a
   mesma regra de negócio.
5. Subir a API com `.venv/bin/uvicorn app.main:app --reload` e abrir `/docs`.
6. Chamar `/calculate-ev` com `bookmaker_odds=2.10` e `sharp_odds=1.85` para
   mostrar `ev_percent=13.51`.
7. Abrir o dashboard com `.venv/bin/streamlit run dashboard.py`.
8. Alterar o slider de EV mínimo e o filtro de esporte para mostrar a interação.
9. Rodar `.venv/bin/python -m pytest -q` para fechar com evidência de qualidade.
10. Mostrar Docker/Compose como caminho de execução isolado.

## Roteiro para post no LinkedIn

Criei uma demo de portfólio em Python para análise educacional de value bets.

O projeto usa FastAPI, Streamlit, Pydantic, Pandas, Pytest e Docker. A aplicação
é 100% offline: não usa API real de odds, não usa token, não faz scraping e não
envia alertas reais. A ideia é demonstrar arquitetura, testes e clareza de regra
de negócio com dados simulados.

Pontos técnicos:

- API com Swagger e contratos Pydantic.
- Dashboard Streamlit importando os services diretamente.
- Cálculo de EV em porcentagem com explicação da limitação metodológica.
- Testes automatizados e workflow de CI.
- Docker Compose para subir a API localmente.

Também deixei a ressalva responsável explícita: é uma demonstração educacional,
sem recomendação financeira, promessa de lucro ou incentivo a apostas reais.

## Pontos para explicar a recrutadores

- A regra de negócio não está duplicada entre API e dashboard.
- Os dados são determinísticos, o que facilita teste e demonstração.
- Os endpoints são finos e delegam cálculo aos services.
- O projeto evita segredos e dependências externas por design.
- A documentação assume limitações do modelo em vez de vender precisão falsa.
- A estrutura permite evolução para fontes reais mantendo mocks nos testes.

## Comandos da demo

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/uvicorn app.main:app --reload
.venv/bin/streamlit run dashboard.py
docker compose up --build
```
