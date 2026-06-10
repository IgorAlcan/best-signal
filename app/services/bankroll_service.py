"""
Gestão de banca (bankroll) — sugestão de stake por gerenciamento de risco fixo.

Ideia: apostar sempre uma fração pequena e fixa da banca (ex.: 1%) por aposta é
uma regra de gestão de risco simples e conhecida ("fixed fractional"). Ela limita
a exposição e protege contra sequências ruins.

POSTURA RESPONSÁVEL: isto é uma ilustração educacional de gestão de risco, não
recomendação de aposta.
"""

from __future__ import annotations


def suggest_stake(bankroll: float, risk_percent: float = 1.0) -> float:
    """Sugere o valor a apostar: uma porcentagem fixa da banca.

    Fórmula: stake = bankroll * risk_percent / 100

    Regras:
    - `bankroll` deve ser > 0.
    - `risk_percent` deve estar em (0, 100].
    - Caso inválido, levanta ValueError.
    - Retorna float arredondado em 2 casas decimais.

    Ex.: bankroll 1000, risk 1% -> 10.00.
    """
    if bankroll <= 0:
        raise ValueError(f"bankroll deve ser maior que 0, recebido: {bankroll}")
    if not (0 < risk_percent <= 100):
        raise ValueError(f"risk_percent deve estar em (0, 100], recebido: {risk_percent}")
    return round(bankroll * risk_percent / 100, 2)
