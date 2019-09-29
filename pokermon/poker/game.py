# All Amounts are relative to the small blind.
from typing import Optional, List, Union
from dataclasses import dataclass
from pokermon.poker.cards import Hand, Board

from pokermon.poker.ordered_enum import OrderedEnum


class Move(OrderedEnum):
  SMALL_BLIND = 1
  BIG_BLIND = 2
  FOLD = 3
  CHECK_CALL = 4
  BET_RAISE = 5


@dataclass
class Action:
  player_index: int
  starting_amount: int
  move: Move
  # The total amount of the bet/call/raise.  For a call, it's the additional
  # money called on this turn.  For a raise, it's the additional money raised
  # (the amount "on top") not the total bet for this street.
  amount: Optional[int]


@dataclass
class ObservedGame:
  """
  All data for a game that is fully known to all players.
  """
  
  # A list of starting player stacks
  stacks = List[int]
  
  board = Board
  
  preflop_action = List[Action]
  flop_action = List[Action]
  turn_action = List[Action]
  river_action = List[Action]
  
  def action(self):
    return (self.preflop_action
            + self.flop_action
            + self.turn_action
            + self.river_action)
  
  def street_action(self, timestamp: int = -1):
    """
    The list of action on the street containing the given action.
    :param timestamp:
    :return:
    """
    
    raise NotImplementedError()
  
  def stack_size(self, player_index: int, timestamp: int = -1):
    stack_size = self.stacks[player_index]
    for ts, a in enumerate(self.action()[:timestamp]):
      if a.player_index == player_index:
        stack_size -= a.amount
    return stack_size
  
  def amount_to_call(self, timestamp: int = -1):
    """
    The minimum amount needed to call by the player whose turn it is.
    :param timestamp:
    :return:
    """
    
    if len(self.action()) == 0:
      return 0
    else:
      last_action = self.action()[timestamp - 1]
      
      #if last_action in {}
  
  def min_raise_alowed(self, timestamp: int = None):


@dataclass
class GameResults:
  """
  """
  
  winning_player_index: int
  
  # The actual profits, in small blings, won or list by each player during this game
  profits = List[int]
  
  # A list of the actual player hands (or None if the hand is unknown)
  hands = List[Hand]
