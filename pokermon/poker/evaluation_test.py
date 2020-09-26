import deuces
from pokermon.poker.board import Board, mkflop
from pokermon.poker.cards import mkcard
from pokermon.poker.evaluation import EvaluationResult, evaluate_hand
from pokermon.poker.hands import HandType, mkhand


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


def test_wheel() -> None:
    hole_cards = mkhand("2c7d")
    board = Board(flop=mkflop("3h4c5s"))

    eval_result = evaluate_hand(hole_cards, board)

    assert eval_result == EvaluationResult(
        hand_type=HandType.HIGH, rank=7462, percentage=0.0
    )


def test_winner() -> None:
    hole_cards = mkhand("AdAc")
    board = Board(flop=mkflop("AdKs3h"), turn=mkcard("5h"), river=mkcard("7s"))

    eval_result = evaluate_hand(hole_cards, board)

    assert eval_result == EvaluationResult(
        hand_type=HandType.TRIPS, rank=1615, percentage=0.7835700884481372
    )


def test_turn() -> None:
    hole_cards = mkhand("7d8s")
    board = Board(flop=mkflop("5h6cJs"), turn=mkcard("5h"))

    eval_result = evaluate_hand(hole_cards, board)

    assert eval_result == EvaluationResult(
        hand_type=HandType.PAIR, rank=5455, percentage=0.2689627445725007
    )
