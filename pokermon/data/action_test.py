from pokermon.data.action import make_last_actions, LastAction, make_next_actions, NextAction, \
    encode_action, make_action_from_encoded
from pokermon.poker.game_runner import GameRunner


def test_action_encoded():
    game = GameRunner(starting_stacks=[100, 100, 82])
    game.start_game()

    action = game.game_view().min_raise()
    assert encode_action(action, game.game_view()) == 2

    action = game.game_view().bet_raise(to=4)
    assert encode_action(action, game.game_view()) == 2

    action = game.game_view().bet_raise(to=6)
    assert encode_action(action, game.game_view()) == 3

    action = game.game_view().bet_raise(to=8)
    assert encode_action(action, game.game_view()) == 3

    action = game.game_view().bet_raise(to=10)
    assert encode_action(action, game.game_view()) == 4

    action = game.game_view().bet_raise(to=74)
    assert encode_action(action, game.game_view()) == 20

    action = game.game_view().bet_raise(to=78)
    assert encode_action(action, game.game_view()) == 21

    action = game.game_view().bet_raise(to=82)
    assert encode_action(action, game.game_view()) == 22

    action = game.game_view().go_all_in()
    assert encode_action(action, game.game_view()) == 22


def test_action_decoded():
    game = GameRunner(starting_stacks=[100, 100, 82])
    game.start_game()

    assert make_action_from_encoded(0, game.game_view()) == game.game_view().fold()

    assert make_action_from_encoded(1, game.game_view()) == game.game_view().call()

    assert make_action_from_encoded(2, game.game_view()) == game.game_view().min_raise()

    assert make_action_from_encoded(2, game.game_view()) == game.game_view().bet_raise(to=4)

    assert make_action_from_encoded(3, game.game_view()) == game.game_view().bet_raise(to=6)

    assert make_action_from_encoded(4, game.game_view()) == game.game_view().bet_raise(to=10)

    assert make_action_from_encoded(20, game.game_view()) == game.game_view().bet_raise(to=74)

    assert make_action_from_encoded(21, game.game_view()) == game.game_view().bet_raise(to=78)

    assert make_action_from_encoded(22, game.game_view()) == game.game_view().bet_raise(to=82)

    assert make_action_from_encoded(22, game.game_view()) == game.game_view().go_all_in()


def test_fold_preflop() -> None:
    game = GameRunner(starting_stacks=[200, 250, 100])
    game.start_game()
    game.bet_raise(to=10)
    game.fold()
    game.fold()

    last_actions = make_last_actions(game.game_view())
    assert last_actions == [LastAction(move=-1, action_encoded=-1, amount_added=-1,
                                       amount_added_percent_of_remaining=-1, amount_raised=-1,
                                       amount_raised_percent_of_pot=-1),
                            LastAction(move=5, action_encoded=3, amount_added=10,
                                       amount_added_percent_of_remaining=10, amount_raised=8,
                                       amount_raised_percent_of_pot=266),
                            LastAction(move=3, action_encoded=0, amount_added=0,
                                       amount_added_percent_of_remaining=0, amount_raised=0,
                                       amount_raised_percent_of_pot=0)]

    next_actions = make_next_actions(game.game_view())

    assert next_actions == [
        NextAction(move=5, action_encoded=3, amount_added=10, amount_raised=8, new_total_bet=10),
        NextAction(move=3, action_encoded=0, amount_added=0, amount_raised=0, new_total_bet=10),
        NextAction(move=3, action_encoded=0, amount_added=0, amount_raised=0, new_total_bet=10)]
