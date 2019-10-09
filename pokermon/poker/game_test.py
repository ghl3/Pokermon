from pokermon.poker.game import Game, Action, Move, Street


def test_num_players():
  game = Game(stacks=[100, 200, 300])
  
  assert game.num_players() == 3
  assert game.view().num_players() == 3


def test_action_views():
  game = Game(stacks=[100, 200, 300])
  
  preflop_action = [
    Action(0, Move.SMALL_BLIND, total_bet=1, amount_added=1),
    Action(1, Move.BIG_BLIND, total_bet=2, amount_added=2),
    Action(2, Move.BET_RAISE, total_bet=6, amount_added=6),
    Action(0, Move.CHECK_CALL, total_bet=6, amount_added=5),
    Action(1, Move.CHECK_CALL, total_bet=6, amount_added=4),
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
    Action(0, Move.CHECK_CALL, total_bet=0, amount_added=0),
    Action(1, Move.BET_RAISE, total_bet=10, amount_added=10),
    Action(2, Move.FOLD, total_bet=10, amount_added=0),
    Action(0, Move.FOLD, total_bet=10, amount_added=0),
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
    Action(0, Move.SMALL_BLIND, total_bet=1, amount_added=1),
    Action(1, Move.BIG_BLIND, total_bet=2, amount_added=2),
    Action(2, Move.BET_RAISE, total_bet=6, amount_added=6)]


def test_amount_bet():
  game = Game(stacks=[100, 200, 300])
  
  preflop_action = [
    Action(0, Move.SMALL_BLIND, total_bet=1, amount_added=1),
    Action(1, Move.BIG_BLIND, total_bet=2, amount_added=2),
    Action(2, Move.BET_RAISE, total_bet=6, amount_added=6),
  ]
  
  for a in preflop_action:
    game.add_action(a)
  
  assert game.view().amount_added_in_street() == {0: 1, 1: 2, 2: 6}
  
  game.current_street = Street.FLOP
  
  flop_action = [
    Action(0, Move.CHECK_CALL, total_bet=0, amount_added=0),
    Action(1, Move.BET_RAISE, total_bet=10, amount_added=10),
    Action(2, Move.FOLD, amount_added=0, total_bet=10),
    Action(0, Move.FOLD, amount_added=0, total_bet=10),
  ]
  
  for a in flop_action:
    game.add_action(a)
  
  assert game.view().amount_added_in_street() == {0: 0, 1: 10, 2: 0}
  assert game.view().amount_added_total() == {0: 1, 1: 12, 2: 6}


def test_stack_sizes():
  game = Game(stacks=[100, 200, 300])
  
  assert game.view().current_stack_sizes() == {0: 100, 1: 200, 2: 300}
  
  game.add_action(Action(0, Move.SMALL_BLIND, total_bet=1, amount_added=1))
  game.add_action(Action(1, Move.BIG_BLIND, total_bet=2, amount_added=2))
  game.add_action(Action(2, Move.BET_RAISE, total_bet=6, amount_added=6))
  assert game.view().current_stack_sizes() == {0: 99, 1: 198, 2: 294}
  
  game.add_action(Action(0, Move.CHECK_CALL, total_bet=6, amount_added=5))
  game.add_action(Action(1, Move.CHECK_CALL, total_bet=6, amount_added=4))
  assert game.view().current_stack_sizes() == {0: 94, 1: 194, 2: 294}
  
  game.current_street = Street.TURN
  
  game.add_action(Action(0, Move.CHECK_CALL, total_bet=0, amount_added=0))
  game.add_action(Action(1, Move.BET_RAISE, total_bet=10, amount_added=10))
  assert game.view().current_stack_sizes() == {0: 94, 1: 184, 2: 294}


