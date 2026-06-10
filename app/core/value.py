"""
Núcleo de "value betting" — a matemática que decide se uma aposta tem valor.

Ideia central
-------------
Uma casa de apostas oferece uma *odd decimal* (ex.: 2.00 = você recebe R$2 por
cada R$1 apostado, se acertar). Dessa odd dá pra extrair a *probabilidade
implícita* que a casa atribui ao evento.

Se a NOSSA estimativa de probabilidade ("probabilidade justa") for MAIOR do que a
implícita pela odd, existe uma vantagem matemática a nosso favor — é a chamada
*value bet* (aposta de valor). O valor esperado (EV) positivo é o sinal.

IMPORTANTE (postura responsável): EV positivo NÃO garante lucro nem acerto. É
apenas uma medida estatística de longo prazo, e depende inteiramente de a nossa
estimativa de probabilidade ser boa. Este módulo só calcula os números; não
promete resultado.

Convenções de nomes (código em inglês, explicação em português):
- odds  -> odd decimal (decimal odds), sempre > 1.0
- prob  -> probabilidade justa estimada, no intervalo (0, 1)
"""

from __future__ import annotations


def implied_probability(odds: float) -> float:
    """Probabilidade implícita pela odd decimal.

    É simplesmente 1 / odd. Inclui a margem da casa (o "vig"/"juice"), por isso a
    soma das implícitas de todos os resultados de um jogo passa de 100%.

    Ex.: odd 2.00 -> 0.50 (a casa precifica 50% de chance).
    """
    if odds <= 1.0:
        raise ValueError(f"odd decimal deve ser > 1.0, recebido: {odds}")
    return 1.0 / odds


def edge(prob: float, odds: float) -> float:
    """Vantagem (edge) = nossa probabilidade − probabilidade implícita pela odd.

    Positivo  -> achamos o evento mais provável do que a casa precifica.
    Negativo  -> a casa precifica mais provável do que nós; não é value.

    Ex.: prob=0.55, odd=2.00 -> 0.55 − 0.50 = 0.05 (5% de edge).
    """
    _validate_prob(prob)
    return prob - implied_probability(odds)


def expected_value(prob: float, odds: float) -> float:
    """Valor esperado (EV) por 1 unidade apostada.

    Fórmula: EV = prob * (odds − 1) − (1 − prob)
             EV = prob * odds − 1

    Interpretação: lucro médio por unidade no longo prazo, SE a nossa `prob`
    estiver correta. EV = 0.08 significa +8% de retorno esperado por aposta.

    EV > 0 é a condição de value bet (equivale a prob > probabilidade implícita).
    """
    _validate_prob(prob)
    if odds <= 1.0:
        raise ValueError(f"odd decimal deve ser > 1.0, recebido: {odds}")
    return prob * odds - 1.0


def kelly_fraction(prob: float, odds: float) -> float:
    """Fração de Kelly — quanto da banca apostar para maximizar crescimento.

    Fórmula: f* = (prob * odds − 1) / (odds − 1) = EV / (odds − 1)

    Retorna 0.0 quando não há valor (EV <= 0), pois Kelly nunca recomenda apostar
    sem vantagem. Na prática usa-se uma fração do Kelly (ex.: "quarter Kelly") por
    ser mais conservador; aqui devolvemos o Kelly cheio e deixamos a decisão de
    escalar para a camada de cima.
    """
    _validate_prob(prob)
    if odds <= 1.0:
        raise ValueError(f"odd decimal deve ser > 1.0, recebido: {odds}")
    ev = expected_value(prob, odds)
    if ev <= 0.0:
        return 0.0
    return ev / (odds - 1.0)


def is_value_bet(prob: float, odds: float, min_ev: float = 0.0) -> bool:
    """Diz se é uma aposta de valor: EV acima de um limiar mínimo.

    `min_ev` permite exigir uma margem de segurança (ex.: 0.05 = só aceita EV>=5%),
    útil porque nossa estimativa de `prob` tem incerteza.
    """
    return expected_value(prob, odds) >= min_ev


def _validate_prob(prob: float) -> None:
    """Garante que a probabilidade está no intervalo aberto (0, 1)."""
    if not (0.0 < prob < 1.0):
        raise ValueError(f"probabilidade deve estar em (0, 1), recebido: {prob}")
