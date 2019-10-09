from typing import Optional, Tuple

from pokermon.ai.policy import Policy
from pokermon.poker import rules
from pokermon.poker.cards import HoleCards
from pokermon.poker.game import GameView, Action, Move
import re


class Human(Policy):
  _parser_call_fold = re.compile("\s*(call|fold)\s*")
  _parser_bet_raise = re.compile("\s*(bet|raise)\s+([0-9]+)\s*")
  
  def action(self, player_index: int, hand: HoleCards, game: GameView) -> Action:
    amount_to_call = game.amount_to_call()[player_index]
    
    stack_size = game.current_stack_sizes()[player_index]
    
    def parse_action(line: str):
      
      move, amount = self.parse_move(line)
      
      if move is None:
        return None
      elif move == Move.FOLD:
        return Action(player_index, Move.FOLD, 0)
      elif move == Move.CHECK_CALL:
        amount_able_to_call = min(amount_to_call, stack_size)
        return Action(player_index, Move.CHECK_CALL, amount_able_to_call)
      elif move == Move.BET_RAISE:
        amount_to_raise = min(amount, stack_size)
        return Action(player_index, Move.BET_RAISE, amount_to_raise)
      else:
        return None
    
    print("Amount to Call {} (Current Stack Size: {})".format(
      amount_to_call, stack_size))
    
    s = input('Action> ')
    
    maybe_action = parse_action(s)
    
    while maybe_action is None or not rules.action_valid(player_index, maybe_action, game):
      print("Action Invalid")
      s = input('Action >>')
      maybe_action = parse_action(s)
    
    return maybe_action
  
  def parse_move(self, line: str) -> Tuple[Optional[Move], Optional[int]]:
    
    # Attempt to parse call/fold
    groups = None
    
    groups = self._parser_call_fold.groups(line)
    if groups is not None:
      
      action = groups[0]
      
      if action == 'call':
        return Move.CHECK_CALL, None
      elif action == 'fold':
        return Move.FOLD, None
      else:
        raise Exception("Invaid action")
    
    groups = self._parser_bet_raise.groups(line)
    if groups is not None:
      action, amount = groups
      
      return Move.BET_RAISE, amount
    
    return None, None
