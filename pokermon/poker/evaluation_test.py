import deuces
from pokermon.poker.cards import Board, HandType, mkcard, mkflop, mkhand
from pokermon.poker.evaluation import (
    EvaluationResult,
    NutResult,
    evaluate_hand,
    make_nut_result,
)


def test_deck() -> None:
    deck = deuces.Deck()
    board = deck.draw(5)
    deuces.Card.print_pretty_cards(board)


def test_royal() -> None:
    hole_cards = mkhand("AcKc")
    board = Board(flop=mkflop("TcJcQc"))

    eval_result = evaluate_hand(hole_cards, board)

    assert eval_result == EvaluationResult(
        hand_type=HandType.STRAIGHT_FLUSH, rank=1, percentage=0.9998659876708658
    )

    assert make_nut_result(hole_cards, board) == NutResult(
        num_better=0, num_tied=0, num_worse=1175
    )


def test_wheel() -> None:
    hole_cards = mkhand("2c7d")
    board = Board(flop=mkflop("3h4c5s"))

    eval_result = evaluate_hand(hole_cards, board)

    assert eval_result == EvaluationResult(
        hand_type=HandType.HIGH, rank=7462, percentage=0.0
    )

    assert make_nut_result(hole_cards, board) == NutResult(
        num_better=1160, num_tied=15, num_worse=0
    )


def test_winner() -> None:
    hole_cards = mkhand("AdAc")
    board = Board(flop=mkflop("AdKs3h"), turn=mkcard("5h"), river=mkcard("7s"))

    eval_result = evaluate_hand(hole_cards, board)

    assert eval_result == EvaluationResult(
        hand_type=HandType.TRIPS, rank=1615, percentage=0.7835700884481372
    )

    assert make_nut_result(hole_cards, board) == NutResult(
        num_better=32, num_tied=3, num_worse=1046
    )
