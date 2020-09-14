import random
import zlib
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from pokermon.poker import cards
from pokermon.poker.cards import Board, Card, HoleCards, Rank, Suit
from pokermon.poker.evaluation import evaluate_hand


class HeadToHeadResult(Enum):
    WIN = 1
    TIE = 2
    LOSS = 3


def is_winner(hand: HoleCards, other_hand: HoleCards, board: Board) -> HeadToHeadResult:
    hero_hand = evaluate_hand(hand, board)
    villian_hand = evaluate_hand(other_hand, board)

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


def int_to_bytes(i: int, *, signed: bool = False) -> bytes:
    length = ((i + ((i * signed) < 0)).bit_length() + 7 + signed) // 8
    return i.to_bytes(length, byteorder="big", signed=signed)


def make_seed(
    num_draws,
    hand: HoleCards,
    board: Board = None,
    other_hand: Optional[HoleCards] = None,
) -> int:
    cards: List[Card] = list(hand)
    if board:
        for c in board.cards():
            cards.append(c)
    if other_hand:
        cards.extend(list(other_hand))

    bytes = b""
    bytes += int_to_bytes(num_draws)
    for card in cards:
        bytes += int_to_bytes(card.rank.value) + int_to_bytes(card.suit.value)

    return zlib.adler32(bytes)


def odds_vs_random_hand(
    hand: HoleCards,
    board: Optional[Board] = None,
    other_hand: Optional[HoleCards] = None,
    num_draws=1000,
    rng=None,
):
    """

    :type board: object
    """

    if board is None:
        board = Board(flop=None, turn=None, river=None)

    if rng is None:
        rng = random.Random(make_seed(num_draws, hand, board, other_hand))

    remaining_cards = tuple(
        [
            c
            for c in cards.ALL_CARDS
            if c not in hand
               and c not in board.cards()
               and (other_hand is None or c not in other_hand)
        ]
    )

    board_cards_to_draw = 5 - len(board)
    opponent_hand_to_draw = 0 if other_hand else 2
    num_to_draw = board_cards_to_draw + opponent_hand_to_draw

    num_wins = 0
    num_losses = 0
    num_ties = 0

    # Make odds deterministic
    for _ in range(num_draws):
        drawn_cards: Tuple[Card, ...] = tuple(rng.sample(remaining_cards, num_to_draw))
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
