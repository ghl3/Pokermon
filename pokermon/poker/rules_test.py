from pokermon.poker import rules
from pokermon.poker.game import Game, Move, Street
from pokermon.poker.game_runner import GameRunner
from pokermon.poker.rules import (
    Error,
    Metadata,
    ValidationResult,
    get_pot_payouts,
    voluntary_action_allowed,
)


def test_street_over():
    game = Game(starting_stacks=[100, 200, 300])
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().small_blind())
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().big_blind())
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().bet_raise(to=10))
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) is True

    # Flop
    game.set_street(Street.FLOP)
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) is True

    # Turn
    game.set_street(Street.TURN)
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().bet_raise(to=20))
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().fold())
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) is True

    # River
    game.set_street(Street.RIVER)
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().bet_raise(to=30))
    assert rules.street_over(game.view()) is False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) is True


def test_street_over_all_fold():
    game = Game(starting_stacks=[100, 200, 300])

    game.add_action(game.view().small_blind())
    game.add_action(game.view().big_blind())
    game.add_action(game.view().bet_raise(to=10))
    game.add_action(game.view().fold())
    game.add_action(game.view().fold())

    assert rules.street_over(game.view()) is True

    game.set_street(Street.FLOP)
    assert rules.street_over(game.view()) is True

    game.set_street(Street.TURN)
    assert rules.street_over(game.view()) is True

    game.set_street(Street.RIVER)
    assert rules.street_over(game.view()) is True


def test_pot_payouts():
    assert get_pot_payouts([[0], [1]], [20, 20]) == {0: 40, 1: 0}

    assert get_pot_payouts([[0], [1], [2]], [10, 25, 25]) == {0: 30, 1: 30, 2: 0}

    assert get_pot_payouts([[2], [0], [1], [3]], [0, 10, 10, 10]) == {
        2: 30,
        1: 0,
        0: 0,
        3: 0,
    }

    assert get_pot_payouts([[0, 1], [2], [3]], [10, 20, 30, 30]) == {
        0: 20,
        1: 20 + 30,
        2: 20,
        3: 0,
    }

    assert get_pot_payouts([[0], [1, 2], [3]], [10, 20, 30, 30]) == {
        0: 40,
        1: 15,
        2: 15 + 20,
        3: 0,
    }

    assert get_pot_payouts([[0, 1, 2], [3], [4]], [50, 50, 50, 50, 50]) == {
        0: 84,
        1: 83,
        2: 83,
        3: 0,
        4: 0,
    }

    assert get_pot_payouts([[0, 1, 2], [3], [4]], [50, 50, 50, 100, 100]) == {
        0: 84,
        1: 83,
        2: 83,
        3: 100,
        4: 0,
    }


def test_call_or_raise_all_in():
    game = GameRunner(starting_stacks=[30, 20])
    game.start_game()

    # Raise to 10, which is 8 on top
    game.bet_raise(to=30)

    assert voluntary_action_allowed(
        game.game_view().bet_raise(to=20), game.game_view()
    ) == ValidationResult(
        error=Error.INVALID_MOVE,
        metadata={Metadata.ALLOWED_MOVES_ARE: [Move.FOLD, Move.CHECK_CALL]},
    )

    assert voluntary_action_allowed(
        game.game_view().call(), game.game_view()
    ) == ValidationResult(error=None, metadata={})


def test_min_raise():
    game = GameRunner(starting_stacks=[20, 20])
    game.start_game()

    # Raise to 10, which is 8 on top
    game.bet_raise(to=10)

    assert voluntary_action_allowed(
        game.game_view().bet_raise(to=17), game.game_view()
    ) == ValidationResult(
        error=Error.MIN_RAISE_REQUIRED, metadata={Metadata.RAISE_MUST_BE_GE: 8}
    )


def test_min_raise_when_all_in():
    game = GameRunner(starting_stacks=[20, 12])
    game.start_game()

    # Raise to 10, which is 8 on top
    game.bet_raise(to=10)

    # You can go all in
    assert voluntary_action_allowed(
        game.game_view().bet_raise(to=12), game.game_view()
    ) == ValidationResult(error=None, metadata={})

    # But you must do the right all in amount
    assert voluntary_action_allowed(
        game.game_view().bet_raise(to=20), game.game_view()
    ) == ValidationResult(
        error=Error.INVALID_AMOUNT_ADDED,
        metadata={Metadata.AMOUNT_ADDED_SHOULD_BE_LE: 10},
    )
