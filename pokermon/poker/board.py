from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from pokermon.poker.cards import Card, mkcards, sorted_cards
from pokermon.poker.ordered_enum import OrderedEnum


class Street(OrderedEnum):
    PREFLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    HAND_OVER = 5


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
