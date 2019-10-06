from pokermon.poker.cards import Card, Suit, Rank, HoleCards, Board, Hand

# This is the only place where we import deuces from pokermon
import deuces

DeucesCard = int

_SUIT_TO_DEUCES_INT = {Suit.SPADES: 1,
                       Suit.HEARTS: 2,
                       Suit.DIAMONDS: 4,
                       Suit.CLUBS: 8}

_DEUCES_INT_TO_SUIT = {v: k for k, v in _SUIT_TO_DEUCES_INT.items()}


def _to_decues_rank_suit_tuple(card: Card) -> DeucesCard:
  rank_int = card.rank.value() - 2
  suit_int = _SUIT_TO_DEUCES_INT[card.suit]
  return deuces.card.Card.from_rank_int_and_suit_int(rank_int, suit_int)


def _from_deuces_card(deuces_card: DeucesCard) -> Card:
  rank_int = deuces.Card.get_rank_int(deuces_card)
  suit_int = deuces.Card.get_suit_int(deuces_card)
  rank = Rank(rank_int + 2)
  suit = _DEUCES_INT_TO_SUIT[suit_int]
  return Card(rank=rank, suit=suit)


class Evaluator:
  
  def __init__(self):
    self._deuces_evaluator = deuces.Evaluator()
  
  def evaluate(self, hole_cards: HoleCards, board: Board) -> Hand:
    pass
