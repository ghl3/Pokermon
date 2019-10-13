from pokermon.ai.policy import Policy
import random

from pokermon.poker.cards import HoleCards
from pokermon.poker.game import Action, Move, GameView

import pokermon.poker.rules as rules


class RandomPolicy(Policy):
  def action(self, player_index: int, _: HoleCards, game: GameView) -> Action:
    
    amount_to_call = game.amount_to_call()[player_index]
    remaining_stack = game.current_stack_sizes()[player_index]
    
    if amount_to_call > 0:
      
      move = random.choice([Move.FOLD, Move.CHECK_CALL, Move.BET_RAISE])
    
    else:
      move = random.choice([Move.CHECK_CALL, Move.BET_RAISE])
    
    if move == Move.FOLD:
      return game.fold()
    
    elif move == Move.CHECK_CALL:
      return game.call()
    
    elif move == Move.BET_RAISE:
      
      max_amount = remaining_stack
      
      min_amount = max((game.current_bet_amount() + rules.min_bet_amount(game) -
                       game.amount_added_in_street()[player_index], 0))
      
      # min_amoun_to_add =
      
      raise_amount = random.randint(min_amount,
                                    max_amount)
      return game.bet_raise(
        raise_amount=raise_amount)  # Action(player_index, Move.BET_RAISE, raise_amount)
    
    else:
      raise Exception()
