import itertools
from dataclasses import dataclass
from typing import Dict, Tuple

from pokermon.poker.cards import ALL_CARDS, INVERSE_RANK_MAP, Card, mkcards
from pokermon.poker.ordered_enum import OrderedEnum


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


@dataclass(frozen=True)
class HoleCards:
    cards: Tuple[Card, Card]

    reduced_form: str

    encoded: int

    def index(self):
        c1 = self.cards[1].index()
        c2 = self.cards[0].index()
        offset = 52 * c1 - c1 * (c1 + 1) // 2
        return offset + (c2 - c1 - 1)


def _order_cards(first: Card, second: Card) -> Tuple[Card, Card]:
    if first > second:
        return first, second
    else:
        return second, first


def _make_hole_cards(first: Card, second: Card) -> HoleCards:
    first, second = _order_cards(first, second)
    first_rank = INVERSE_RANK_MAP[first.rank]
    second_rank = INVERSE_RANK_MAP[second.rank]
    suited = first.suit == second.suit
    reduced_form = f"{first_rank}{second_rank}{'s' if suited else 'o'}"
    return HoleCards(
        (first, second),
        reduced_form=reduced_form,
        encoded=get_hole_cards_as_int((first, second)),
    )


def get_hole_cards_as_int(cards: Tuple[Card, Card]):
    suited = cards[0].suit == cards[1].suit
    paired = cards[0].rank == cards[1].rank

    # The first 13 indices are pairs
    if paired:
        return cards[0].rank.value - 2

    # If they're not paired, then the lowest hands are
    # 32s, 32o, 42s, 42o, 43s, 43o, ...

    # 32, 42, 43
    # The total length of the first rank is:
    # Let N = first_rank-2
    # total = 2*sum(i=1 to N, inclusive, of i)
    # So, the offset is

    # If the card is a 3, I want to start with 0
    # If the card is a 4, I want to start with N=1
    # If the card is a 5, I want to start with N=2
    # ...

    N = cards[0].rank.value - 1 - 2
    offset = 13 + 2 * ((N) * (N + 1) // 2)
    second_rank = cards[1].rank.value - 2
    # We then do all unpaired hands with suited/unsuited as the fastest dimension
    return offset + 2 * second_rank + (0 if suited else 1)


ALL_HANDS: Tuple[HoleCards, ...] = tuple(
    [
        _make_hole_cards(comb[0], comb[1])
        for comb in itertools.combinations(ALL_CARDS, 2)
    ]
)

_CARD_MAP: Dict[Card, Dict[Card, HoleCards]] = {}
for hand in ALL_HANDS:
    f, s = hand.cards
    if f not in _CARD_MAP:
        _CARD_MAP[f] = {}
    _CARD_MAP[f][s] = hand


def lookup_hole_cards(first: Card, second: Card) -> HoleCards:
    first, second = _order_cards(first, second)
    return _CARD_MAP[first][second]


def mkhand(s: str) -> HoleCards:
    cards = mkcards(s)
    assert len(cards) == 2
    return lookup_hole_cards(cards[0], cards[1])


# No more constructing HoleCards after this point
HoleCards.__init__ = None  # type: ignore
HoleCards.__new__ = None  # type: ignore
