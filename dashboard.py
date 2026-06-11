"""Dashboard Streamlit da demo ValueBetAI.

O dashboard consome os services diretamente para manter a regra de negócio em um
lugar só. Não há chamada HTTP, scraping, API externa ou envio real de alerta.

Identidade visual: tema escuro "fintech analytics" (OLED), tipografia Fira Sans /
Fira Code (números tabulares para colunas de dados), azul como cor de dados e
âmbar/verde como destaques. O objetivo é uma leitura profissional e intuitiva.
"""

from __future__ import annotations

from collections import Counter
from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from app import config
from app.services import odds_service

DISCLAIMER = "Este projeto é uma demonstração educacional de portfólio e não representa recomendação financeira, promessa de lucro ou incentivo a apostas reais."
SPORT_OPTIONS = ["todos", "tennis", "football", "basketball"]
SPORT_LABELS = {
    "todos": "Todos os esportes",
    "tennis": "Tênis",
    "football": "Futebol",
    "basketball": "Basquete",
}
VISIBLE_COLUMNS = [
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


def inject_page_style() -> None:
    """Aplica a identidade visual escura (fintech analytics) ao dashboard."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700;800&display=swap');

            :root {
                --bg: #0a0e17;
                --surface: #131a27;
                --surface-2: #192334;
                --border: #233047;
                --text: #e8eef7;
                --text-strong: #f6f9ff;
                --muted: #8696ad;
                --faint: #5d6b80;
                --book: #3b82f6;          /* azul = dados / casa */
                --book-soft: #1e3a8a;
                --signal: #2dd4a7;         /* verde = EV+ / valor */
                --accent: #f59e0b;         /* âmbar = destaque */
                --danger: #f87171;
                --display-font: "Fira Sans", "Segoe UI", sans-serif;
                --body-font: "Fira Sans", "Segoe UI", sans-serif;
                --data-font: "Fira Code", "SFMono-Regular", "Menlo", monospace;
            }

            .stApp {
                background:
                    radial-gradient(1100px 540px at 82% -8%, rgba(59, 130, 246, 0.10), transparent 60%),
                    radial-gradient(900px 480px at 8% 4%, rgba(45, 212, 167, 0.06), transparent 55%),
                    var(--bg);
                color: var(--text);
                font-family: var(--body-font);
            }

            .block-container {
                max-width: 1240px;
                padding-top: 1.4rem;
                padding-bottom: 3.5rem;
            }

            /* Tipografia tabular para qualquer número exibido em colunas de dados. */
            [data-testid="stMetricValue"],
            .stDataFrame,
            .tape-ev,
            .tape-meta,
            .data-chip {
                font-variant-numeric: tabular-nums;
            }

            section[data-testid="stSidebar"] {
                background: #0c121d;
                border-right: 1px solid var(--border);
            }
            section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
                color: var(--text-strong);
                font-weight: 600;
            }
            section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
                color: var(--muted);
            }

            /* Foco visível (acessibilidade) */
            button:focus-visible,
            [role="tab"]:focus-visible,
            input:focus-visible,
            select:focus-visible,
            [data-baseweb="select"]:focus-within > div {
                outline: 3px solid var(--accent);
                outline-offset: 2px;
            }

            /* ---- Métricas ---- */
            [data-testid="stMetric"] {
                background: linear-gradient(180deg, var(--surface), #10182447);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 1.05rem 1.1rem;
                transition: border-color 180ms ease, transform 180ms ease;
            }
            [data-testid="stMetric"]:hover {
                border-color: var(--book);
                transform: translateY(-2px);
            }
            [data-testid="stMetricLabel"] {
                color: var(--muted);
                font-family: var(--data-font);
                font-size: 0.74rem;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }
            [data-testid="stMetricValue"] {
                color: var(--text-strong);
                font-family: var(--display-font);
                font-size: 1.9rem;
                font-weight: 750;
            }
            [data-testid="stMetricDelta"] { color: var(--signal); }

            div[data-testid="stAlert"] {
                background: #1c160a;
                border: 1px solid #4a3a16;
                border-left: 4px solid var(--accent);
                border-radius: 10px;
            }
            div[data-testid="stAlert"] * { color: #f2dca0 !important; }

            /* ---- Cabeçalho ---- */
            .app-header {
                background:
                    linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(45, 212, 167, 0.05) 60%),
                    var(--surface);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 1.6rem 1.7rem;
                margin-bottom: 1rem;
                position: relative;
                overflow: hidden;
            }
            .app-header::after {
                content: "";
                position: absolute;
                inset: 0;
                background: repeating-linear-gradient(90deg, transparent 0 28px, rgba(255,255,255,0.015) 28px 29px);
                pointer-events: none;
            }
            .app-kicker {
                color: var(--accent);
                font-family: var(--data-font);
                font-size: 0.76rem;
                font-weight: 600;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
                position: relative; z-index: 1;
            }
            .app-title {
                color: var(--text-strong);
                font-family: var(--display-font);
                font-size: 2.5rem;
                font-weight: 800;
                line-height: 1.05;
                margin: 0;
                letter-spacing: -0.01em;
                position: relative; z-index: 1;
            }
            .app-title span { color: var(--book); }
            .app-subtitle {
                color: var(--muted);
                font-size: 1rem;
                line-height: 1.6;
                margin: 0.6rem 0 0;
                max-width: 720px;
                position: relative; z-index: 1;
            }
            .status-strip {
                display: flex; flex-wrap: wrap; gap: 0.5rem;
                margin-top: 1.1rem; position: relative; z-index: 1;
            }
            .status-pill {
                align-items: center;
                background: rgba(59, 130, 246, 0.10);
                border: 1px solid rgba(59, 130, 246, 0.30);
                border-radius: 999px;
                color: #bcd4f7;
                display: inline-flex;
                font-family: var(--data-font);
                font-size: 0.8rem;
                font-weight: 500;
                min-height: 2rem;
                padding: 0.3rem 0.75rem;
            }

            /* ---- Fita de oportunidades ---- */
            .market-tape {
                display: grid;
                gap: 0.7rem;
                grid-template-columns: repeat(auto-fit, minmax(178px, 1fr));
                margin: 0.4rem 0 1.3rem;
            }
            .tape-cell {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 0.9rem 0.95rem;
                transition: border-color 180ms ease, transform 180ms ease;
            }
            .tape-cell:hover { border-color: var(--signal); transform: translateY(-2px); }
            .tape-sport {
                color: var(--book);
                font-family: var(--data-font);
                font-size: 0.7rem; font-weight: 600;
                letter-spacing: 0.05em; text-transform: uppercase;
            }
            .tape-selection {
                color: var(--text-strong);
                font-size: 0.98rem; font-weight: 700;
                line-height: 1.25; margin-top: 0.4rem;
            }
            .tape-meta {
                color: var(--muted);
                font-family: var(--data-font);
                font-size: 0.74rem; margin-top: 0.5rem;
            }
            .tape-ev {
                color: var(--signal);
                font-family: var(--data-font);
                font-size: 1.2rem; font-weight: 700;
                margin-top: 0.45rem;
            }
            .tape-empty {
                background: var(--surface); border: 1px dashed var(--border);
                border-radius: 12px; padding: 1rem; color: var(--muted);
                grid-column: 1 / -1;
            }

            /* ---- Cartões de seção ---- */
            .section-card {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 1.05rem 1.2rem;
                transition: border-color 180ms ease, transform 180ms ease;
            }
            .section-card:hover { border-color: #314563; transform: translateY(-1px); }
            .section-card h3 {
                color: var(--text-strong);
                font-family: var(--display-font);
                font-size: 1rem; font-weight: 700; margin: 0 0 0.5rem;
            }
            .section-card p { color: var(--muted); line-height: 1.6; margin: 0 0 0.4rem; }
            .section-card code {
                background: #0c1320; border: 1px solid var(--border);
                border-radius: 6px; color: #cfe0f7; font-family: var(--data-font);
                font-size: 0.82rem; padding: 0.1rem 0.4rem;
            }
            .opportunity-callout { border-left: 4px solid var(--signal); }
            .risk-callout { border-left: 4px solid var(--accent); }

            .data-chip {
                background: #0c1320; border: 1px solid var(--border);
                border-radius: 6px; color: #aebfd6;
                display: inline-block; font-family: var(--data-font);
                font-size: 0.76rem; margin: 0.4rem 0.3rem 0 0; padding: 0.25rem 0.5rem;
            }

            h2, h3 { color: var(--text-strong); font-family: var(--display-font); }

            .stDataFrame { border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
            [data-testid="stTabs"] button { font-family: var(--data-font); }

            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    transition-duration: 0.01ms !important;
                    scroll-behavior: auto !important;
                }
            }
            @media (max-width: 640px) {
                .block-container { padding-left: 0.9rem; padding-right: 0.9rem; }
                .app-title { font-size: 1.95rem; }
                .market-tape { grid-template-columns: 1fr; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_dataframe(events: list[dict[str, Any]]) -> pd.DataFrame:
    """Monta um DataFrame com colunas em ordem amigável para leitura."""
    return pd.DataFrame(events, columns=VISIBLE_COLUMNS)


def filter_by_sport(events: list[dict[str, Any]], sport: str) -> list[dict[str, Any]]:
    """Filtra por esporte, mantendo todos quando o seletor estiver em 'todos'."""
    if sport == "todos":
        return events
    return [event for event in events if event["sport"] == sport]


def sort_by_ev(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ordena eventos do maior para o menor EV."""
    return sorted(events, key=lambda event: float(event["ev_percent"]), reverse=True)


def sport_with_most_opportunities(value_bets: list[dict[str, Any]]) -> str:
    """Retorna o esporte com mais value bets no recorte atual."""
    if not value_bets:
        return "—"
    counter = Counter(event["sport"] for event in value_bets)
    sport, total = counter.most_common(1)[0]
    return f"{SPORT_LABELS.get(sport, sport)} ({total})"


def build_sport_summary(events: list[dict[str, Any]]) -> pd.DataFrame:
    """Agrupa eventos por esporte para visualização executiva."""
    if not events:
        return pd.DataFrame(columns=["sport", "events", "value_bets", "highest_ev"])

    frame = pd.DataFrame(events)
    summary = (
        frame.groupby("sport", as_index=False)
        .agg(
            events=("event", "count"),
            value_bets=("is_value_bet", "sum"),
            highest_ev=("ev_percent", "max"),
        )
        .sort_values(["value_bets", "highest_ev"], ascending=[False, False])
    )
    summary["value_bets"] = summary["value_bets"].astype(int)
    return summary


def summarize_sport_chart(summary: pd.DataFrame) -> str:
    """Gera um resumo textual do gráfico para leitura e acessibilidade."""
    if summary.empty:
        return "Sem eventos no recorte atual."

    leader = summary.iloc[0]
    label = SPORT_LABELS.get(leader["sport"], leader["sport"])
    return (
        f"{label} lidera o recorte com {int(leader['value_bets'])} "
        f"sinais EV+ e pico de {float(leader['highest_ev']):.2f}%."
    )


def get_column_config() -> dict[str, Any]:
    """Define rótulos e formatos das tabelas."""
    return {
        "sport": st.column_config.TextColumn("Esporte"),
        "event": st.column_config.TextColumn("Evento", width="large"),
        "selection": st.column_config.TextColumn("Seleção", width="medium"),
        "market": st.column_config.TextColumn("Mercado"),
        "bookmaker": st.column_config.TextColumn("Casa"),
        "bookmaker_odds": st.column_config.NumberColumn("Odd casa", format="%.2f"),
        "sharp_bookmaker": st.column_config.TextColumn("Sharp"),
        "sharp_odds": st.column_config.NumberColumn("Odd sharp", format="%.2f"),
        "implied_probability": st.column_config.NumberColumn("Prob. implícita", format="%.4f"),
        "ev_percent": st.column_config.NumberColumn("EV (%)", format="%.2f"),
        "is_value_bet": st.column_config.CheckboxColumn("EV+"),
        "timestamp": st.column_config.TextColumn("Coleta"),
    }


def render_header(total_events: int) -> None:
    """Exibe o topo do dashboard."""
    st.markdown(
        f"""
        <div class="app-header">
            <div class="app-kicker">Mesa de análise · dados simulados · EV em %</div>
            <h1 class="app-title">ValueBet<span>AI</span></h1>
            <p class="app-subtitle">
                Painel de análise de apostas de valor (EV+) sobre dados simulados.
                Compara odds de casas comuns com uma casa de referência (sharp),
                calcula o valor esperado e separa os sinais positivos — com a
                metodologia explicada de forma transparente.
            </p>
            <div class="status-strip">
                <span class="status-pill">feed local · {total_events} eventos</span>
                <span class="status-pill">100% mock</span>
                <span class="status-pill">sem execução real</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.warning(DISCLAIMER)


def render_sidebar() -> tuple[str, float]:
    """Renderiza os filtros e retorna as escolhas do usuário."""
    with st.sidebar:
        st.header("Filtros")
        sport = st.selectbox(
            "Esporte",
            SPORT_OPTIONS,
            format_func=lambda value: SPORT_LABELS.get(value, value),
        )
        min_ev = st.slider(
            "EV mínimo (%)",
            min_value=0.0,
            max_value=15.0,
            value=float(config.MIN_EV_PERCENT),
            step=0.5,
            help="Apostas com EV abaixo deste corte não são marcadas como sinal.",
        )

        st.divider()
        st.subheader("Como ler")
        st.caption("EV+ = valor esperado positivo, em porcentagem.")
        st.caption("Fonte: app/data/sample_odds.json (offline).")

    return sport, min_ev


def render_market_tape(value_bets: list[dict[str, Any]]) -> None:
    """Renderiza a fita visual das melhores oportunidades EV+."""
    # IMPORTANTE: o HTML é emitido SEM indentação por linha. Streamlit interpreta
    # blocos indentados (4+ espaços) como bloco de código e mostraria a tag crua.
    if not value_bets:
        st.markdown(
            '<div class="market-tape"><div class="tape-empty">'
            "Nenhum sinal EV+ no recorte atual — ajuste o EV mínimo ou o esporte."
            "</div></div>",
            unsafe_allow_html=True,
        )
        return

    cells = []
    for event in value_bets[:6]:
        sport = escape(SPORT_LABELS.get(str(event["sport"]), str(event["sport"])))
        selection = escape(str(event["selection"]))
        bookmaker_odds = float(event["bookmaker_odds"])
        sharp_odds = float(event["sharp_odds"])
        ev_percent = float(event["ev_percent"])
        cells.append(
            '<div class="tape-cell">'
            f'<div class="tape-sport">{sport}</div>'
            f'<div class="tape-selection">{selection}</div>'
            f'<div class="tape-meta">casa {bookmaker_odds:.2f} · sharp {sharp_odds:.2f}</div>'
            f'<div class="tape-ev">+{ev_percent:.2f}% EV</div>'
            "</div>"
        )

    st.markdown(
        f'<div class="market-tape">{"".join(cells)}</div>',
        unsafe_allow_html=True,
    )


def render_metrics(events: list[dict[str, Any]], value_bets: list[dict[str, Any]]) -> None:
    """Exibe métricas principais do recorte filtrado."""
    highest_ev = max((event["ev_percent"] for event in events), default=0.0)
    value_rate = (len(value_bets) / len(events) * 100) if events else 0.0

    metric_cols = st.columns(4)
    metric_cols[0].metric("Eventos analisados", len(events))
    metric_cols[1].metric("Sinais de valor (EV+)", len(value_bets), f"{value_rate:.0f}% do recorte")
    metric_cols[2].metric("Maior EV", f"{highest_ev:.2f}%")
    metric_cols[3].metric("Esporte líder", sport_with_most_opportunities(value_bets))


def render_overview(events: list[dict[str, Any]], value_bets: list[dict[str, Any]]) -> None:
    """Mostra resumo visual do recorte atual."""
    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.subheader("Oportunidades por esporte")
        summary = build_sport_summary(events)
        if summary.empty:
            st.info("Nenhum evento encontrado para os filtros atuais.")
        else:
            chart_data = summary.set_index("sport")[["events", "value_bets"]]
            chart_data.columns = ["Eventos", "Sinais EV+"]
            st.bar_chart(chart_data, color=["#3b82f6", "#2dd4a7"], height=280)
            st.caption(summarize_sport_chart(summary))

    with right:
        st.subheader("Maior oportunidade")
        top_bet = value_bets[0] if value_bets else None
        if top_bet:
            st.markdown(
                f"""
                <div class="section-card opportunity-callout">
                    <h3>Top sinal do recorte</h3>
                    <p><strong>{escape(str(top_bet["selection"]))}</strong> · {escape(str(top_bet["event"]))}</p>
                    <span class="data-chip">EV {top_bet["ev_percent"]:.2f}%</span>
                    <span class="data-chip">casa {top_bet["bookmaker_odds"]:.2f}</span>
                    <span class="data-chip">sharp {top_bet["sharp_odds"]:.2f}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="section-card opportunity-callout">
                    <h3>Sem sinal EV+</h3>
                    <p>Os filtros atuais não encontram eventos com EV acima do mínimo escolhido.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div class="section-card risk-callout" style="margin-top: 0.75rem;">
                <h3>Limite metodológico</h3>
                <p>Dados simulados; a probabilidade derivada da odd sharp ainda
                carrega vig. A interface mostra análise técnica, não decisão de aposta.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_recruiter_proof() -> None:
    """Mostra evidências técnicas em linguagem de portfólio."""
    st.subheader("Evidências para revisão técnica")
    proof_cols = st.columns(3, gap="large")
    cards = [
        (
            "Regra centralizada",
            "API e dashboard consomem os mesmos services; o EV não é recalculado na interface.",
        ),
        (
            "Demo auditável",
            "Dados simulados, sem segredo, sem scraping e com testes offline reproduzíveis.",
        ),
        (
            "Entrega operável",
            "FastAPI, Swagger, Streamlit, Docker Compose e CI organizados para avaliação rápida.",
        ),
    ]

    for column, (title, body) in zip(proof_cols, cards, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="section-card">
                    <h3>{escape(title)}</h3>
                    <p>{escape(body)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_value_bets_table(value_bets: list[dict[str, Any]], min_ev: float) -> None:
    """Exibe a tabela principal de oportunidades."""
    st.subheader(f"Sinais EV+ (corte ≥ {min_ev:.1f}%)")
    if not value_bets:
        st.info("Nenhuma oportunidade encontrada para os filtros atuais.")
        return

    st.dataframe(
        build_dataframe(value_bets),
        column_config=get_column_config(),
        column_order=VISIBLE_COLUMNS,
        height=360,
        hide_index=True,
        width="stretch",
    )


def render_all_odds_table(events: list[dict[str, Any]]) -> None:
    """Exibe todas as odds enriquecidas do recorte."""
    st.subheader("Tabela completa de odds")
    st.dataframe(
        build_dataframe(events),
        column_config=get_column_config(),
        column_order=VISIBLE_COLUMNS,
        height=460,
        hide_index=True,
        width="stretch",
    )


def render_formula_block() -> None:
    """Explica a fórmula e a limitação metodológica em linguagem simples."""
    st.subheader("Metodologia")
    formula_col, limit_col = st.columns(2, gap="large")

    with formula_col:
        st.markdown(
            """
            <div class="section-card">
                <h3>Modelo de EV</h3>
                <p>A demo usa a odd sharp como referência aproximada:</p>
                <p><code>probabilidade = 1 / sharp_odds</code></p>
                <p><code>EV (%) = (probabilidade × bookmaker_odds − 1) × 100</code></p>
                <p>Exemplo: casa 2.10 e sharp 1.85 resultam em <strong>+13.51%</strong>.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with limit_col:
        st.markdown(
            """
            <div class="section-card risk-callout">
                <h3>Vig embutido (limite honesto)</h3>
                <p>Usar <code>1 / sharp_odds</code> é uma simplificação: a odd sharp
                também embute a margem da casa (vig/overround), então a probabilidade
                estimada fica alta demais e o EV tende a ser inflado.</p>
                <p>Em produção, o ideal seria remover essa margem (de-vig) usando os
                dois lados do mercado.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    """Renderiza a aplicação Streamlit."""
    st.set_page_config(page_title=config.PROJECT_NAME, page_icon="📊", layout="wide")
    inject_page_style()

    raw_odds = odds_service.load_sample_odds()
    sport, min_ev = render_sidebar()
    enriched_odds = odds_service.enrich_odds_with_ev(raw_odds, min_ev=min_ev)
    filtered_odds = sort_by_ev(filter_by_sport(enriched_odds, sport))
    value_bets = [event for event in filtered_odds if event["is_value_bet"]]

    render_header(total_events=len(raw_odds))
    render_metrics(filtered_odds, value_bets)
    render_market_tape(value_bets)
    render_overview(filtered_odds, value_bets)
    render_recruiter_proof()

    tabs = st.tabs(["Sinais EV+", "Tabela completa", "Metodologia"])
    with tabs[0]:
        render_value_bets_table(value_bets, min_ev)
    with tabs[1]:
        render_all_odds_table(filtered_odds)
    with tabs[2]:
        render_formula_block()
        st.markdown(
            """
            Esta interface demonstra organização de produto, API e regra de negócio
            em um projeto de portfólio. Os eventos são simulados, determinísticos e
            não representam mercado real.
            """
        )


if __name__ == "__main__":
    main()
