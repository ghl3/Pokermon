from typing import Tuple, Optional, List
from dataclasses import dataclass

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


@dataclass(order=True)
class Card:
  rank: Rank
  suit: Suit


@dataclass
class HoleCards:
  left: Card
  right: Card


@dataclass
class Board:
  """
  A board of cards, which may be partially or fully rolled out.
  """
  flop: Optional[Tuple[Card, Card, Card]]
  turn: Optional[Card]
  river: Optional[Card]


@dataclass
class FullDeal:
  hole_cards: List[HoleCards]
  board: Board
