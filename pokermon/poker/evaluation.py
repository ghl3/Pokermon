from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering

import deuces
from pokermon.poker import deuces_wrapper
from pokermon.poker.cards import (
    ALL_HANDS,
    Board,
    HandType,
    HoleCards,
    sorted_hole_cards,
)


@total_ordering
@dataclass
class EvaluationResult:
    hand_type: HandType

    # Lower is better
    rank: int

    # Higher is better
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


@dataclass(frozen=True)
class NutResult:
    num_better: int
    num_tied: int
    num_worse: int

    def rank(self):
        return 1 + self.num_better


def make_nut_result(hole_cards: HoleCards, board: Board) -> NutResult:
    """
    1 = The current nuts
    2 = The current second nuts
    ..
    1326 = The worst hand possible
    """
    hole_cards = sorted_hole_cards(hole_cards)

    my_result = evaluate_hand(hole_cards, board)

    all_evals = [
        (hc, evaluate_hand(hc, board))
        for hc in ALL_HANDS
        if hc[0] not in board.cards() and hc[1] not in board.cards()
    ]

    num_better = 0
    num_tied = 0
    num_worse = 0

    for hand, result in all_evals:
        if hand == hole_cards:
            continue
        elif result.rank < my_result.rank:
            num_better += 1
        elif result.rank == my_result.rank:
            num_tied += 1
        else:
            num_worse += 1

    return NutResult(num_better=num_better, num_tied=num_tied, num_worse=num_worse)
