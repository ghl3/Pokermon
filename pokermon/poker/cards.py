import dataclasses
from typing import Tuple, Optional, List
from dataclasses import dataclass

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


card_map = {
    "A": Rank.ACE,
    "K": Rank.KING,
    "Q": Rank.QUEEN,
    "J": Rank.JACK,
    "10": Rank.TEN,
    "9": Rank.NINE,
    "8": Rank.EIGHT,
    "7": Rank.SEVEN,
    "6": Rank.SIX,
    "5": Rank.FIVE,
    "4": Rank.FOUR,
    "3": Rank.THREE,
    "2": Rank.TWO,
}

suit_map = {"S": Suit.SPADES, "C": Suit.CLUBS, "D": Suit.DIAMONDS, "H": Suit.HEARTS}

_card_regex = regex.compile("^(([AKQJ]|10|[2-9])([SHCD]))+$")


def mkcards(s: str) -> List[Card]:
    s = s.upper()

    match = _card_regex.match(s)

    if not match:
        raise Exception("Invaid Cards")

    cards = []

    for rank, suit in zip(match.captures(2), match.captures(3)):
        cards.append(Card(rank=card_map[rank], suit=suit_map[suit]))
    return cards


def mkcard(s: str) -> Card:
    cards = mkcards(s)
    assert len(cards) == 1
    return cards[0]


def mkhand(s: str) -> Tuple[Card, Card]:
    cards = mkcards(s)
    assert len(cards) == 2
    return (cards[0], cards[1])


def mkflop(s: str) -> Tuple[Card, Card, Card]:
    cards = mkcards(s)
    assert len(cards) == 3
    return (cards[0], cards[1], cards[2])


HoleCards = Tuple[Card, Card]


@dataclass(frozen=True)
class Board:
    """
  A board of cards, which may be partially or fully rolled out.
  """

    flop: Optional[Tuple[Card, Card, Card]]
    turn: Optional[Card]
    river: Optional[Card]

    def at_street(self, street: Street):

        board = self

        if street < Street.RIVER:
            board = dataclasses.replace(board, river=None)

        if street < Street.TURN:
            board = dataclasses.replace(board, turn=None)

        if street < Street.FLOP:
            board = dataclasses.replace(board, flop=None)

        return board


@dataclass(frozen=True)
class FullDeal:
    hole_cards: List[HoleCards]
    board: Board
