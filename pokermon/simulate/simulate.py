import logging
from typing import List, Tuple, Optional
from pokermon.ai.policy import Policy
from pokermon.data.features import make_rows
from pokermon.poker.cards import FullDeal
from pokermon.poker.evaluation import Evaluator
from pokermon.poker.game import Game, Action, Move, Street, GameView
import itertools
import pokermon.poker.rules as rules
from pokermon.poker.rules import GameResults

from pokermon.poker.game import SMALL_BLIND_AMOUNT, BIG_BLIND_AMOUNT

logger = logging.getLogger(__name__)


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
  
  logger.debug("Simulating game with %s players", len(players))
  
  game = Game(starting_stacks=starting_stacks)
  
  action_index = 0
  
  # For now, only support players having the same starting stacks.
  # This avoids having to implement side pots.
  # TODO: Support Side Pots
  assert len(set(starting_stacks)) == 1
  
  logger.info("Hole Cards: %s", deal.hole_cards)
  
  for street in [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]:
    
    logger.debug("Starting Street: %s", street)
    
    game.set_street(street)
    
    if game.current_street() == Street.FLOP:
      logger.info("Flop: %s", deal.board.flop)
    elif game.current_street() == Street.TURN:
      logger.info("Turn: %s", deal.board.turn)
    elif game.current_street() == Street.RIVER:
      logger.info("River: %s", deal.board.river)
    
    for player_index, player in itertools.cycle(enumerate(players)):
      
      game_view = game.view()
      
      if rules.street_over(game_view):
        break
      
      if game_view.is_folded()[player_index]:
        logger.debug("Player %s is folded", player_index)
        continue
      
      if game_view.is_all_in()[player_index]:
        logger.debug("Player %s is all in", player_index)
        continue
      
      action = _get_action(action_index, player, player_index, game_view, deal)
      
      # Action is None if the player has already folded or gone all in.
      if action is None:
        raise Exception("Invalid Action")
      
      logger.debug("Action %s Player %s: %s", action_index, player_index, action)
      
      action_result = rules.action_valid(action_index=action_index, player_index=player_index,
                                         action=action, game=game_view)
      
      if not action_result.is_valid():
        logger.error("Action is invalid %s %s", action, action_result)
        raise Exception("Action is invalid", action, action_result)
      else:
        game.add_action(action)
        action_index += 1
  
  game.end_hand()
  
  evaluator = Evaluator()
  
  result = rules.get_result(deal, game.view(), evaluator)
  
  logger.info("Result: %s", result)
  
  for row in make_rows(game, deal, result, evaluator):
    print(row)
  
  return (game, result)


def _get_action(action_index: int, player: Policy, player_index: int, game_view: GameView,
                deal: FullDeal) -> Optional[Action]:
  # Post the small blind
  if action_index == 0:
    return Action(player_index, Move.SMALL_BLIND, amount_added=SMALL_BLIND_AMOUNT,
                  total_bet=SMALL_BLIND_AMOUNT)
  
  # Post the big blind
  if action_index == 1:
    return Action(player_index, Move.BIG_BLIND, amount_added=BIG_BLIND_AMOUNT,
                  total_bet=BIG_BLIND_AMOUNT)
  
  hand = deal.hole_cards[player_index]
  return player.action(player_index, hand, game_view)
