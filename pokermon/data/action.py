from dataclasses import dataclass

from pokermon.data.utils import iter_actions
from pokermon.poker.game import GameView


@dataclass(frozen=True)
class Action:
    action_index: int
    action_encoded: int
    amount_added: int


def make_actions(game: GameView):
    actions = []

    for i, a in iter_actions(game):
        actions.append(
            Action(
                action_index=i,
                action_encoded=a.move.value,
                amount_added=a.amount_added,
            )
        )

    return actions
