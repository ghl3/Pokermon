from dataclasses import dataclass
from typing import List

# Targets are values that are unknown until after the hand (but don't vary by action).
from pokermon.data.utils import get_hole_cards_as_int
from pokermon.poker.cards import FullDeal
from pokermon.poker.rules import GameResults


@dataclass(frozen=True)
class Target:
    # The total reward this player will earn throughout this hand
    total_rewards: List[int]

    # Each player's hole cards (or -1 if they're unknown), represented
    # as an integer, where the mapping is defined
    hole_cards: List[int]


def make_target(deal: FullDeal, result: GameResults) -> Target:
    return Target(
        total_rewards=result.profits,
        hole_cards=[get_hole_cards_as_int(hc) for hc in deal.hole_cards],
    )
