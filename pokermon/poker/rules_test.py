from pokermon.poker import rules
from pokermon.poker.cards import FullDeal, Board, mkhand, mkflop, mkcard
from pokermon.poker.evaluation import Evaluator
from pokermon.poker.game import Game, Street


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
    assert rules.street_over(game.view()) == False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) == False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) == False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) == True

    # Turn
    game.set_street(Street.TURN)
    assert rules.street_over(game.view()) == False

    game.add_action(game.view().bet_raise(to=20))
    assert rules.street_over(game.view()) == False

    game.add_action(game.view().fold())
    assert rules.street_over(game.view()) == False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) == True

    # River
    game.set_street(Street.RIVER)
    assert rules.street_over(game.view()) == False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) == False

    game.add_action(game.view().bet_raise(to=30))
    assert rules.street_over(game.view()) == False

    game.add_action(game.view().call())
    assert rules.street_over(game.view()) == True


def test_street_over_all_fold():
    game = Game(starting_stacks=[100, 200, 300])

    game.add_action(game.view().small_blind())
    game.add_action(game.view().big_blind())
    game.add_action(game.view().bet_raise(to=10))
    game.add_action(game.view().fold())
    game.add_action(game.view().fold())

    assert rules.street_over(game.view()) == True

    game.set_street(Street.FLOP)
    assert rules.street_over(game.view()) == True

    game.set_street(Street.TURN)
    assert rules.street_over(game.view()) == True

    game.set_street(Street.RIVER)
    assert rules.street_over(game.view()) == True


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

    result = rules.get_result(deal, game.view(), Evaluator())
