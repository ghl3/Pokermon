import csv
import importlib.resources as pkg_resources
import random
import zlib
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

from pokermon import data
from pokermon.poker import cards, hands
from pokermon.poker.board import Board
from pokermon.poker.cards import Card
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
    cards: List[Card] = list(hand.cards)
    for c in board.cards():
        cards.append(c)

    bytes = b""
    bytes += int_to_bytes(num_draws)
    for card in cards:
        bytes += int_to_bytes(card.rank.value) + int_to_bytes(card.suit.value)
    bytes += int_to_bytes(num_other_hands)

    return zlib.adler32(bytes)


@dataclass(frozen=True)
class OddsResult:
    frac_win: float
    frac_tie: float
    frac_lose: float


def _read_preflop_odds() -> Dict[str, OddsResult]:
    odds_csv = pkg_resources.read_text(data, "preflop_odds.csv")
    csv_lines = csv.reader(odds_csv.split("\n"), delimiter=",")
    hand_odds: Dict[str, OddsResult] = {}
    next(csv_lines)
    for row in csv_lines:
        if row:
            hand = row[0]
            odds_result = OddsResult(
                frac_win=float(row[1]), frac_tie=float(row[2]), frac_lose=float(row[3])
            )
            hand_odds[hand] = odds_result
    return hand_odds


def _make_hand_odds_vs_random():
    preflop_odds: Dict[str, OddsResult] = _read_preflop_odds()
    hand_odds: Dict[HoleCards, OddsResult] = {}
    for hand in hands.ALL_HANDS:
        hand_odds[hand] = preflop_odds[hand.reduced_form]
    return hand_odds


PREFLOP_ODDS_VS_RANDOM: Dict[HoleCards, OddsResult] = _make_hand_odds_vs_random()


def calculate_odds(
    hand: HoleCards,
    board: Optional[Board] = None,
    other_hands: Optional[List[HoleCards]] = None,
    num_hands_to_simulate=1000,
) -> OddsResult:

    # Use a lookup table for preflop odds vs random hand
    if board is None and not other_hands:
        return PREFLOP_ODDS_VS_RANDOM[hand]
    else:
        return simulate_odds(
            hand, board, other_hands, num_hands_to_simulate=num_hands_to_simulate
        )


def simulate_odds(
    hand: HoleCards,
    board: Optional[Board] = None,
    other_hands: Optional[List[HoleCards]] = None,
    num_hands_to_simulate=1000,
) -> OddsResult:
    """

    :type board: object
    """

    if board is None:
        board = Board()

    taken_cards = set()
    taken_cards.update(hand.cards)
    taken_cards.update(board.cards())

    if other_hands is None:
        other_hands = [
            h
            for h in hands.ALL_HANDS
            if h.cards[0] not in taken_cards and h.cards[1] not in taken_cards
        ]

    # Use a deterministic RNG to make testing easier
    rng = random.Random(make_seed(num_hands_to_simulate, hand, board, len(other_hands)))

    num_to_draw = 5 - len(board)

    num_wins = 0
    num_losses = 0
    num_ties = 0

    # Make odds deterministic
    for _ in range(num_hands_to_simulate):

        # Randomly select the opponent's hand
        other_hand = random.choice(other_hands)

        # Find the remaining cards in the deck
        remaining_cards = tuple(
            [
                c
                for c in cards.ALL_CARDS
                if c not in taken_cards and c not in other_hand.cards
            ]
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

    return OddsResult(
        frac_win=num_wins / num_hands_to_simulate,
        frac_tie=num_ties / num_hands_to_simulate,
        frac_lose=num_losses / num_hands_to_simulate,
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

    my_result = evaluate_hand(hole_cards, board)

    disallowed_cards = set()
    disallowed_cards.update(hole_cards.cards)
    disallowed_cards.update(board.cards())

    all_evals = [
        (hc, evaluate_hand(hc, board))
        for hc in hands.ALL_HANDS
        if hc.cards[0] not in disallowed_cards and hc.cards[1] not in disallowed_cards
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
class PartitionedOddsResult:
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
) -> PartitionedOddsResult:
    simulation_vs_better = simulate_odds(hand, board, partitioned_hands.better_hands)
    simulation_vs_worse = simulate_odds(hand, board, partitioned_hands.better_hands)

    # This is an approximation, but we don't want to spend too much effort on tied
    # hands since they're a bit of an edge case
    if len(partitioned_hands.tied_hands) > 0:
        simulation_vs_tied = simulate_odds(hand, board, partitioned_hands.better_hands)
    else:
        simulation_vs_tied = OddsResult(frac_win=0, frac_tie=1.0, frac_lose=0)

    return PartitionedOddsResult(
        odds_vs_better=simulation_vs_better.frac_win,
        odds_vs_tied=simulation_vs_tied.frac_win,
        odds_vs_worse=simulation_vs_worse.frac_win,
    )
