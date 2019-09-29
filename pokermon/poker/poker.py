from typing import Tuple, Optional
from dataclasses import dataclass

from enum import Enum


class Suit(Enum):
    SPADES = 1
    CLUBS = 2
    DIAMONDS = 3
    HEARTS = 4


class Rank(Enum):
    ACE = 1
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


class HandType(Enum):
    HIGH = 1
    PAIR = 2
    TWO_PAIR = 3
    TRIPS = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    STRAIGHT_FLUSH = 8


@dataclass
class Hand:
    type: HandType
    suit: Optional[Suit]
    kickers: Optional[Tuple[Rank, Rank, Rank, Rank, Rank]]


Card = Tuple[Rank, Suit]


class HoleCards:
    def __init__(self, first: Card, second: Card):
        self.cards = (first, second)

    cards = Tuple[Card, Card]


class Board:
    flop: Tuple[Card, Card, Card]
    turn: Card
    river: Card


def get_hand(hole_cards: HoleCards, board: Board) -> Hand:
    return Hand(type=HandType.STRAIGHT, suit=None, kickers=(Rank.ACE, Rank.QUEEN, Rank.NINE, Rank.EIGHT, Rank.FOUR))
