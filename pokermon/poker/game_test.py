from pokermon.poker.game import Game, Action, Move, Street


def test_num_players():
  game = Game(stacks=[100, 200, 300])
  
  assert game.num_players() == 3
  assert game.view().num_players() == 3


def test_action_views():
  game = Game(stacks=[100, 200, 300])
  
  preflop_action = [
    Action(0, Move.SMALL_BLIND, amount=1),
    Action(1, Move.BIG_BLIND, amount=2),
    Action(2, Move.BET_RAISE, amount=6),
    Action(0, Move.CHECK_CALL, amount=5),
    Action(1, Move.CHECK_CALL, amount=4),
  ]
  
  for a in preflop_action:
    game.add_action(a)
  
  assert game.current_street == Street.PREFLOP
  assert game.get_street_action() == preflop_action
  
  preflop_view = game.view()
  assert preflop_view.street_action() == preflop_action
  assert preflop_view.action() == preflop_action
  
  game.current_street = Street.FLOP
  
  flop_action = [
    Action(0, Move.CHECK_CALL, amount=0),
    Action(1, Move.BET_RAISE, amount=10),
    Action(2, Move.FOLD, 0),
    Action(0, Move.FOLD, 0),
  ]
  
  for a in flop_action:
    game.add_action(a)
  
  assert game.current_street == Street.FLOP
  assert game.get_street_action() == flop_action
  
  assert preflop_view.street_action() == preflop_action
  assert preflop_view.action() == preflop_action
  
  # Recreate the preflop view
  preflop_view = game.view(timestamp=5)
  assert preflop_view.street_action() == preflop_action
  assert preflop_view.action() == preflop_action
  
  flop_view = game.view()
  
  assert flop_view.street_action() == flop_action
  assert flop_view.action() == preflop_action + flop_action
  
  # Test a view in the middle of the preflop
  
  mid_preflop_view = game.view(3)
  assert mid_preflop_view.street_action() == [
    Action(0, Move.SMALL_BLIND, amount=1),
    Action(1, Move.BIG_BLIND, amount=2),
    Action(2, Move.BET_RAISE, amount=6)]
