# Regras de negócio

> **Aviso obrigatório:** Este projeto é uma demonstração educacional de portfólio e não representa recomendação financeira, promessa de lucro ou incentivo a apostas reais.

## Probabilidade implícita

A probabilidade implícita de uma odd decimal é:

```text
implied_probability = 1 / bookmaker_odds
```

No projeto, esse valor é retornado com 4 casas decimais. Exemplo:

```text
bookmaker_odds = 2.10
implied_probability = 1 / 2.10 = 0.4762
```

## EV+

EV significa valor esperado. A demo estima a probabilidade real a partir da odd
sharp e calcula o EV em porcentagem:

```text
estimated_probability = 1 / sharp_odds
ev_percent = (estimated_probability * bookmaker_odds - 1) * 100
```

Uma oportunidade é marcada como value bet quando:

```text
ev_percent >= min_ev
```

Por padrão, `min_ev` é `3.0`, ou seja, 3%.

## Simplificação de 1/sharp_odds

Usar `1 / sharp_odds` é uma simplificação proposital para manter a demo pequena e
offline. A odd sharp também carrega margem da casa, conhecida como vig ou
overround. Como essa margem está embutida, `1 / sharp_odds` pode superestimar a
probabilidade real e inflar o EV.

Em um sistema de produção, o cálculo deveria receber os dois lados do mercado e
remover a margem antes de usar a probabilidade como referência. Esse processo é
conhecido como de-vig.

## Filtro de EV mínimo

O filtro `min_ev` é uma margem de segurança. Ele reduz o ruído de oportunidades
com EV muito próximo de zero e deixa a análise focada em sinais com folga maior.

Unidade importante: `min_ev` e `ev_percent` estão em porcentagem. Portanto,
`13.51` significa `+13,51%`, não `0.1351`.

## Stake sugerida

`bankroll_service.suggest_stake()` usa uma regra simples de percentual fixo:

```text
stake = bankroll * risk_percent / 100
```

Exemplo:

```text
bankroll = 1000
risk_percent = 1
stake = 10.00
```

Isso é apenas uma ilustração de gestão de risco para portfólio, não uma
recomendação de aposta.

## Dados simulados

Todos os eventos vêm de `app/data/sample_odds.json`. Eles são fictícios,
determinísticos e existem para testes, demonstração e entrevistas. A aplicação
não consulta odds reais, não usa scraping, não envia alertas reais e não depende
de tokens.
