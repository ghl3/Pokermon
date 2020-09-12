from dataclasses import dataclass

from pokermon.data.utils import iter_actions
from pokermon.poker.game import GameView, Action, Move, BIG_BLIND_AMOUNT


# At timestamp i, this was the action made at i-1
@dataclass(frozen=True)
class LastAction:
    action_encoded: int
    amount_added: int
    amount_added_percent_of_remaining: int


# At timestamp i, the action that will be made
@dataclass(frozen=True)
class CurrentAction:
    action_encoded: int
    amount_added: int


def make_last_actions(game: GameView):

    # We need a dummy entry for the first voluntary action
    actions = [LastAction(action_encoded=-1,
                          amount_added=-1,
                          amount_added_percent_of_remaining=-1)]

    for i, a in list(iter_actions(game))[:-1]:

        game_view = game.view(i)

        stack_size = game_view.current_stack_sizes()[game_view.current_player()]

        actions.append(
            LastAction(
                action_encoded = a.move.value,
                amount_added=a.amount_added,
                amount_added_percent_of_remaining = 100 *a.amount_added // stack_size
            )
        )

    return actions


def make_current_actions(game: GameView):
    actions = []

    for i, a in iter_actions(game):
        actions.append(
            CurrentAction(
                action_encoded=a.move.value,
                amount_added=a.amount_added,
            )
        )

    return actions
