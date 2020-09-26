from pokermon.poker import odds
from pokermon.poker.board import Board, mkboard, mkflop
from pokermon.poker.cards import mkcard
from pokermon.poker.hands import mkhand
from pokermon.poker.odds import NutResult, make_nut_result


def test_evaluation_vs_random():
    res = odds.calculate_odds(hand=mkhand("AcAd"))
    assert 0.80 < res.frac_win < 0.90

    res = odds.calculate_odds(hand=mkhand("AsKd"))
    assert 0.60 < res.frac_win < 0.70

    res = odds.calculate_odds(hand=mkhand("5h5d"))
    assert 0.55 < res.frac_win < 0.65


def test_evaluation_vs_hand():
    res = odds.calculate_odds(hand=mkhand("AcAd"), other_hands=(mkhand("KdKs"),))
    assert 0.78 < res.frac_win < 0.88

    res = odds.calculate_odds(hand=mkhand("TcTs"), other_hands=(mkhand("8d9h"),))
    assert 0.80 < res.frac_win < 0.90

    res = odds.calculate_odds(hand=mkhand("9d9s"), other_hands=(mkhand("KcQc"),))
    assert 0.47 < res.frac_win < 0.57


def test_evaluation_with_board():
    res = odds.calculate_odds(hand=mkhand("AcAd"), board=mkboard("3s5dTc9h"))
    assert 0.84 < res.frac_win < 0.94

    res = odds.calculate_odds(hand=mkhand("AcAd"), board=mkboard("AsAh3d"))
    assert res.frac_win > 0.95


def test_evaluation_vs_hand_with_board():
    res = odds.calculate_odds(
        hand=mkhand("AcAd"), other_hands=(mkhand("KcKs"),), board=mkboard("3s5s7s")
    )
    assert 0.52 < res.frac_win < 0.62

    res = odds.calculate_odds(
        hand=mkhand("5s8s"), other_hands=(mkhand("Tc9d"),), board=mkboard("6h7cTd")
    )
    assert 0.21 < res.frac_win < 0.31


def test_royal() -> None:
    hole_cards = mkhand("AcKc")
    board = Board(flop=mkflop("TcJcQc"))

    nr = make_nut_result(hole_cards, board)
    assert len(nr.better_hands) == 0
    assert len(nr.tied_hands) == 0
    assert len(nr.worse_hands) == 1081


def test_wheel() -> None:
    hole_cards = mkhand("2c7d")
    board = Board(flop=mkflop("3h4c5s"))

    nr = make_nut_result(hole_cards, board)
    assert len(nr.better_hands) == 1072
    assert len(nr.tied_hands) == 9
    assert len(nr.worse_hands) == 0


def test_winner() -> None:
    hole_cards = mkhand("AdAc")
    board = Board(flop=mkflop("AhKs3h"), turn=mkcard("5h"), river=mkcard("7s"))

    nr = make_nut_result(hole_cards, board)
    assert len(nr.better_hands) == 75
    assert len(nr.tied_hands) == 0
    assert len(nr.worse_hands) == 915


def test_turn() -> None:
    hole_cards = mkhand("7d8s")
    board = Board(flop=mkflop("5h6cJs"), turn=mkcard("5h"))

    nr = make_nut_result(hole_cards, board)
    assert len(nr.better_hands) == 952
    assert len(nr.tied_hands) == 9
    assert len(nr.worse_hands) == 120
