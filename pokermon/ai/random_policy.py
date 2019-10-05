from pokermon.ai.policy import Policy
import random
from pokermon.poker.cards import Hand

from pokermon.poker.game import Action, Move, ObservedGameView


class RandomPolicy(Policy):
  def action(self, player_index: int, _: Hand, game: ObservedGameView) -> Action:
    
    amount_to_call = game.amount_to_call()[player_index]
    remaining_stack = game.current_stack_sizes()[player_index]
    
    if amount_to_call > 0:
      
      move = random.choice([Move.FOLD, Move.CHECK_CALL, Move.BET_RAISE])
      
      if move == Move.FOLD:
        return Action(player_index, Move.FOLD, 0)
      
      elif move == Move.CHECK_CALL:
        return Action(player_index, Move.CHECK_CALL, amount_to_call)
      
      elif move == Move.BET_RAISE:
        raise_amount = random.randint(game.min_bet_raise_amount(),
                                      remaining_stack)
        return Action(player_index, Move.BET_RAISE, raise_amount)
      
      else:
        raise Exception()
    
    else:
      
      move = random.choice([Move.CHECK_CALL, Move.BET_RAISE])
      
      if move == Move.CHECK_CALL:
        return Action(player_index, Move.CHECK_CALL, amount_to_call)
      
      elif move == Move.BET_RAISE:
        raise_amount = random.randint(game.min_bet_raise_amount(),
                                      remaining_stack)
        return Action(player_index, Move.BET_RAISE, raise_amount)
      
      else:
        raise Exception()
