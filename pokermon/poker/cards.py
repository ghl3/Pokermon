from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Dict, List, Tuple

import regex as regex  # type: ignore

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

INVERSE_RANK_MAP = {
    Rank.ACE: "A",
    Rank.KING: "K",
    Rank.QUEEN: "Q",
    Rank.JACK: "J",
    Rank.TEN: "T",
    Rank.NINE: "9",
    Rank.EIGHT: "8",
    Rank.SEVEN: "7",
    Rank.SIX: "6",
    Rank.FIVE: "5",
    Rank.FOUR: "4",
    Rank.THREE: "3",
    Rank.TWO: "2",
}


SUIT_MAP = {"S": Suit.SPADES, "C": Suit.CLUBS, "D": Suit.DIAMONDS, "H": Suit.HEARTS}

_card_regex = regex.compile("^(([AKQJT]|10|[2-9])([SHCD]))+$")


def sorted_cards(cards: Tuple[Card, ...]) -> Tuple[Card, ...]:
    return tuple(sorted(cards, reverse=True))


def mkcard(s: str) -> Card:
    cards = mkcards(s)
    assert len(cards) == 1
    return cards[0]


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
