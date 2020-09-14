import zlib
from typing import Iterable, Tuple

import stringcase  # type: ignore

from pokermon.poker.cards import Card, HoleCards, sorted_hole_cards
from pokermon.poker.game import Action, GameView, Move, Street


def field_feature_name(clazz, field) -> str:
    return f"{stringcase.snakecase(clazz.__name__)}__{field.name}"


def card_order(card: Card) -> Tuple[int, int]:
    return 0 - card.rank.value, card.suit.value


def get_hole_cards_as_int(hole_cards: HoleCards):
    cards: HoleCards = sorted_hole_cards(hole_cards)

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


def iter_actions(game: GameView) -> Iterable[Tuple[int, Action]]:
    """
    Iterate over all non-voluntary actions
    """
    for i, e in list(enumerate(game.events())):

        # i is the index of this event
        # game.view(i) is the state of the game at this tme
        # e is the action that it taken at this time (the action is 'after' the state)

        # Only generate rows where there is an action
        if isinstance(e, Street):
            continue

        # We now know the event is an action
        a: Action = e

        # Since Small/Big blinds are forced actions, we don't generate
        # rows for them
        if a.move == Move.SMALL_BLIND or a.move == Move.BIG_BLIND:
            continue

        yield i, e
