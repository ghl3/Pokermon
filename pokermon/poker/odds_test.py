from pokermon.poker.board import mkboard
from pokermon.poker.hands import mkhand
from pokermon.poker import odds


def test_evaluation_vs_random():
    res = odds.calculate_odds(hand=mkhand("AcAd"))
    assert 0.80 < res.frac_win < 0.90

    res = odds.calculate_odds(hand=mkhand("AsKd"))
    assert 0.60 < res.frac_win < 0.70

    res = odds.calculate_odds(hand=mkhand("5h5d"))
    assert 0.55 < res.frac_win < 0.65


def test_evaluation_vs_hand():
    res = odds.calculate_odds(hand=mkhand("AcAd"), other_hands=[mkhand("KdKs")])
    assert 0.78 < res.frac_win < 0.88

    res = odds.calculate_odds(hand=mkhand("TcTs"), other_hands=[mkhand("8d9h")])
    assert 0.80 < res.frac_win < 0.90

    res = odds.calculate_odds(hand=mkhand("9d9s"), other_hands=[mkhand("KcQc")])
    assert 0.47 < res.frac_win < 0.57


def test_evaluation_with_board():
    res = odds.calculate_odds(hand=mkhand("AcAd"), board=mkboard("3s5dTc9h"))
    assert 0.84 < res.frac_win < 0.94

    res = odds.calculate_odds(hand=mkhand("AcAd"), board=mkboard("AsAh3d"))
    assert res.frac_win > 0.95


def test_evaluation_vs_hand_with_board():
    res = odds.calculate_odds(
        hand=mkhand("AcAd"), other_hands=[mkhand("KcKs")], board=mkboard("3s5s7s")
    )
    assert 0.52 < res.frac_win < 0.62

    res = odds.calculate_odds(
        hand=mkhand("5s8s"), other_hands=[mkhand("Tc9d")], board=mkboard("6h7cTd")
    )
    assert 0.21 < res.frac_win < 0.31
