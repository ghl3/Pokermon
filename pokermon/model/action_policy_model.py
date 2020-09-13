
import numpy as np
import tensorflow as tf

from pokermon.data.action import make_action_from_encoded, NUM_ACTION_BET_BINS
from pokermon.model.utils import select_proportionally
from pokermon.poker.cards import HoleCards, Board
from pokermon.poker.game import GameView, Action
from abc import ABCMeta, abstractmethod


def policy_vector_size():
    return NUM_ACTION_BET_BINS + 2


class ActionPolicyModel(metaclass=ABCMeta):
    def __init__(self, player_id):
        self.player_id = player_id

    @abstractmethod
    def action_probs(self, game: GameView, hole_cards: HoleCards, board: Board) -> tf.Tensor:
        pass

    def select_next_action(self, game: GameView, hole_cards: HoleCards, board: Board) -> Action:
        """
        Select the next action to take.  This can be a stocastic choice.
        """
        assert game.current_player() == self.player_id
        board = board.at_street(game.street())
        action_probs: np.Array = self.action_probs(game, hole_cards, board)
        action_index = select_proportionally(action_probs)
        return make_action_from_encoded(action_index=action_index, game=game)
