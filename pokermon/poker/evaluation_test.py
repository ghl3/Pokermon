import deuces
import pokermon.poker.evaluation

deck = deuces.Deck()
board = deck.draw(5)

deuces.Card.print_pretty_cards(board)
print([pokermon.poker.evaluation._from_deuces_card(b) for b in board])
