from typing import List, Tuple
from pokermon.ai.policy import Policy
from pokermon.poker.cards import FullDeal
from pokermon.poker.game import Game, GameResults, Action, Move, Street, Pot, SidePot
import itertools
import pokermon.poker.rules as rules

from pokermon.poker.game import SMALL_BLIND_AMOUNT, BIG_BIND_AMOUNT


def simulate(players: List[Policy],
             starting_stacks: List[int],
             deal: FullDeal) -> Tuple[Game, GameResults]:
  """
  Players are ordered by Small Blind, Big Blind, ..., Button
  :param players:
  :param starting_stacks:
  :param deal:
  :return:
  """
  
  game = Game(stacks=starting_stacks)
  
  action_index = 0
  
  # For now, only support players having the same starting stacks.
  # This avoids having to implement side pots.
  # TODO: Support Side Pots
  assert len(set(starting_stacks)) == 1
  
  pot = Pot([SidePot(0, set(range(game.num_players())))])
  
  for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
    game.current_street = street
    
    for player_index, player in itertools.repeat(enumerate(players)):
      
      game_view = game.view()
      
      # Post the small blind
      if action_index == 0:
        game.add_action(Action(0, Move.SMALL_BLIND, SMALL_BLIND_AMOUNT))
        continue
      
      # Post the big blind
      if action_index == 1:
        game.add_action(Action(1, Move.BIG_BLIND, BIG_BIND_AMOUNT))
        continue
      
      if game_view.is_folded()[player_index]:
        continue
      
      if game_view.is_al_in()[player_index]:
        continue
      
      hand = deal.hole_cards[player_index]
      
      action = player.action(player_index, hand, game_view)
      
      # Update the pot BEFORE applying the action
      rules.update_pot(pot, game_view, action)
      
      if not rules.action_valid(player_index, action, game_view):
        raise Exception("Action is invalid")
      else:
        game.add_action(action)
      
      if rules.street_over(game_view):
        break
  
  result = rules.get_result(deal, game.view(), pot)
  
  return (game, result)
