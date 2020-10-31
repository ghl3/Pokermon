from pokermon.poker.board import Board, mkflop
from pokermon.poker.cards import mkcard
from pokermon.poker.evaluation import EvaluationResult, evaluate_hand
from pokermon.poker.hands import HandType, mkhand


def test_royal() -> None:
    hole_cards = mkhand("AcKc")
    board = Board(flop=mkflop("TcJcQc"))
    eval_result = evaluate_hand(hole_cards, board)
    assert eval_result == EvaluationResult(hand_type=HandType.STRAIGHT_FLUSH, kicker=9)


def test_wheel() -> None:
    hole_cards = mkhand("2c7d")
    board = Board(flop=mkflop("3h4c5s"))
    eval_result = evaluate_hand(hole_cards, board)
    assert eval_result == EvaluationResult(hand_type=HandType.HIGH, kicker=47)


def test_winner() -> None:
    hole_cards = mkhand("AdAc")
    board = Board(flop=mkflop("AdKs3h"), turn=mkcard("5h"), river=mkcard("7s"))
    eval_result = evaluate_hand(hole_cards, board)
    assert eval_result == EvaluationResult(hand_type=HandType.TRIPS, kicker=33556512)


def test_turn() -> None:
    hole_cards = mkhand("7d8s")
    board = Board(flop=mkflop("5h6cJs"), turn=mkcard("5h"))
    eval_result = evaluate_hand(hole_cards, board)
    assert eval_result == EvaluationResult(hand_type=HandType.PAIR, kicker=66144)


def sanity_tests() -> None:

    # Order doesn't matter
    assert evaluate_hand(mkhand("7d8s"), Board(flop=mkflop("5h6cJs"))) == evaluate_hand(
        mkhand("5hJs"), Board(flop=mkflop("7d8s6c"))
    )

    # Suits don't matter for non-flushes
    assert evaluate_hand(mkhand("7d8s"), Board(flop=mkflop("5h6cJs"))) == evaluate_hand(
        mkhand("7c8h"), Board(flop=mkflop("5h6cJs"))
    )

    # Kickers all the way down matter
    assert evaluate_hand(mkhand("7d8s"), Board(flop=mkflop("AdAcJs"))) > evaluate_hand(
        mkhand("8s6h"), Board(flop=mkflop("AdAcJs"))
    )
