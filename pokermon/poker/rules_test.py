from pokermon.poker import rules
from pokermon.poker.cards import Board, FullDeal, mkcard, mkflop, mkhand
from pokermon.poker.evaluation import Evaluator
from pokermon.poker.game import Game, Street
from pokermon.poker.rules import get_pot_payouts


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


def test_game_result():
    deal = FullDeal(
        hole_cards=[mkhand("AcAh"), mkhand("KdKs"), mkhand("JhJd")],
        board=Board(flop=mkflop("6dQc2s"), turn=mkcard("6s"), river=mkcard("3c")),
    )

    game = Game(starting_stacks=[100, 200, 300])

    game.add_action(game.view().small_blind())
    game.add_action(game.view().big_blind())
    game.add_action(game.view().bet_raise(to=10))
    game.add_action(game.view().call())
    game.add_action(game.view().call())

    game.set_street(Street.FLOP)
    game.add_action(game.view().bet_raise(to=20))
    game.add_action(game.view().call())
    game.add_action(game.view().call())

    game.set_street(Street.TURN)
    game.add_action(game.view().bet_raise(to=30))
    game.add_action(game.view().call())
    game.add_action(game.view().call())

    game.set_street(Street.RIVER)
    game.add_action(game.view().call())
    game.add_action(game.view().call())
    game.add_action(game.view().call())

    rules.get_result(deal, game.view(), Evaluator())


def test_pot_payouts():

    assert get_pot_payouts([[0], [1]],
                           [20, 20]) == {0: 40, 1: 0}

    assert get_pot_payouts([[0], [1], [2]],
                           [10, 25, 25]) == {0: 30, 1: 30, 2: 0}

    assert get_pot_payouts([[2], [0], [1], [3]],
                           [0, 10, 10, 10]) == {2: 30, 1: 0, 0: 0, 3: 0}

    assert get_pot_payouts([[0, 1], [2], [3]],
                           [10, 20, 30, 30]) == {0: 20, 1: 20 + 30, 2: 20, 3: 0}

    assert get_pot_payouts([[0], [1, 2], [3]],
                           [10, 20, 30, 30]) == {0: 40, 1: 15, 2: 15 + 20, 3: 0}

    assert get_pot_payouts([[0, 1, 2], [3], [4]],
                           [50, 50, 50, 50, 50]) == {0: 84, 1: 83, 2: 83, 3: 0, 4: 0}

    assert get_pot_payouts([[0, 1, 2], [3], [4]],
                           [50, 50, 50, 100, 100]) == {0: 84, 1: 83, 2: 83, 3: 100, 4: 0}