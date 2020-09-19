# Features that describe the status of a single player
# Terminology:
# player: The selected player
# current_player: The player whose turn it is
from dataclasses import dataclass
from typing import List, Optional

from pokermon.data.utils import iter_game_states
from pokermon.poker.cards import Board, HoleCards
from pokermon.poker.evaluation import evaluate_hand, make_nut_result
from pokermon.poker.game import GameView, Street
from pokermon.poker.odds import odds_vs_random_hand


@dataclass(frozen=True)
class PlayerState:
    is_current_player: bool

    # The player has an offset of 0.  Players who are positioned before the player
    # have a negative offset, players positioned after the player have a positive
    # offset.
    current_player_offset: int

    current_hand_type: Optional[int] = None
    current_hand_strength: Optional[float] = None
    current_hand_rank: Optional[int] = None

    num_hands_better: Optional[int] = None
    num_hands_tied: Optional[int] = None
    num_hands_worse: Optional[int] = None

    win_prob_vs_random: Optional[float] = None


def make_player_states(
    player_index: int, game: GameView, hole_cards: HoleCards, board: Board
) -> List[PlayerState]:

    player_states = []
    street_cache = {}

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
            # These odds are deterministic if we don't pass an explicit rng#
            win_odds = odds_vs_random_hand(hole_cards, current_board, num_draws=1000)

            nut_result = make_nut_result(hole_cards, current_board)

            player_state = PlayerState(
                is_current_player=True,
                current_player_offset=0,
                current_hand_type=hand_eval.hand_type.value,
                current_hand_strength=hand_eval.percentage,
                current_hand_rank=hand_eval.rank,
                win_prob_vs_random=win_odds.win_rate(),
                num_hands_better=nut_result.num_better,
                num_hands_tied=nut_result.num_tied,
                num_hands_worse=nut_result.num_worse,
            )

        street_cache[street] = player_state
        player_states.append(player_state)

    return player_states
