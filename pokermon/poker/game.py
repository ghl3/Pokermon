# All Amounts are relative to the small blind.
import random
from collections import defaultdict
import functools
from typing import Optional, List, Dict, Union, Iterable
from dataclasses import dataclass, field
from pokermon.poker.ordered_enum import OrderedEnum


"""
An important concept in a game is the timestamp.  A timestamp connects two ideas:
- An index into events
- An index for the state of the game BEFORE the ith action was made

So, game.view(0) is the state of the game before any action, and action[0] is
the very first action.  Similarly, game.view(i) is the state of the game when
a player is contemplating what will become the ith action.
"""


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


# A street, as an event, represents the dealing of that street.
Event = Union[Action, Street]


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
  starting_stacks: List[int]
  
  events: List[Event] = field(default_factory=list)
  
  # A unique id for this game
  id: int = field(default_factory=lambda: random.getrandbits(64))
  
  def num_players(self) -> int:
    return len(self.starting_stacks)
  
  def set_street(self, street: Street):
    self.events.append(street)
  
  def current_street(self) -> Street:
    for e in reversed(self.events):
      if isinstance(e, Street):
        return e
    return Street.PREFLOP
  
  def end_hand(self):
    self.set_street(Street.OVER)
  
  def all_action(self) -> List[Action]:
    return [e for e in self.events if isinstance(e, Action)]
  
  def add_action(self, action: Action) -> None:
    self.events.append(action)
  
  def timestamp(self) -> int:
    return len(self.events)
  
  def view(self, timestamp: int = None):
    """Return a view of the game at the given timestamp.
    
    The meaning of a timestamp is defined as follows:
    - At the ith timestamp, i moves have been made
    - At the ith timestamp, a user is deciding the move with index=i (0 indexed)
    
    A timestamp represents different states of the game
    Returns a view of the game AFTER the timestamp'th action.  Or, equivalantly,
    returns a view of the game when the 0-indexed action is being decided.
    
    So, if timestamp == 0, then no actions have been done.
    If timestamp==2, then the view is AFTER the big blind is posted.
    The current view is timestamp=len(action) (in other words, length is one
    more than the last action index, which is therefore the current move).
    :param timestamp:
    :return:
    """
    
    if timestamp is None:
      timestamp = self.timestamp()
    
    if timestamp > self.timestamp():
      raise Exception("Timestamp out of range")
    else:
      return GameView(self, timestamp)


@dataclass(frozen=True)
class GameView:
  """
  A view of an observed game at a given timestamp.
  
  Contains methods to get useful information summarizing the state of the game.
  
  """
  _game: Game
  
  # The timestamp is guaranteed to be in the range of the given game.
  timestamp: int
  
  def __hash__(self):
    return hash((self._game.id,
                 self.timestamp,
                 "364258436582634"))
  
  @functools.lru_cache()
  def num_players(self) -> int:
    return self._game.num_players()
  
  @functools.lru_cache()
  def events(self) -> Iterable[Event]:
    return self._game.events[:self.timestamp]
  
  @functools.lru_cache()
  def starting_stacks(self) -> List[int]:
    return self._game.starting_stacks
  
  # Nothing below these methods should reference the underlying game
  
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
  def street(self):
    
    current_street = Street.PREFLOP
    
    for event in self.events():
      
      if isinstance(event, Street):
        current_street = event
    
    return current_street
  
  @functools.lru_cache()
  def street_action_dict(self):
    
    street_actions = defaultdict(lambda: [])
    
    current_street = Street.PREFLOP
    
    for e in self.events():
      
      if isinstance(e, Action):
        street_actions[current_street].append(e)
      
      elif isinstance(e, Street):
        current_street = e
    
    return street_actions
  
  @functools.lru_cache()
  def street_action(self):
    return self.street_action_dict()[self.street()]
  
  @functools.lru_cache()
  def current_street_index(self):
    return len(self.street_action())
  
  @functools.lru_cache()
  def action(self) -> List[Action]:
    """
    The list of actions before the given timestamp  on the street containing the given action.
    :param timestamp:
    :return:
    """
    
    return [e for e in self.events() if isinstance(e, Action)]
  
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
    return {i: self.starting_stacks()[i] - amount_bet
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
  
  @functools.lru_cache()
  def fold(self) -> Action:
    player_id = self.current_player()
    return Action(player_id, Move.FOLD, amount_added=0, total_bet=self.current_bet_amount())

