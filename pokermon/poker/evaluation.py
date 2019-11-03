from dataclasses import dataclass

import deuces
from pokermon.poker import deuces_wrapper
from pokermon.poker.cards import Board, HandType, HoleCards


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

        return EvaluationResult(hand_type=hand_type, rank=rank, percentage=percentage)
