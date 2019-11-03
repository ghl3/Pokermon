from pokermon.data import features
from pokermon.poker import rules
from pokermon.poker.cards import FullDeal, mkhand, Board, mkflop, mkcard
from pokermon.poker.evaluation import Evaluator
from pokermon.poker.game import Game, Street


def test_basic_features():
    # A 3-player game that goes to the river.

    # Player 3 wins with a flopped set of jacks.
    deal = FullDeal(
        hole_cards=[mkhand("AcAd"),
                    mkhand("AsKh"),
                    mkhand("JcJh")],
        board=Board(flop=mkflop("KsJs3d"),
                    turn=mkcard("7s"),
                    river=mkcard("6s")))

    game = Game(starting_stacks=[100, 200, 300])

    game.add_action(game.view().small_blind())
    game.add_action(game.view().big_blind())
    game.add_action(game.view().bet_raise(to=10))
    game.add_action(game.view().call())
    game.add_action(game.view().call())

    # Flop
    game.set_street(Street.FLOP)
    game.add_action(game.view().call())
    game.add_action(game.view().call())
    game.add_action(game.view().call())

    # Turn
    game.set_street(Street.TURN)
    game.add_action(game.view().bet_raise(to=20))
    game.add_action(game.view().fold())
    game.add_action(game.view().call())

    # River
    game.set_street(Street.RIVER)
    game.add_action(game.view().call())
    game.add_action(game.view().bet_raise(to=30))
    game.add_action(game.view().call())

    evaluator = Evaluator()
    results = rules.get_result(deal, game.view(), evaluator)

    rows = features.make_rows(game, deal, results, evaluator)

    last_row = rows[-1]
