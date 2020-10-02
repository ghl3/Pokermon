from typing import Iterable, Tuple

import stringcase  # type: ignore

from pokermon.poker.cards import Card
from pokermon.poker.game import Action, GameView, Move, Street


def field_feature_name(clazz, field) -> str:
    return f"{stringcase.snakecase(clazz.__name__)}__{field.name}"


def card_order(card: Card) -> Tuple[int, int]:
    return 0 - card.rank.value, card.suit.value


def iter_game_states(game: GameView) -> Iterable[int]:
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

        yield i

    # If the game isn't over, we yield the current state.  We don't know the next action,
    # so we yield None for it
    if game.street() == Street.HAND_OVER:
        return
    else:
        yield game.timestamp
