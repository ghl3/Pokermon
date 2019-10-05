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
  STRAIGHT_FLUSH = 8


@dataclass(order=True)
class Hand:
  type: HandType
  kickers: Tuple[Rank, Rank, Rank, Rank, Rank]
  suit: Optional[Suit] = None


@dataclass(order=True)
class Card:
  rank: Rank
  suit: Suit


class HoleCards:
  def __init__(self, first: Card, second: Card):
    self.cards = (first, second)
  
  cards = Tuple[Card, Card]


class Board:
  """
  A board of cards, which may be partially or fully rolled out.
  """
  flop: Optional[Tuple[Card, Card, Card]]
  turn: Optional[Card]
  river: Optional[Card]


def get_hand(hole_cards: HoleCards, board: Board) -> Hand:
  return Hand(type=HandType.STRAIGHT, suit=None,
              kickers=(Rank.ACE, Rank.QUEEN, Rank.NINE, Rank.EIGHT, Rank.FOUR))


def get_winning_hands(board: Board, hole_cards: List[HoleCards]):
  if len(hole_cards) == 0:
    raise ValueError("No hole cards given")
  
  hands = [get_hand(hc, board) for hc in hole_cards]
  hands = sorted(hands)
  
  best_hand = hands[0]
  return [h for h in hands if h == best_hand]
