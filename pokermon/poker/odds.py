import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from pokermon.poker.cards import Board, Card, HoleCards, Rank, Suit
from pokermon.poker.evaluation import evaluate

ALL_CARDS: Tuple[Card, ...] = tuple(
    [Card(rank=rank, suit=suit) for rank in Rank for suit in Suit]
)


class HeadToHeadResult(Enum):
    WIN = 1
    TIE = 2
    LOSS = 3


def is_winner(hand: HoleCards, other_hand: HoleCards, board: Board) -> HeadToHeadResult:
    hero_hand = evaluate(hand, board)
    villian_hand = evaluate(other_hand, board)

    if hero_hand > villian_hand:
        return HeadToHeadResult.WIN
    elif hero_hand < villian_hand:
        return HeadToHeadResult.LOSS
    else:
        return HeadToHeadResult.TIE


@dataclass
class SimulationResult:
    num_wins: int
    num_losses: int
    num_ties: int

    def num_simulations(self):
        return self.num_ties + self.num_wins + self.num_losses

    def win_rate(self) -> float:
        return self.num_wins / self.num_simulations()


def odds_vs_random_hand(
    hand: HoleCards,
    board: Board = None,
    other_hand: Optional[HoleCards] = None,
    num_draws=1000,
):
    """

    :type board: object
    """

    if board is None:
        board = Board(flop=None, turn=None, river=None)

    remaining_cards = tuple(
        [c for c in ALL_CARDS if c not in hand and c not in board.cards()]
    )

    board_cards_to_draw = 5 - len(board)
    opponent_hand_to_draw = 0 if other_hand else 2
    num_to_draw = board_cards_to_draw + opponent_hand_to_draw

    num_wins = 0
    num_losses = 0
    num_ties = 0

    for _ in range(num_draws):
        drawn_cards: Tuple[Card, ...] = tuple(
            random.sample(remaining_cards, num_to_draw)
        )
        simulated_board: Board = board + tuple(drawn_cards[:board_cards_to_draw])
        result: HeadToHeadResult = is_winner(
            hand,
            other_hand if other_hand else (drawn_cards[-2], drawn_cards[-1]),
            simulated_board,
        )
        if result == HeadToHeadResult.WIN:
            num_wins += 1
        elif result == HeadToHeadResult.TIE:
            num_ties += 1
        elif result == HeadToHeadResult.LOSS:
            num_losses += 1
        else:
            raise Exception()

    return SimulationResult(
        num_wins=num_wins,
        num_losses=num_losses,
        num_ties=num_ties,
    )
