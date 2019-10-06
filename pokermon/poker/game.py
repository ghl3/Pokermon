# All Amounts are relative to the small blind.
from typing import Optional, List, Dict, Set
from dataclasses import dataclass, field
from pokermon.poker.ordered_enum import OrderedEnum
import functools


class Street(OrderedEnum):
  PREFLOP = 1
  FLOP = 2
  TURN = 3
  RIVER = 4
  OVER = 5


class Move(OrderedEnum):
  SMALL_BLIND = 1
  BIG_BLIND = 2
  FOLD = 3
  CHECK_CALL = 4
  BET_RAISE = 5


SMALL_BLIND_AMOUNT = 1
BIG_BIND_AMOUNT = 2


@dataclass
class Action:
  player_index: int
  move: Move
  # The total amount of the bet/call/raise.  For a call, it's the additional
  # money called on this action.  For a raise, it's the additional money raised
  # (the amount "on top"), not the total bet for this street.
  amount: Optional[int]


@dataclass
class Game:
  """
  All data for a game that is fully known to all players.
  
  An observed game is a snapshot of a game at a given action (or possibly after
  all actions are complete and the hand is done).
  
  Each action in an observed game has a timestamp index (integer).  These
  integers cross streets (so, if the last action on the FLOP is N, then the
  first action on the TURN is N+1).
  """
  
  # A list of starting player stacks
  stacks: List[int]
  
  current_street: Street = Street.PREFLOP
  
  preflop_action: List[Action] = field(default_factory=list)
  flop_action: List[Action] = field(default_factory=list)
  turn_action: List[Action] = field(default_factory=list)
  river_action: List[Action] = field(default_factory=list)
  
  def num_players(self) -> int:
    return len(self.stacks)
  
  def get_street_action(self) -> List[Action]:
    if self.current_street == Street.PREFLOP:
      return self.preflop_action
    elif self.current_street == Street.FLOP:
      return self.flop_action
    elif self.current_street == Street.TURN:
      return self.turn_action
    elif self.current_street == Street.RIVER:
      return self.river_action
    else:
      raise Exception("Invalid current street.")
  
  def add_action(self, action: Action) -> None:
    self.get_street_action().append(action)
  
  def num_timestamps(self) -> int:
    return (len(self.preflop_action) + len(self.flop_action) + len(self.turn_action) + len(
      self.river_action))
  
  def view(self, timestamp: int = -1):
    if timestamp > self.num_timestamps():
      raise Exception("Timestamp out of range")
    else:
      return GameView(self, timestamp)


@dataclass
class SidePot:
  amount: int = 0
  players: Set[int] = field(default_factory=set)


@dataclass
class Pot:
  side_pots: List[SidePot]


@dataclass
class GameView:
  """
  A view of an observed game at a given timestamp.
  
  Contains methods to get useful information summarizing the state of the game.
  
  # TODO: Memoize all methods
  
  """
  game: Game
  
  # The timestamp is guaranteed to be in the range of the given game.
  timestamp: int
  
  @functools.lru_cache
  def num_players(self) -> int:
    return len(self.game.stacks)
  
  @functools.lru_cache
  def action(self) -> List[Action]:
    """
    The list of actions before the given timestamp  on the street containing the given action.
    :param timestamp:
    :return:
    """
    
    all_actions = []
    amount_remaining = self.timestamp
    
    for street_actions in (self.game.preflop_action, self.game.flop_action,
                           self.game.turn_action, self.game.river_action):
      
      if amount_remaining > len(street_actions):
        all_actions.extend(street_actions)
        amount_remaining -= len(street_actions)
      else:
        all_actions.extend(street_actions[:amount_remaining])
        return all_actions
    
    raise Exception("Action Error")
  
  @functools.lru_cache
  def street_action(self) -> List[Action]:
    """
    The list of actions before the given timestamp  on the street containing the given action.
    :param timestamp:
    :return:
    """
    
    amount_remaining = self.timestamp
    
    for street_actions in (self.game.preflop_action, self.game.flop_action,
                           self.game.turn_action, self.game.river_action):
      
      if amount_remaining > len(street_actions):
        amount_remaining -= len(street_actions)
      else:
        return street_actions[:amount_remaining]
    
    raise Exception("Street Action Error")
  
  @functools.lru_cache
  def amount_bet_in_street(self) -> Dict[int, int]:
    """
    Return a dictionary of the total amount bet per player so far.
    :return:
    """
    
    amount = {i: 0 for i in range(self.num_players())}
    
    for action in self.street_action():
      player_id = action.player_index
      
      amount[player_id] += action.amount
    
    return amount
  
  @functools.lru_cache
  def amount_bet_total(self) -> Dict[int, int]:
    """
    Return a dictionary of the total amount bet per player so far.
    :return:
    """
    
    amount = {i: 0 for i in range(self.num_players())}
    
    for action in self.action():
      player_id = action.player_index
      
      amount[player_id] += action.amount
    
    return amount
  
  @functools.lru_cache
  def current_stack_sizes(self) -> Dict[int, int]:
    return {i: self.game.stacks[i] - amount_bet
            for i, amount_bet in self.amount_bet_total()}
  
  @functools.lru_cache
  def current_bet_amount(self) -> int:
    return max(self.amount_bet_in_street().values())
  
  @functools.lru_cache
  def amount_to_call(self) -> Dict[int, int]:
    return {i: self.current_bet_amount() - amount_bet
            for i, amount_bet in self.amount_bet_in_street()}
  
  @functools.lru_cache
  def latest_bet_raise_amount(self) -> int:
    
    for action in reversed(self.street_action()):
      
      if action.move in {Move.SMALL_BLIND, Move.BIG_BLIND, Move.BET_RAISE}:
        return action.amount
    
    return 0
  
  @functools.lru_cache
  def is_folded(self) -> Dict[int, bool]:
    
    folded = {player_index: False for player_index in range(self.num_players())}
    
    for a in self.action():
      if a.move == Move.FOLD:
        folded[a.player_index] = True
    
    return folded
  
  @functools.lru_cache
  def is_all_in(self) -> Dict[int, bool]:
    return {player_index: current_stack_size == 0
            for player_index, current_stack_size in self.current_stack_sizes()}


@dataclass
class GameResults:
  """
  """
  
  # If multiple players have the best hand (a tie), return a list of all player indices.
  best_hand_index: List[int]
  
  # The actual profits, in small blings, won or list by each player during this game
  profits: List[int]
