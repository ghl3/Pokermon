from pokermon.features.action import (
    LastAction,
    NextAction,
    encode_action,
    make_action_from_encoded,
    make_last_actions,
    make_next_actions,
)
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
    assert encode_action(action, game.game_view()) == 4

    action = game.game_view().bet_raise(to=10)
    assert encode_action(action, game.game_view()) == 4

    action = game.game_view().bet_raise(to=12)
    assert encode_action(action, game.game_view()) == 5

    action = game.game_view().bet_raise(to=74)
    assert encode_action(action, game.game_view()) == 20

    action = game.game_view().bet_raise(to=78)
    assert encode_action(action, game.game_view()) == 21

    action = game.game_view().bet_raise(to=82)
    assert encode_action(action, game.game_view()) == 22

    action = game.game_view().go_all_in()
    assert encode_action(action, game.game_view()) == 22


def encode_min_raise():
    pass


def encode_all_in():
    pass


def test_action_decoded():
    game = GameRunner(starting_stacks=[100, 100, 84])
    game.start_game()

    assert make_action_from_encoded(0, game.game_view()) == game.game_view().fold()

    assert make_action_from_encoded(1, game.game_view()) == game.game_view().call()

    assert make_action_from_encoded(2, game.game_view()) == game.game_view().min_raise()

    assert make_action_from_encoded(2, game.game_view()) == game.game_view().bet_raise(
        to=4
    )

    assert make_action_from_encoded(3, game.game_view()) == game.game_view().bet_raise(
        to=8
    )

    assert make_action_from_encoded(4, game.game_view()) == game.game_view().bet_raise(
        to=12
    )

    assert make_action_from_encoded(20, game.game_view()) == game.game_view().bet_raise(
        to=76
    )

    assert make_action_from_encoded(21, game.game_view()) == game.game_view().bet_raise(
        to=80
    )

    assert make_action_from_encoded(22, game.game_view()) == game.game_view().bet_raise(
        to=84
    )

    assert (
        make_action_from_encoded(22, game.game_view()) == game.game_view().go_all_in()
    )


def test_fold_preflop() -> None:
    game = GameRunner(starting_stacks=[200, 250, 100])
    game.start_game()
    game.bet_raise(to=10)
    game.fold()
    game.fold()

    last_actions = make_last_actions(game.game_view())
    assert last_actions == [
        LastAction(
            move=-1,
            action_encoded=-1,
            amount_added=-1,
            amount_added_percent_of_remaining=-1,
            amount_raised=-1,
            amount_raised_percent_of_pot=-1,
        ),
        LastAction(
            move=5,
            action_encoded=4,
            amount_added=10,
            amount_added_percent_of_remaining=0.10,
            amount_raised=8,
            amount_raised_percent_of_pot=2.6666666666666665,
        ),
        LastAction(
            move=3,
            action_encoded=0,
            amount_added=0,
            amount_added_percent_of_remaining=0,
            amount_raised=0,
            amount_raised_percent_of_pot=0,
        ),
    ]

    next_actions = make_next_actions(game.game_view())

    assert next_actions == [
        NextAction(
            move=5, action_encoded=4, amount_added=10, amount_raised=8, new_total_bet=10
        ),
        NextAction(
            move=3, action_encoded=0, amount_added=0, amount_raised=0, new_total_bet=10
        ),
        NextAction(
            move=3, action_encoded=0, amount_added=0, amount_raised=0, new_total_bet=10
        ),
    ]


def test_decode_bug_a():
    game = GameRunner(starting_stacks=[208, 262])
    game.start_game()
    game.bet_raise(to=167)

    assert make_action_from_encoded(4, game.game_view()) == game.game_view().go_all_in()


def test_decode_bug_b():
    game = GameRunner(starting_stacks=[267, 194])
    game.start_game()
    game.bet_raise(to=82)
    game.bet_raise(to=192)

    assert (
        make_action_from_encoded(21, game.game_view()) == game.game_view().go_all_in()
    )


def test_decode_bug_c():
    game = GameRunner(starting_stacks=[219, 224])
    game.start_game()
    game.bet_raise(to=79)
    game.bet_raise(to=156)

    assert make_action_from_encoded(2, game.game_view()) == game.game_view().go_all_in()
    assert (
        make_action_from_encoded(18, game.game_view()) == game.game_view().go_all_in()
    )
