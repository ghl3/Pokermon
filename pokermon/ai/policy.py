from abc import ABC, abstractmethod

from pokermon.poker.board import Board
from pokermon.poker.game import Action, GameView
from pokermon.poker.hands import HoleCards


class Policy(ABC):
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError("Policy is purely abstract")

    @abstractmethod
    def select_action(
        self, player_index: int, game: GameView, hand: HoleCards, board: Board
    ) -> Action:
        """
        Given the state of a game, return a

        :param player_index: The index of the player whose turn it is
        :param hand: The hand of the player whose turn it is
        :param game: All observed action up-to the current turn.  This is the state of the game so far.
        :return:
        """
        raise NotImplementedError("Policy is purely abstract")
