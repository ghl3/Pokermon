import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional

from pokermon.poker.evaluation import Evaluator, EvaluationResult
from pokermon.poker.game import GameView, GameResults, Action, Move, Pot, SMALL_BLIND_AMOUNT
from pokermon.poker.game import BIG_BLIND_AMOUNT
from pokermon.poker.cards import FullDeal

logger = logging.getLogger(__name__)


class Error(Enum):
  UNKNOWN_MOVE = 1
  SMALL_BLIND_REQUIRED = 2
  BIG_BLIND_REQUIRED = 3
  INVALID_AMOUNT_ADDED = 4
  INVAID_TOTAL_BET = 5
  INVALID_PLAYER = 6
  MIN_RAISE_REQUIRED = 7


class Metadata(Enum):
  TYPE = 1
  BLIND_AMOUNT = 2
  AMOUNT_ADDED_SHOULD_BE_GE = 3
  AMOUNT_ADDED_SHOULD_BE_LE = 4
  TOTAL_BET_SHOULD_BE = 5
  MIN_BE_RAISE_AMOUNT = 6
  RAISE_MUST_BE_GE = 7


@dataclass
class Result:
  error: Optional[Error]
  
  metadata: Dict[Metadata, Any]
  
  def is_valid(self):
    return self.error is not None


MOVE_OK = Result(None, {})


def min_bet_amount(game: GameView) -> int:
  return max(BIG_BLIND_AMOUNT, game.last_raise_amount())


def action_valid(action_index: int, player_index: int, action: Action,
                 game: GameView) -> Result:
  amount_to_call = game.amount_to_call()[player_index]
  player_stack = game.current_stack_sizes()[player_index]
  amount_already_addded = game.amount_added_in_street()[player_index]
  
  if action_index == 0:
    if action.move != Move.SMALL_BLIND:
      return Result(Error.SMALL_BLIND_REQUIRED, {Metadata.BLIND_AMOUNT: SMALL_BLIND_AMOUNT})
    if action.amount_added != SMALL_BLIND_AMOUNT:
      return Result(Error.INVALID_AMOUNT_ADDED, {Metadata.BLIND_AMOUNT: SMALL_BLIND_AMOUNT})
    if action.total_bet != SMALL_BLIND_AMOUNT:
      return Result(Error.INVAID_TOTAL_BET, {Metadata.BLIND_AMOUNT: SMALL_BLIND_AMOUNT})
    return MOVE_OK
    # return action.move == Move.SMALL_BLIND and action.amount_added == SMALL_BLIND_AMOUNT and action.total_bet == SMALL_BLIND_AMOUNT
  
  elif action_index == 1:
    if action.move != Move.BIG_BLIND:
      return Result(Error.BIG_BLIND_REQUIRED, {Metadata.BLIND_AMOUNT: BIG_BLIND_AMOUNT})
    if action.amount_added != BIG_BLIND_AMOUNT:
      return Result(Error.INVALID_AMOUNT_ADDED, {Metadata.BLIND_AMOUNT: BIG_BLIND_AMOUNT})
    if action.total_bet != BIG_BLIND_AMOUNT:
      return Result(Error.INVAID_TOTAL_BET, {Metadata.BLIND_AMOUNT: BIG_BLIND_AMOUNT})
    return MOVE_OK
  
  elif action.move == Move.FOLD:
    if action.amount_added != 0:
      return Result(Error.INVALID_AMOUNT_ADDED, {Metadata.AMOUNT_ADDED_SHOULD_BE: 0})
    if action.total_bet != game.current_bet_amount():
      return Result(Error.INVALID_AMOUNT_ADDED,
                    {Metadata.TOTAL_AMOUNT_SHOULD_BE: game.current_bet_amount()})
    return MOVE_OK
  
  # Blinds handled elsewhere
  #  elif action.move in {Move.SMALL_BLIND, Move.BIG_BLIND}:
  #    return False
  
  elif action.move == Move.CHECK_CALL:
    
    if amount_to_call <= player_stack:
      
      if action.amount_added != amount_to_call:
        return Result(Error.INVALID_AMOUNT_ADDED, {Metadata.AMOUNT_ADDED_SHOULD_BE: amount_to_call})
      
      if action.total_bet != game.current_bet_amount():
        return Result(Error.INVAID_TOTAL_BET,
                      {Metadata.TOTAL_BET_SHOULD_BE: game.current_bet_amount()})
      
      return MOVE_OK
      
      # return action.amount_added == amount_to_call and action.total_bet == game.current_bet_amount()
    
    else:
      # Player calls all in
      
      if action.amount_added != player_stack:
        return Result(Error.INVALID_AMOUNT_ADDED, {Metadata.AMOUNT_ADDED_SHOULD_BE: player_stack})
      
      if action.total_bet != game.current_bet_amount():
        return Result(Error.INVAID_TOTAL_BET,
                      {Metadata.TOTAL_BET_SHOULD_BE: game.current_bet_amount()})
      
      return MOVE_OK
      
      # return action.amount_added == player_stack and action.total_bet == game.current_bet_amount()
  
  elif action.move == Move.BET_RAISE:
    
    #    if action.amount_added == 0:
    
    #      return Result(Error.INVALID_AMOUNT_ADDED, {Metadata.AMOUNT_ADDED_SHOULD_BE: player_stack})
    #      return False
    
    if action.amount_added > player_stack:
      return Result(Error.INVALID_AMOUNT_ADDED, {Metadata.AMOUNT_ADDED_SHOULD_BE_LE: player_stack})
    
    # Player goes all in.  You can always call all in.
    if action.amount_added == player_stack:
      # TODO: Check the total bet size here is consistent
      
      required_total_bet = player_stack + amount_already_addded
      
      if action.total_bet != required_total_bet:
        return Result(Error.INVAID_TOTAL_BET, {Metadata.TOTAL_BET_SHOULD_BE: required_total_bet})
      
      return MOVE_OK
    
    else:
      
      # Must bet at least the big blind OR must raise at least as much as the
      # last bet/raise
      min_bet_amount = max(BIG_BLIND_AMOUNT, game.last_raise_amount())
      
      # Player must raise at least as much as the previous raise.
      if action.total_bet - game.current_bet_amount() < min_bet_amount:
        return Result(Error.MIN_RAISE_REQUIRED, {Metadata.RAISE_MUST_BE_GE: min_bet_amount})
  
  return Result(Error.UNKNOWN_MOVE, {})


