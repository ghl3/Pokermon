from pokermon.poker import rules
from pokermon.poker.game import Game, Action, Street


def test_street_over():
  game = Game(stacks=[100, 200, 300])
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().small_blind())
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().big_blind())
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().bet_raise(to=10))
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().call())
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().call())
  assert rules.street_over(game.view()) == True
  
  # Flop
  game.current_street = Street.FLOP
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().call())
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().call())
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().call())
  assert rules.street_over(game.view()) == True
  
  # Turn
  game.current_street = Street.TURN
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().bet_raise(to=20))
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().fold())
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().call())
  assert rules.street_over(game.view()) == True
  
  # River
  game.current_street = Street.TURN
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().call())
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().bet_raise(to=30))
  assert rules.street_over(game.view()) == False
  
  game.add_action(game.view().call())
  assert rules.street_over(game.view()) == True
