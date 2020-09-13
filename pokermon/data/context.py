# There is a single context per-hand.
# There are two types of contexts:
# - Public Context: The context anyone watching the game would know
# - Private Context: The context that requires knowing someone's hole cards
from dataclasses import dataclass
from typing import List

from pokermon.poker.cards import HoleCards
from pokermon.poker.game import GameView


@dataclass(frozen=True)
class PublicContext:
    num_players: int

    starting_stack_sizes: List[int]


@dataclass(frozen=True)
class PrivateContext:
    # Cards are ordered by:
    # Rank, [S, C, D, H]
    hole_card_0_rank: int
    hole_card_0_suit: int
    hole_card_1_rank: int
    hole_card_1_suit: int


def make_public_context(game: GameView) -> PublicContext:
    return PublicContext(
        num_players=game.num_players(), starting_stack_sizes=game.starting_stacks()
    )


def make_private_context(hole_cards: HoleCards):
    return PrivateContext(
        hole_card_0_rank=hole_cards[0].rank.value,
        hole_card_0_suit=hole_cards[0].suit.value,
        hole_card_1_rank=hole_cards[1].rank.value,
        hole_card_1_suit=hole_cards[1].suit.value,
    )
