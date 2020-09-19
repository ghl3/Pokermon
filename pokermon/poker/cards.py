from __future__ import annotations

import dataclasses
import functools
import itertools
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import regex as regex  # type: ignore

from pokermon.poker.game import Street
from pokermon.poker.ordered_enum import OrderedEnum


class Suit(OrderedEnum):
    SPADES = 1
    CLUBS = 2
    DIAMONDS = 3
    HEARTS = 4


class Rank(OrderedEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class HandType(OrderedEnum):
    HIGH = 1
    PAIR = 2
    TWO_PAIR = 3
    TRIPS = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    QUADS = 8
    STRAIGHT_FLUSH = 9


@dataclass(order=True, frozen=True)
class Card:
    rank: Rank
    suit: Suit


RANK_SUIT_MAP: Dict[Rank, Dict[Suit, Card]] = {}

for rank in Rank:
    if rank not in RANK_SUIT_MAP:
        RANK_SUIT_MAP[rank] = {}
    for suit in Suit:
        card = Card(rank=rank, suit=suit)
        RANK_SUIT_MAP[rank][suit] = card

ALL_CARDS = tuple([c for r, d in RANK_SUIT_MAP.items() for c in d.values()])

RANK_MAP = {
    "A": Rank.ACE,
    "K": Rank.KING,
    "Q": Rank.QUEEN,
    "J": Rank.JACK,
    "10": Rank.TEN,
    "T": Rank.TEN,
    "9": Rank.NINE,
    "8": Rank.EIGHT,
    "7": Rank.SEVEN,
    "6": Rank.SIX,
    "5": Rank.FIVE,
    "4": Rank.FOUR,
    "3": Rank.THREE,
    "2": Rank.TWO,
}

SUIT_MAP = {"S": Suit.SPADES, "C": Suit.CLUBS, "D": Suit.DIAMONDS, "H": Suit.HEARTS}

_card_regex = regex.compile("^(([AKQJT]|10|[2-9])([SHCD]))+$")

HoleCards = Tuple[Card, Card]


def make_hole_cards(first: Card, second: Card) -> HoleCards:
    if first > second:
        return first, second
    else:
        return second, first


def sorted_cards(cards: Tuple[Card, ...]) -> Tuple[Card, ...]:
    return tuple(sorted(cards, reverse=True))


def sorted_hole_cards(hole_cards: HoleCards) -> HoleCards:
    if hole_cards[0] > hole_cards[1]:
        return hole_cards[0], hole_cards[1]
    else:
        return hole_cards[1], hole_cards[0]


@functools.lru_cache(104)
def mkcards(s: str) -> List[Card]:
    s = s.upper()

    match = _card_regex.match(s)

    if not match:
        raise Exception("Invaid Cards")

    cards = []

    for rank_code, suit_code in zip(match.captures(2), match.captures(3)):
        cards.append(RANK_SUIT_MAP[RANK_MAP[rank_code]][SUIT_MAP[suit_code]])
    return cards


def mkcard(s: str) -> Card:
    cards = mkcards(s)
    assert len(cards) == 1
    return cards[0]


def mkhand(s: str) -> HoleCards:
    cards = mkcards(s)
    assert len(cards) == 2
    return sorted_hole_cards(cards)


def mkflop(s: str) -> Tuple[Card, Card, Card]:
    cards = mkcards(s)
    assert len(cards) == 3
    return sorted_cards((cards[0], cards[1], cards[2]))


def mkboard(s: str) -> Board:
    cards = mkcards(s)
    assert 3 <= len(cards) <= 5
    return Board(
        flop=sorted_cards((cards[0], cards[1], cards[2])),
        turn=cards[3] if len(cards) > 3 else None,
        river=cards[4] if len(cards) > 4 else None,
    )


ALL_HANDS: Tuple[HoleCards, ...] = tuple(
    [make_hole_cards(comb[0], comb[1]) for comb in itertools.combinations(ALL_CARDS, 2)]
)


@dataclass(frozen=True)
class Board:
    """
    A board of cards, which may be partially or fully rolled out.
    """

    flop: Optional[Tuple[Card, Card, Card]] = None
    turn: Optional[Card] = None
    river: Optional[Card] = None

    def at_street(self, street: Street):

        board = self

        if street < Street.RIVER:
            board = dataclasses.replace(board, river=None)

        if street < Street.TURN:
            board = dataclasses.replace(board, turn=None)

        if street < Street.FLOP:
            board = dataclasses.replace(board, flop=None)

        return board

    def cards(self) -> Tuple[Card, ...]:
        if self.flop and self.turn and self.river:
            return self.flop + (self.turn,) + (self.river,)
        elif self.flop and self.turn:
            return self.flop + (self.turn,)
        elif self.flop:
            return self.flop
        else:
            return tuple()

    def __len__(self):
        if self.flop is None:
            return 0
        elif self.turn is None:
            return 3
        elif self.river is None:
            return 4
        else:
            return 5

    def __add__(self, cards: Sequence[Card]) -> Board:

        if len(cards) + len(self) > 5:
            raise Exception("Too many cards")

        rcards: List[Card] = list(reversed(cards))

        return Board(
            flop=(
                self.flop if self.flop else (rcards.pop(), rcards.pop(), rcards.pop())
            ),
            turn=(self.turn if self.turn else rcards.pop()),
            river=(self.river if self.river else rcards.pop()),
        )


@dataclass(frozen=True)
class FullDeal:
    hole_cards: List[HoleCards]
    board: Board
