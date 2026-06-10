"""Dashboard Streamlit da demo ValueBetAI.

O dashboard consome os services diretamente para manter a regra de negócio em um
lugar só. Não há chamada HTTP, scraping, API externa ou envio real de alerta.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd
import streamlit as st

from app import config
from app.services import odds_service

DISCLAIMER = "Este projeto é uma demonstração educacional de portfólio e não representa recomendação financeira, promessa de lucro ou incentivo a apostas reais."


def build_dataframe(events: list[dict[str, Any]]) -> pd.DataFrame:
    """Monta um DataFrame com colunas em ordem amigável para leitura."""
    columns = [
        "sport",
        "event",
        "market",
        "selection",
        "bookmaker",
        "bookmaker_odds",
        "sharp_bookmaker",
        "sharp_odds",
        "implied_probability",
        "ev_percent",
        "is_value_bet",
        "timestamp",
    ]
    return pd.DataFrame(events, columns=columns)


def filter_by_sport(events: list[dict[str, Any]], sport: str) -> list[dict[str, Any]]:
    """Filtra por esporte, mantendo todos quando o seletor estiver em 'todos'."""
    if sport == "todos":
        return events
    return [event for event in events if event["sport"] == sport]


def sport_with_most_opportunities(value_bets: list[dict[str, Any]]) -> str:
    """Retorna o esporte com mais value bets no recorte atual."""
    if not value_bets:
        return "sem oportunidades"
    counter = Counter(event["sport"] for event in value_bets)
    sport, total = counter.most_common(1)[0]
    return f"{sport} ({total})"


def render_metrics(events: list[dict[str, Any]], value_bets: list[dict[str, Any]]) -> None:
    """Exibe métricas principais do recorte filtrado."""
    highest_ev = max((event["ev_percent"] for event in events), default=0.0)
    metric_cols = st.columns(4)
    metric_cols[0].metric("Eventos analisados", len(events))
    metric_cols[1].metric("Value bets", len(value_bets))
    metric_cols[2].metric("Maior EV", f"{highest_ev:.2f}%")
    metric_cols[3].metric("Esporte com mais oportunidades", sport_with_most_opportunities(value_bets))


def render_formula_block() -> None:
    """Explica a fórmula e a limitação metodológica em linguagem simples."""
    st.subheader("Como o EV é calculado")
    st.markdown(
        """
        A demo usa a odd de uma casa sharp como referência aproximada da
        probabilidade real:

        `probabilidade = 1 / sharp_odds`

        Depois compara essa probabilidade com a odd oferecida pela casa comum:

        `EV (%) = (probabilidade * bookmaker_odds - 1) * 100`

        Exemplo: com `bookmaker_odds = 2.10` e `sharp_odds = 1.85`, o EV é
        `+13.51%`.

        Limitação importante: usar `1 / sharp_odds` é uma simplificação. A odd
        sharp também embute margem da casa, o "vig" ou "overround"; por isso a
        probabilidade estimada pode ficar alta demais e o EV calculado tende a
        ser inflado. Em produção, seria necessário remover essa margem com um
        processo de de-vig usando os dois lados do mercado.
        """
    )


def main() -> None:
    """Renderiza a aplicação Streamlit."""
    st.set_page_config(page_title=config.PROJECT_NAME, layout="wide")

    st.title(config.PROJECT_NAME)
    st.warning(DISCLAIMER, icon="⚠️")
    st.caption("Demo 100% offline, com dados simulados carregados de app/data/sample_odds.json.")

    min_ev = st.slider(
        "EV mínimo (%)",
        min_value=0.0,
        max_value=15.0,
        value=float(config.MIN_EV_PERCENT),
        step=0.5,
    )
    sport = st.selectbox("Esporte", ["todos", "tennis", "football", "basketball"])

    raw_odds = odds_service.load_sample_odds()
    enriched_odds = odds_service.enrich_odds_with_ev(raw_odds, min_ev=min_ev)
    filtered_odds = filter_by_sport(enriched_odds, sport)
    value_bets = [event for event in filtered_odds if event["is_value_bet"]]

    render_metrics(filtered_odds, value_bets)

    st.subheader("Todas as odds enriquecidas")
    st.dataframe(build_dataframe(filtered_odds), width="stretch", hide_index=True)

    st.subheader(f"Value bets com EV >= {min_ev:.1f}%")
    if value_bets:
        st.dataframe(build_dataframe(value_bets), width="stretch", hide_index=True)
    else:
        st.info("Nenhuma oportunidade encontrada para os filtros atuais.")

    render_formula_block()

    st.markdown(
        """
        Esta interface existe para demonstrar organização de produto, API e
        regra de negócio em um projeto de portfólio. Os eventos são simulados,
        determinísticos e não representam mercado real.
        """
    )


if __name__ == "__main__":
    main()
