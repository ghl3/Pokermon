from pokermon.ai.policy import Policy

import random

from pokermon.poker.game import Move


def RandomPolicy(Policy):
  def action(self, player_index, hand, game):
    current_stack_size = game.stack_size(player_index)
    
    move = random.choice([Move.FOLD, Move.CHECK_CALL, Move.BET_RAISE])
    
    if move == Move.BET_RAISE:
      
      amount =
