import deuces
from pokermon.poker.cards import Board, HandType, mkcard, mkflop, mkhand
from pokermon.poker.evaluation import evaluate_hand


def test_deck() -> None:
    deck = deuces.Deck()
    board = deck.draw(5)
    deuces.Card.print_pretty_cards(board)


def test_winner() -> None:
    hole_cards = mkhand("AdAc")
    board = Board(flop=mkflop("AdKs3h"), turn=mkcard("5h"), river=mkcard("7s"))

    eval_result = evaluate_hand(hole_cards, board)

    assert eval_result.hand_type == HandType.TRIPS
    assert eval_result.percentage > 0.70
