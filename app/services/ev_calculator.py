"""
Cálculo de value betting baseado em odds de uma casa "sharp" como referência.

Ideia
-----
Uma casa de apostas oferece uma *odd decimal*. De toda odd dá pra extrair a
*probabilidade implícita* (1 / odd). Aqui usamos as odds de uma casa "sharp"
(mercado eficiente) como ESTIMATIVA da probabilidade real, e comparamos com as
odds de uma casa comum. Se a odd comum paga mais do que a probabilidade estimada
justifica, o valor esperado (EV) fica positivo.

LIMITAÇÃO IMPORTANTE (honestidade metodológica)
-----------------------------------------------
Usar `probability = 1 / sharp_odds` é uma SIMPLIFICAÇÃO. A odd da casa sharp
também embute a margem dela (o "vig"/"overround"), então `1 / sharp_odds`
*superestima* um pouco a probabilidade real — e, por consequência, o EV calculado
fica um pouco inflado. Num sistema de produção, removeríamos a margem ("de-vig")
usando as odds dos dois lados do mercado antes de tratar como probabilidade.

Mantemos a simplificação aqui de propósito (a demo tem uma odd sharp por seleção,
não o par), mas deixamos o limite explícito. Ver docs/business_rules.md.

POSTURA RESPONSÁVEL: EV positivo é uma medida estatística de longo prazo — não é
recomendação financeira, promessa de lucro nem incentivo a apostas reais.

Convenção de unidades: o EV é devolvido em PORCENTAGEM (ex.: 13.51 = +13,51%).
"""

from __future__ import annotations


def implied_probability(odds: float) -> float:
    """Probabilidade implícita pela odd decimal: 1 / odds.

    - `odds` deve ser > 1.0, senão levanta ValueError.
    - Retorna float arredondado em 4 casas decimais.

    Ex.: odds 1.85 -> 0.5405.
    """
    if odds <= 1:
        raise ValueError(f"odds deve ser maior que 1, recebido: {odds}")
    return round(1 / odds, 4)


def calculate_ev(bookmaker_odds: float, sharp_odds: float) -> float:
    """Valor esperado (EV) em PORCENTAGEM, usando a casa sharp como referência.

    Fórmula:
        probability = 1 / sharp_odds
        ev_percent  = (probability * bookmaker_odds - 1) * 100

    - `bookmaker_odds` e `sharp_odds` devem ser > 1.0, senão ValueError.
    - Calcula a partir das odds cruas (não dos valores arredondados) e arredonda
      só na saída, em 2 casas decimais.

    Ex.: bookmaker 2.10, sharp 1.85 -> (0.5405... * 2.10 - 1) * 100 = +13.51.
    """
    if bookmaker_odds <= 1:
        raise ValueError(f"bookmaker_odds deve ser maior que 1, recebido: {bookmaker_odds}")
    if sharp_odds <= 1:
        raise ValueError(f"sharp_odds deve ser maior que 1, recebido: {sharp_odds}")

    probability = 1 / sharp_odds
    ev = probability * bookmaker_odds - 1
    return round(ev * 100, 2)


def is_value_bet(bookmaker_odds: float, sharp_odds: float, min_ev: float = 3.0) -> bool:
    """Diz se é uma aposta de valor: EV (em %) maior ou igual ao limiar `min_ev`.

    `min_ev` é uma margem de segurança (padrão 3%), porque a estimativa de
    probabilidade tem incerteza.
    """
    return calculate_ev(bookmaker_odds, sharp_odds) >= min_ev
