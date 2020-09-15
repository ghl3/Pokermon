from dataclasses import dataclass

# Features that describe the status of a single player
# Terminology:
# player: The selected player
# current_player: The player whose turn it is
from typing import List

from pokermon.data.utils import iter_actions
from pokermon.poker.game import GameView


@dataclass(frozen=True)
class PlayerData:
    player_index: int

    is_current_player: bool

    # The player has an offset of 0.  Players who are positioned before the player
    # have a negative offset, players positioned after the player have a positive
    # offset.
    current_player_offset: int


def make_player_data(player_index: int, game: GameView) -> List[PlayerData]:
    player_data = []

    for i, a in iter_actions(game):
        game_view = game.view(i)

        player_data.append(
            PlayerData(
                player_index=player_index,
                is_current_player=(game_view.current_player() == player_index),
                current_player_offset=(game_view.current_player() - player_index)
            )
        )

    return player_data
