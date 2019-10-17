# All Amounts are relative to the small blind.
import random
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
BIG_BLIND_AMOUNT = 2


@dataclass(frozen=True)
class Action:
  player_index: int
  move: Move
  
  # The amount this player added to the pot as a part of this action.
  amount_added: int
  
  # The new total size of the bet after this action.
  total_bet: int


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
  
  # A unique id for this game
  id: int = field(default_factory=lambda: random.getrandbits(64))
  
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
    # TODO: Validate the player index
    self.get_street_action().append(action)
  
  def num_timestamps(self) -> int:
    return (len(self.preflop_action) + len(self.flop_action) + len(self.turn_action) + len(
      self.river_action))
  
  def view(self, timestamp: int = None):
    """
    Returns a view of the game AFTER the timestamp'th action.
    
    So, if timestamp == 0, then no actions have been done.
    If timestamp==2, then the view is AFTER the big blind is posted.
    The current view is timestamp=len(action) (in other words, length is one
    more than the last action index, which is therefore the current move).
    :param timestamp:
    :return:
    """
    
    if timestamp is None:
      timestamp = self.num_timestamps()
    
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


@dataclass(frozen=True)
class GameView:
  """
  A view of an observed game at a given timestamp.
  
  Contains methods to get useful information summarizing the state of the game.
  
  """
  game: Game
  
  # The timestamp is guaranteed to be in the range of the given game.
  timestamp: int
  
  def __hash__(self):
    return hash((self.game.id,
                 self.game.current_street,
                 self.timestamp,
                 "364258436582634"))
  
  @functools.lru_cache()
  def num_players(self) -> int:
    return len(self.game.stacks)
  
  @functools.lru_cache()
  def _player_list(self, starting_player: int = 0) -> List[int]:
    all_players_twice = list(range(self.num_players())) + list(range(self.num_players()))
    return all_players_twice[starting_player: starting_player + self.num_players()]
  
  @functools.lru_cache()
  def current_player(self) -> int:
    if len(self.street_action()) == 0:
      starting_player = 0
    else:
      starting_player = (self.street_action()[-1].player_index + 1) % self.num_players()
    
    for player in self._player_list(starting_player):
      if not self.is_folded()[player]:
        return player
  
  @functools.lru_cache()
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
      elif amount_remaining == len(street_actions):
        all_actions.extend(street_actions)
        return all_actions
      else:
        all_actions.extend(street_actions[:amount_remaining])
        return all_actions
    
    raise Exception("Action Error")
  
  @functools.lru_cache()
  def street_action(self) -> List[Action]:
    """
    The list of actions before the given timestamp  on the street containing the given action.
    :param timestamp:
    :return:
    """
    
    amount_remaining = self.timestamp
    
    # TODO: Street action is broken at the end of a steet.
    # Needs to consider the current street
    for street_actions in (self.game.preflop_action, self.game.flop_action,
                           self.game.turn_action, self.game.river_action):
      
      if amount_remaining > len(street_actions):
        amount_remaining -= len(street_actions)
      elif amount_remaining == len(street_actions):
        return street_actions
      else:
        return street_actions[:amount_remaining]
    
    raise Exception("Street Action Error")
  
  @functools.lru_cache()
  def amount_added_in_street(self) -> Dict[int, int]:
    """
    Return a dictionary of the total amount bet per player so far.
    :return:
    """
    
    amount = {i: 0 for i in range(self.num_players())}
    
    for action in self.street_action():
      player_id = action.player_index
      
      amount[player_id] += action.amount_added
    
    return amount
  
  @functools.lru_cache()
  def amount_added_total(self) -> Dict[int, int]:
    """
    Return a dictionary of the total amount bet per player so far.
    :return:
    """
    
    amount = {i: 0 for i in range(self.num_players())}
    
    for action in self.action():
      player_id = action.player_index
      
      amount[player_id] += action.amount_added
    
    return amount
  
  @functools.lru_cache()
  def current_stack_sizes(self) -> Dict[int, int]:
    return {i: self.game.stacks[i] - amount_bet
            for i, amount_bet in self.amount_added_total().items()}
  
  @functools.lru_cache()
  def current_bet_amount(self) -> int:
    return max(self.amount_added_in_street().values())
  
  @functools.lru_cache()
  def amount_to_call(self) -> Dict[int, int]:
    return {i: self.current_bet_amount() - amount_bet
            for i, amount_bet in self.amount_added_in_street().items()}
  
  @functools.lru_cache()
  def last_raise_amount(self) -> int:
    """
    The size of the last raise over the previous bet
    :return:
    """
    
    if len(self.street_action()) == 0:
      return 0
    
    current_bet = self.street_action()[-1].total_bet
    
    for action in reversed(self.street_action()):
      
      if action.total_bet != current_bet:
        return current_bet - action.total_bet
      
      # if action.move in {Move.SMALL_BLIND, Move.BIG_BLIND, Move.BET_RAISE}:
      #  return action.total_bet
    
    return current_bet
  
  @functools.lru_cache()
  def is_folded(self) -> Dict[int, bool]:
    
    folded = {player_index: False for player_index in range(self.num_players())}
    
    for a in self.action():
      if a.move == Move.FOLD:
        folded[a.player_index] = True
    
    return folded
  
  @functools.lru_cache()
  def is_all_in(self) -> Dict[int, bool]:
    return {player_index: current_stack_size == 0
            for player_index, current_stack_size in self.current_stack_sizes().items()}
  
  @functools.lru_cache()
  def small_blind(self):
    return Action(0, Move.SMALL_BLIND, total_bet=SMALL_BLIND_AMOUNT,
                  amount_added=SMALL_BLIND_AMOUNT)
  
  @functools.lru_cache()
  def big_blind(self):
    return Action(0, Move.BIG_BLIND, total_bet=BIG_BLIND_AMOUNT,
                  amount_added=BIG_BLIND_AMOUNT)
  
  @functools.lru_cache()
  def call(self) -> Action:
    player_index = self.current_player()
    
    amount_to_call = self.amount_to_call()[player_index]
    player_stack = self.current_stack_sizes()[player_index]
    # amount_already_addded = game.amount_added_in_street()[player_index]
    
    if amount_to_call < player_stack:
      return Action(player_index, Move.CHECK_CALL, amount_added=amount_to_call,
                    total_bet=self.current_bet_amount())
    else:
      return Action(player_index, Move.CHECK_CALL, amount_added=player_stack,
                    total_bet=self.current_bet_amount())
  
  @functools.lru_cache()
  def bet_raise(self, to: Optional[int] = None, raise_amount: Optional[int] = None) -> Optional[
    Action]:
    
    player_id = self.current_player()
    
    if to is not None and raise_amount is not None:
      raise Exception()
    
    elif to is not None:
      new_bet_size = to
      amount_to_add = to - self.amount_added_in_street()[player_id]
    
    elif raise_amount is not None:
      new_bet_size = self.current_bet_amount() + raise_amount
      amount_to_add = new_bet_size - self.amount_added_in_street()[player_id]
    
    else:
      raise Exception()
    
    # This may be an invalid raise, but this will be caught downstream
    return Action(player_id, Move.BET_RAISE, amount_to_add, new_bet_size)
  
  #    raise_amount = new_bet_size - self.current_bet_amount()
  
  # Player is all in
  #    if amount_to_add == self.current_stack_sizes()[player_id]:
  #      return Action(player_id, Move.BET_RAISE, amount_to_add, new_bet_size)
  
  #    elif amount_to_add > self.current_stack_sizes()[player_id]:
  #      return None
  
  # Must raise at least the minimum
  #    elif raise_amount < self.last_raise_amount():
  #      return None
  
  #    else:
  #      return Action(player_id, Move.BET_RAISE, amount_to_add, new_bet_size)
  
  @functools.lru_cache()
  def fold(self) -> Action:
    player_id = self.current_player()
    return Action(player_id, Move.FOLD, amount_added=0, total_bet=self.current_bet_amount())


#  @functools.lru_cache()
#  def all_in(self) -> Action:
#    return self.bet_raise(to=game.cur)
#    pass


@dataclass(frozen=True)
class GameResults:
  """
  """
  
  # If multiple players have the best hand (a tie), return a list of all player indices.
  best_hand_index: List[int]
  
  # The actual profits, in small blings, won or list by each player during this game
  profits: List[int]
