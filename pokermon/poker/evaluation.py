from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering

from pokermon.poker.board import Board
from pokermon.poker.hands import HandType, HoleCards
import pyholdthem


@total_ordering
@dataclass
class EvaluationResult:

    # Higher is better
    hand_type: HandType

    # Higher is better
    kicker: int

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, EvaluationResult):
            raise Exception()
        return (self.hand_type.value, self.kicker) < (
            other.hand_type.value,
            other.kicker,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EvaluationResult):
            raise Exception()
        return (self.hand_type.value, self.kicker) == (
            other.hand_type.value,
            other.kicker,
        )


def evaluate_hand(hole_cards: HoleCards, board: Board) -> EvaluationResult:
    (hand, kicker) = pyholdthem.evaluate_hand_from_indices(
        hole_cards.index(), [c.index() for c in board.cards()]
    )

    return EvaluationResult(hand_type=HandType(hand), kicker=kicker)
