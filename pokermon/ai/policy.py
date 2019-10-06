from abc import ABC, abstractmethod
from pokermon.poker.cards import Hand
from pokermon.poker.game import GameView, Action


class Policy(ABC):
  
  @abstractmethod
  def action(self, player_index: int, hand: Hand, game: GameView) -> Action:
    """
    Given the state of a game, return a

    :param player_index: The index of the player whose turn it is
    :param hand: The hand of the player whose turn it is
    :param game: All observed action up-to the current turn.  This is the state of the game so far.
    :return:
    """
    raise NotImplementedError("Policy is purely abstract")

