from typing import List, Dict

from pokermon.poker.evaluation import Evaluator, EvaluationResult
from pokermon.poker.game import GameView, GameResults, Action, Move, Pot
from pokermon.poker.game import BIG_BIND_AMOUNT
from pokermon.poker.cards import FullDeal


def min_bet_amount(game: GameView) -> int:
  return max(BIG_BIND_AMOUNT, game.latest_bet_raise_amount)


def action_valid(action_index: int, player_index: int, action: Action, game: GameView) -> bool:
  if action_index == 0:
    return action.move == Move.SMALL_BLIND
  
  if action_index == 1:
    return action.move == Move.BIG_BLIND
  
  if action.move == Move.FOLD:
    return action.amount == 0
  
  # Blinds handled elsewhere
  elif action.move in {Move.SMALL_BLIND, Move.BIG_BLIND}:
    return False
  
  elif action.move == Move.CHECK_CALL:
    
    amount_to_call = game.amount_to_call()[player_index]
    player_stack = game.current_stack_sizes()[player_index]
    
    if amount_to_call <= player_stack:
      
      if action.amount != amount_to_call:
        return False
    
    else:
      
      # Player calls all in
      if action.amount != player_stack:
        return False
  
  elif action.move == Move.BET_RAISE:
    
    if action.amount == 0:
      return False
    
    player_stack = game.current_stack_sizes()[player_index]
    
    # Player goes all in.  You can always call all in.
    if action.amount == player_stack:
      return True
    
    else:
      
      # Must bet at least the big blind OR must raise at least as much as the
      # last bet/raise
      min_bet_amount = max(BIG_BIND_AMOUNT, game.latest_bet_raise_amount)
      
      # Player must raise at least as much as the previous raise.
      if action.amount < min_bet_amount:
        return False
  
  return True


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
  pot.side_pots[0].amount += action.amount


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
                       for player_index, amount_bet in game.amount_bet_total()}
  
  # For now, assume there is only one pot.
  # TODO: Support Side Pots
  pot_size = pot.side_pots[0].amount
  
  for player_index, winnings in pot_per_winning_player(pot_size, winning_players):
    profit_per_player[player_index] += winnings
  
  return GameResults(best_hand_index=winning_players,
                     profits=[profit_per_player[player_index]
                              for player_index in range(game.num_players())])