def test_bet_and_call_amount():
  game = Game(stacks=[100, 200, 300])
  
  assert game.view().current_bet_amount() == 0
  assert game.view().amount_to_call() == {0: 0, 1: 0, 2: 0}
  
  game.add_action(Action(0, Move.SMALL_BLIND, total_bet=1, amount_added=1))
  assert game.view().current_bet_amount() == 1
  assert game.view().amount_to_call() == {0: 0, 1: 1, 2: 1}
  
  game.add_action(Action(1, Move.BIG_BLIND, total_bet=2, amount_added=2))
  game.add_action(Action(2, Move.BET_RAISE, total_bet=10, amount_added=10))
  assert game.view().current_bet_amount() == 10
  assert game.view().amount_to_call() == {0: 9, 1: 8, 2: 0}
  
  game.add_action(Action(0, Move.CHECK_CALL, total_bet=10, amount_added=9))
  game.add_action(Action(1, Move.CHECK_CALL, total_bet=10, amount_added=8))
  assert game.view().current_bet_amount() == 10
  assert game.view().amount_to_call() == {0: 0, 1: 0, 2: 0}


def test_latest_bet_raise_amount():
  game = Game(stacks=[100, 200, 300])
  
  assert game.view().last_raise_amount() == 0
  
  game.add_action(Action(0, Move.SMALL_BLIND, total_bet=1, amount_added=1))
  assert game.view().last_raise_amount() == 1
  assert game.view().current_bet_amount() == 1
  
  game.add_action(Action(1, Move.BIG_BLIND, total_bet=2, amount_added=2))
  assert game.view().last_raise_amount() == 1
  assert game.view().current_bet_amount() == 2
  
  game.add_action(Action(2, Move.BET_RAISE, total_bet=10, amount_added=10))
  assert game.view().last_raise_amount() == 8
  assert game.view().current_bet_amount() == 10
  
  # Raise to 20 total.  This is a raise of 8 on top of the original 10.
  # It is a min-raise.
  game.add_action(Action(0, Move.BET_RAISE, total_bet=18, amount_added=18 - 1))
  assert game.view().last_raise_amount() == 8
  assert game.view().current_bet_amount() == 18
  
  # Riase it to 30 total (up from the previous 18).  This is a raise of 12.
  game.add_action(Action(1, Move.BET_RAISE, total_bet=30, amount_added=30 - 2))
  assert game.view().last_raise_amount() == 12
  assert game.view().current_bet_amount() == 30


def test_is_folded():
  game = Game(stacks=[100, 200, 300])
  
  game.add_action(Action(0, Move.SMALL_BLIND, total_bet=1, amount_added=1))
  game.add_action(Action(1, Move.BIG_BLIND, total_bet=2, amount_added=2))
  game.add_action(Action(2, Move.FOLD, total_bet=2, amount_added=0))
  
  assert game.view().is_folded() == {0: False, 1: False, 2: True}
  
  game.add_action(Action(1, Move.CHECK_CALL, total_bet=2, amount_added=1))
  game.add_action(Action(2, Move.CHECK_CALL, total_bet=2, amount_added=0))
  
  assert game.view().is_folded() == {0: False, 1: False, 2: True}
  
  game.current_street = Street.TURN
  
  assert game.view().is_folded() == {0: False, 1: False, 2: True}
  
  game.add_action(Action(0, Move.BET_RAISE, total_bet=10, amount_added=10))
  game.add_action(Action(1, Move.FOLD, total_bet=10, amount_added=0))
  assert game.view().is_folded() == {0: False, 1: True, 2: True}


def test_is_all_in():
  game = Game(stacks=[100, 200, 10])
  
  game.add_action(Action(0, Move.SMALL_BLIND, total_bet=1, amount_added=1))
  game.add_action(Action(1, Move.BIG_BLIND, total_bet=2, amount_added=2))
  game.add_action(Action(2, Move.BET_RAISE, total_bet=10, amount_added=10))
  
  assert game.view().is_all_in() == {0: False, 1: False, 2: True}
