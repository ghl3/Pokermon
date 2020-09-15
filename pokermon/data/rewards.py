from dataclasses import dataclass
from typing import List

from pokermon.data.utils import iter_game_states
from pokermon.poker.game import Action, GameView, Street
from pokermon.poker.rules import GameResults


@dataclass(frozen=True)
class Reward:
    # Is this the last move the player makes in the hand
    is_players_last_action: bool

    # The amount earned immediately (before this player's next decision) as a result of this
    # # move.  Will be negative if the player bets on this turn and it isn't their last turn.
    # May be negative or positive if it's their last turn (depending on whether they bet and
    # whether they win).
    instant_reward: int

    # The net amount the player earns or loses for the rest of the hand, including
    # the result of the current action (a bet/raise).  Ignores any previous gains/losses.
    cumulative_reward: int

    # Did the current player eventually win the hand?
    won_hand: bool


def make_rewards(game: GameView, result: GameResults):
    """
    Generate a list of rewards for every non-voluntary action
    """

    # This only makes sense at the end of the game
    assert game.street() == Street.OVER

    rewards = []

    # Profits between now and the end of the hand
    cumulative_rewards: List[int] = result.earned_at_showdown

    is_last_action: List[bool] = [True for _ in range(game.num_players())]

    # Iterate in reverse order
    for i in reversed(list(iter_game_states(game))):

        a: Action = game._game.events[i]

        won_hand = a.player_index in set(result.best_hand_index)

        # Subtract the amount lost after taking the given action, which is a part
        # of the future cumulative winnings / losses
        # print(cumulative_rewards, a.player_index, a.amount_added)
        cumulative_rewards[a.player_index] -= a.amount_added

        if is_last_action[a.player_index]:
            instant_reward = cumulative_rewards[a.player_index]
        else:
            instant_reward = -1 * a.amount_added

        rewards.append(
            Reward(
                is_players_last_action=is_last_action[a.player_index],
                cumulative_reward=cumulative_rewards[a.player_index],
                instant_reward=instant_reward,
                won_hand=won_hand,
            )
        )

        is_last_action[a.player_index] = False

    return list(reversed(rewards))
