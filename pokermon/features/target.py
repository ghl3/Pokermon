from dataclasses import dataclass
from typing import List

# Targets are values that are unknown until after the hand (but don't vary by action).
from pokermon.poker.deal import FullDeal
from pokermon.poker.result import Result


@dataclass(frozen=True)
class Target:
    # The total reward this player will earn throughout this hand
    total_rewards: List[int]

    # Each player's hole cards (or -1 if they're unknown), represented
    # as an integer, where the mapping is defined
    hole_cards: List[int]


def make_target(deal: FullDeal, result: Result) -> Target:
    return Target(
        total_rewards=result.profits,
        hole_cards=[hc.encoded for hc in deal.hole_cards],
    )
