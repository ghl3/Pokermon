from dataclasses import dataclass

import deuces
from pokermon.poker import deuces_wrapper
from pokermon.poker.cards import Card, Suit, Rank, HoleCards, Board, HandType


# import deuces
#
# DeucesCard = int
#
# _SUIT_TO_DEUCES_INT = {Suit.SPADES: 1,
#                        Suit.HEARTS: 2,
#                        Suit.DIAMONDS: 4,
#                        Suit.CLUBS: 8}
#
# _DEUCES_INT_TO_SUIT = {v: k for k, v in _SUIT_TO_DEUCES_INT.items()}
#
#
# def _to_decues_rank_suit_tuple(card: Card) -> DeucesCard:
#   rank_int = card.rank.value() - 2
#   suit_int = _SUIT_TO_DEUCES_INT[card.suit]
#   return deuces.card.Card.from_rank_int_and_suit_int(rank_int, suit_int)
#
#
#
#
#
# def _from_deuces_card(deuces_card: DeucesCard) -> Card:
#   rank_int = deuces.Card.get_rank_int(deuces_card)
#   suit_int = deuces.Card.get_suit_int(deuces_card)
#   rank = Rank(rank_int + 2)
#   suit = _DEUCES_INT_TO_SUIT[suit_int]
#   return Card(rank=rank, suit=suit)
#

@dataclass
class EvaluationResult:
  hand_type: HandType
  rank: int
  percentage: float


class Evaluator:
  
  def __init__(self):
    self._deuces_evaluator = deuces.Evaluator()
  
  def evaluate(self, hole_cards: HoleCards, board: Board) -> EvaluationResult:
    d_hand = deuces_wrapper.to_deuces_hand(hole_cards)
    d_board = deuces_wrapper.to_deuces_board(board)
    
    rank = self._deuces_evaluator.evaluate(d_hand, d_board)
    rank_class = self._deuces_evaluator.get_rank_class(rank)
    percentage = 1.0 - self._deuces_evaluator.get_five_card_rank_percentage(rank)
    
    hand_type = deuces_wrapper.from_deuces_hand_type(rank_class)
    
    return EvaluationResult(
      hand_type=hand_type,
      rank=rank,
      percentage=percentage)
