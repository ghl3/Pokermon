from pokermon.data import features
from pokermon.data.examples import make_example
from pokermon.poker import rules
from pokermon.poker.cards import Board, FullDeal, mkcard, mkflop, mkhand
from pokermon.poker.evaluation import Evaluator
from pokermon.poker.game import Game


def test_empty_example() -> None:
    # Player 3 wins with a flopped set of jacks.
    deal = FullDeal(
        hole_cards=[mkhand("AcAd"), mkhand("AsKh"), mkhand("JcJh")],
        board=Board(flop=mkflop("KsJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = Game(starting_stacks=[100, 200, 300])

    game.add_action(game.view().small_blind())
    game.add_action(game.view().big_blind())
    game.add_action(game.view().bet_raise(to=10))
    game.add_action(game.view().fold())
    game.add_action(game.view().fold())

    evaluator = Evaluator()
    results = rules.get_result(deal, game.view(), evaluator)

    rows = features.make_rows(game, deal, results, evaluator)

    example = make_example(rows)

    assert len(example.features.feature) == 33
