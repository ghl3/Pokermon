import random
import zlib
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

from pokermon.poker import cards, hands
from pokermon.poker.board import Board
from pokermon.poker.cards import Card
from pokermon.poker import cards
from pokermon.poker.evaluation import evaluate_hand
from pokermon.poker.hands import HoleCards


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


def int_to_bytes(i: int, *, signed: bool = False) -> bytes:
    length = ((i + ((i * signed) < 0)).bit_length() + 7 + signed) // 8
    return i.to_bytes(length, byteorder="big", signed=signed)


def make_seed(num_draws, hand: HoleCards, board: Board, num_other_hands: int) -> int:
    cards: List[Card] = list(hand)
    for c in board.cards():
        cards.append(c)

    bytes = b""
    bytes += int_to_bytes(num_draws)
    for card in cards:
        bytes += int_to_bytes(card.rank.value) + int_to_bytes(card.suit.value)
    bytes += int_to_bytes(num_other_hands)

    return zlib.adler32(bytes)


@dataclass(frozen=True)
class SimulationResult:
    frac_win: float
    frac_tie: float
    frac_lose: float


#    def num_simulations(self):
#        return self.num_ties + self.num_wins + self.num_losses

#    def win_rate(self) -> float:
#        return self.num_wins / self.num_simulations()

PREFLOP_ODDS: Dict[HoleCards, SimulationResult] = {}


def simulate_odds(
    hand: HoleCards,
    board: Board,
    other_hands: List[HoleCards],
    num_hands=1000,
    rng=None,
) -> SimulationResult:
    """

    :type board: object
    """

    if board is None:
        return PREFLOP_ODDS[hand]

    if rng is None:
        rng = random.Random(make_seed(num_hands, hand, board, len(other_hands)))

    taken_cards = set()
    taken_cards.update(board.cards())
    taken_cards.update(hand)
    # for other_hand in other_hands:
    #    taken_cards.update(other_hand)

    #    remaining_cards = tuple(
    #        [c for c in cards.ALL_CARDS if c not in taken_cards]
    #    )

    num_to_draw = 5 - len(board)
    # opponent_hand_to_draw = 0 if other_hand else 2
    # num_to_draw = board_cards_to_draw + opponent_hand_to_draw

    num_wins = 0
    num_losses = 0
    num_ties = 0

    # Make odds deterministic
    for _ in range(num_hands):

        # Randomly select the opponent's hand
        other_hand = random.choice(other_hands)

        # Find the remaining cards in the deck
        remaining_cards = tuple(
            [c for c in cards.ALL_CARDS if c not in taken_cards and c not in other_hand]
        )

        # Randomly run out the rest of the board
        drawn_cards: Tuple[Card, ...] = tuple(rng.sample(remaining_cards, num_to_draw))
        simulated_board: Board = board + tuple(drawn_cards[:num_to_draw])

        # And pick the winner
        result: HeadToHeadResult = is_winner(
            hand,
            other_hand
            if other_hand
            else hands.lookup_hole_cards(drawn_cards[-2], drawn_cards[-1]),
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
        frac_win=num_wins / num_hands,
        frac_tie=num_ties / num_hands,
        frac_lose=num_losses / num_hands,
    )


@dataclass(frozen=True)
class NutResult:
    better_hands: List[HoleCards]
    tied_hands: List[HoleCards]
    worse_hands: List[HoleCards]

    def num_hands(self):
        return len(self.worse_hands) + len(self.tied_hands) + len(self.worse_hands)

    def frac_better(self):
        return len(self.worse_hands) / self.num_hands()

    def frac_tied(self):
        return len(self.tied_hands) / self.num_hands()

    def frac_worse(self):
        return len(self.worse_hands) / self.num_hands()


def make_nut_result(hole_cards: HoleCards, board: Board):
    hole_cards = sorted_hole_cards(hole_cards)

    my_result = evaluate_hand(hole_cards, board)

    all_evals = [
        (hc, evaluate_hand(hc, board))
        for hc in ALL_HANDS
        if hc != hole_cards
        and hc[0] not in board.cards()
        and hc[1] not in board.cards()
    ]

    better_hands: List[HoleCards] = []
    tied_hands: List[HoleCards] = []
    worse_hands: List[HoleCards] = []

    for hand, result in all_evals:
        if result.rank < my_result.rank:
            better_hands.append(hand)
        elif result.rank == my_result.rank:
            tied_hands.append(hand)
        else:
            worse_hands.append(hand)

    return NutResult(
        better_hands=better_hands, tied_hands=tied_hands, worse_hands=worse_hands
    )


@dataclass(frozen=True)
class OddsResult:
    odds_vs_better: float
    odds_vs_tied: float
    odds_vs_worse: float

    def odds_vs_any(self, nut_result: NutResult) -> float:
        return (
            self.odds_vs_better * nut_result.frac_better()
            + self.odds_vs_worse * nut_result.frac_worse()
            + self.odds_vs_tied * nut_result.frac_tied()
        )


def make_odds_result(
    hand: HoleCards, board: Board, partitioned_hands: NutResult
) -> OddsResult:
    simulation_vs_better = simulate_odds(hand, board, partitioned_hands.better_hands)
    simulation_vs_worse = simulate_odds(hand, board, partitioned_hands.better_hands)

    # This is an approximation, but we don't want to spend too much effort on tied
    # hands since they're a bit of an edge case
    if len(partitioned_hands.tied_hands) > 0:
        simulation_vs_tied = simulate_odds(hand, board, partitioned_hands.better_hands)
    else:
        simulation_vs_tied = SimulationResult(frac_win=0, frac_tie=1.0, frac_lose=0)

    return OddsResult(
        odds_vs_better=simulation_vs_better.frac_win,
        odds_vs_tied=simulation_vs_tied.frac_win,
        odds_vs_worse=simulation_vs_worse.frac_win,
    )
