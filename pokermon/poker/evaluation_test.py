import deuces
import pokermon.poker.evaluation


def test_deck():
    deck = deuces.Deck()
    board = deck.draw(5)
    deuces.Card.print_pretty_cards(board)
