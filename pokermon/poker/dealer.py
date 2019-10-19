from pokermon.poker.cards import FullDeal, HoleCards, Board
import deuces
import pokermon.poker.deuces_wrapper as wrapper


def deal_cards(num_players: int) -> FullDeal:
  deck = deuces.deck.Deck()
  board = deck.draw(5)
  
  hole_cards = []
  
  for player_index in range(num_players):
    hole_cards.append(deck.draw(2))
  
  flop = (wrapper.from_deuces_card(board[0]),
          wrapper.from_deuces_card(board[1]),
          wrapper.from_deuces_card(board[2]))
  turn = wrapper.from_deuces_card(board[3])
  river = wrapper.from_deuces_card(board[4])
  
  return FullDeal(
    hole_cards=[(wrapper.from_deuces_card(x),
                 wrapper.from_deuces_card(y)) for x, y in hole_cards],
    board=Board(flop=flop, turn=turn, river=river))
