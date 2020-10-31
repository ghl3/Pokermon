# Features that describe the status of a single player
# Terminology:
# player: The selected player
# current_player: The player whose turn it is
from dataclasses import dataclass
from typing import Dict, List, Optional

import pyholdthem
from pokermon.features.utils import iter_game_states
from pokermon.poker.board import Board
from pokermon.poker.evaluation import evaluate_hand
from pokermon.poker.game import GameView, Street
from pokermon.poker.hands import HoleCards


@dataclass(frozen=True)
class PlayerState:

    is_current_player: bool

    # The player has an offset of 0.  Players who are positioned before the player
    # have a negative offset, players positioned after the player have a positive
    # offset.
    current_player_offset: int

    current_hand_type: Optional[int] = None

    frac_better_hands: Optional[float] = None
    frac_tied_hands: Optional[float] = None
    frac_worse_hands: Optional[float] = None

    win_odds: Optional[float] = None
    tie_odds: Optional[float] = None
    lose_odds: Optional[float] = None

    win_odds_vs_better: Optional[float] = None
    tie_odds_vs_better: Optional[float] = None
    lose_odds_vs_better: Optional[float] = None

    win_odds_vs_tied: Optional[float] = None
    tie_odds_vs_tied: Optional[float] = None
    lose_odds_vs_tied: Optional[float] = None

    win_odds_vs_worse: Optional[float] = None
    tie_odds_vs_worse: Optional[float] = None
    lose_odds_vs_worse: Optional[float] = None


def make_player_states(
    player_index: int, game: GameView, hole_cards: HoleCards, board: Board
) -> List[PlayerState]:

    player_states = []
    street_cache: Dict[Street, PlayerState] = {}

    for i in iter_game_states(game):
        game_view = game.view(i)

        is_player_turn = game_view.current_player() == player_index

        # We don't set the rest of the values for non-current-players
        if not is_player_turn:
            player_states.append(
                PlayerState(
                    is_current_player=False,
                    current_player_offset=(game_view.current_player() - player_index),
                )
            )
            continue

        street = game_view.street()

        # These values don't vary by street, so we cache them
        if street in street_cache:
            player_states.append(street_cache[street])
            continue

        if game_view.street() == Street.PREFLOP:
            player_state = PlayerState(is_current_player=True, current_player_offset=0)

        else:
            current_board = board.at_street(game_view.street())
            hand_eval = evaluate_hand(hole_cards, current_board)
            hand_features = pyholdthem.make_hand_features_from_indices(
                hole_cards.index(), [c.index() for c in current_board.cards()], 1000
            )

            player_state = PlayerState(
                is_current_player=True,
                current_player_offset=0,
                current_hand_type=hand_eval.hand_type.value,
                frac_better_hands=hand_features.frac_better_hands,
                frac_tied_hands=hand_features.frac_tied_hands,
                frac_worse_hands=hand_features.frac_worse_hands,
                win_odds=hand_features.win_odds,
                tie_odds=hand_features.tie_odds,
                lose_odds=hand_features.lose_odds,
                win_odds_vs_better=hand_features.win_odds_vs_better,
                tie_odds_vs_better=hand_features.tie_odds_vs_better,
                lose_odds_vs_better=hand_features.lose_odds_vs_better,
                win_odds_vs_tied=hand_features.win_odds_vs_tied,
                tie_odds_vs_tied=hand_features.tie_odds_vs_tied,
                lose_odds_vs_tied=hand_features.lose_odds_vs_tied,
                win_odds_vs_worse=hand_features.win_odds_vs_worse,
                tie_odds_vs_worse=hand_features.tie_odds_vs_worse,
                lose_odds_vs_worse=hand_features.lose_odds_vs_worse,
            )

        street_cache[street] = player_state
        player_states.append(player_state)

    return player_states
