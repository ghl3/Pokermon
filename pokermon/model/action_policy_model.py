
import numpy as np

from pokermon.model.utils import make_action, select_proportionally
from pokermon.poker.cards import HoleCards, Board
from pokermon.poker.game import GameView, Action
from abc import ABCMeta, abstractmethod


class ActionPolicyModel(metaclass=ABCMeta):
    def __init__(self, player_id, num_bet_bins=20):
        self.player_id = player_id
        self.num_bet_bins = num_bet_bins

    def next_action(self, game: GameView, hole_cards: HoleCards, board: Board) -> Action:
        """
        Select the next action to take.  This can be a stocastic choice.
        """
        assert game.current_player() == self.player_id
        board = board.at_street(game.street())
        policy: np.Array = self.generate_policy(game, hole_cards, board)
        action_index = select_proportionally(policy)
        return make_action(action_index=action_index, game=game, num_bet_bins=self.num_bet_bins)

    @abstractmethod
    def generate_policy(self, game: GameView, hole_cards: HoleCards, board: Board) -> np.array:
        pass
