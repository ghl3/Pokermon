from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering

import deuces
from pokermon.poker import deuces_wrapper
from pokermon.poker.cards import Board, HandType, HoleCards


@total_ordering
@dataclass
class EvaluationResult:
    hand_type: HandType
    rank: int
    percentage: float

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, EvaluationResult):
            raise Exception()
        return self.percentage < other.percentage

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EvaluationResult):
            raise Exception()
        return self.rank == other.rank


_EVALUATOR = deuces.Evaluator()


def evaluate_hand(hole_cards: HoleCards, board: Board) -> EvaluationResult:
    d_hand = deuces_wrapper.to_deuces_hand(hole_cards)
    d_board = deuces_wrapper.to_deuces_board(board)

    rank = _EVALUATOR.evaluate(d_hand, d_board)
    rank_class = _EVALUATOR.get_rank_class(rank)
    percentage = 1.0 - _EVALUATOR.get_five_card_rank_percentage(rank)

    hand_type = deuces_wrapper.from_deuces_hand_type(rank_class)

    return EvaluationResult(hand_type=hand_type, rank=rank, percentage=percentage)
