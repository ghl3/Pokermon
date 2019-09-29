from typing import Tuple

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


class Hand(Enum):
    HIGH = 1
    PAIR = 2
    TWO_PAIR = 3
    TRIPS = 4
    STRAGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    STRAIGHT_FLUSH = 8


Card = Tuple[Rank, Suit]


class HoleCards:
    def __init__(self, first: Card, second: Card):
        self.cards = (first, second)

    cards = Tuple[Card, Card]


Flop = Tuple[Card, Card, Card]

Turn = Card

River = Card


class Board:
    flop: Flop