def street_over(game: GameView) -> bool:
  len(game.street_action())
  game.num_players()
  game.amount_to_call().values()
  
  return (len(game.street_action()) >= game.num_players() and sum(
    game.amount_to_call().values()) == 0)


def get_winning_players(hands: Dict[int, EvaluationResult]) -> List[int]:
  winning_rank = [res.rank for _, res in hands.items()]
  return [player_idx for player_idx, h in hands if h.rank == winning_rank]


def update_pot(pot: Pot, game: GameView, action: Action) -> None:
  # If a Player folds, remove them from all pots
  if action.move == Move.FOLD:
    for side_pot in pot.side_pots:
      side_pot.players.remove(action.player_index)
  
  # If a Player bets or calls, add that amount to the pot
  # TODO: Handle side pots
  pot.side_pots[0].amount += action.amount_added


# def update_pots(game: GameView, pot: Pot, action: Action) -> None:
#   """
#   Returns an updated list of pots based on the most recent action.
#
#   The game represents the state of the game BEFORE the action is applied.
#
#   """
#
#   player_index = action.player_index
#
#   # If a Player folds, remove them from all pots
#   if action.move == Move.FOLD:
#     for side_pot in pot.side_pots:
#       side_pot.players.remove(action.player_index)
#
#
#   # If a player calls less than the bet, a side pot of their amount is created:
#   if action.move == Move.CHECK_CALL and action.amount < game.amount_to_call()[player_index]:
#
#     action.
#
#   # If a player calls their entire stack, a new pot is created
#   if game.current_stack_sizes()[action.player_index] == action.amount:
#
#


def pot_per_winning_player(pot_size: int, winning_players: List[int]) -> Dict[int, int]:
  pot_even_division = pot_size // len(winning_players)
  leftover = pot_size - pot_even_division
  
  winning_per_player = {player_index: pot_even_division
                        for player_index in winning_players}
  
  while leftover > 0:
    for player_index in sorted(winning_players):
      winning_per_player[player_index] += 1
      leftover -= 1
      if leftover == 0:
        break
  
  return winning_per_player


def get_result(cards: FullDeal, game: GameView, pot: Pot) -> GameResults:
  # Calculate who has the best hand
  
  evaluator = Evaluator()
  
  showdown_hands: Dict[int, EvaluationResult] = {}
  
  for player_index in range(game.num_players()):
    
    if not game.is_folded()[player_index]:
      hole_cards = cards.hole_cards[player_index]
      board = cards.board
      
      eval_result = evaluator.evaluate(hole_cards, board)
      
      showdown_hands[player_index] = eval_result
  
  winning_players = get_winning_players(showdown_hands)
  
  profit_per_player = {player_index: -1 * amount_bet
                       for player_index, amount_bet in game.amount_added_total()}
  
  # For now, assume there is only one pot.
  # TODO: Support Side Pots
  pot_size = pot.side_pots[0].amount
  
  for player_index, winnings in pot_per_winning_player(pot_size, winning_players):
    profit_per_player[player_index] += winnings
  
  return GameResults(best_hand_index=winning_players,
                     profits=[profit_per_player[player_index]
                              for player_index in range(game.num_players())])
