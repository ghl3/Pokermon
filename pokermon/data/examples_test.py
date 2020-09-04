import pytest
import tensorflow as tf  # type: ignore

from pokermon.data import reenforcement_types
from pokermon.data.examples import make_example, _int64_feature, _float_feature, _bytes_feature, \
    seq_example_to_dict
from pokermon.poker import rules
from pokermon.poker.cards import Board, FullDeal, mkcard, mkflop, mkhand
from pokermon.poker.evaluation import Evaluator
from pokermon.poker.game import Game, Street


def test_empty_example() -> None:
    # Player 3 wins with a flopped set of jacks.
    deal = FullDeal(
        hole_cards=[mkhand("AcAd"), mkhand("AsKh"), mkhand("JcJh")],
        board=Board(flop=mkflop("KsJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = Game(starting_stacks=[100, 200, 300])

    game.set_street(Street.PREFLOP)
    game.add_action(game.view().small_blind())
    game.add_action(game.view().big_blind())
    game.add_action(game.view().bet_raise(to=10))
    game.add_action(game.view().fold())
    game.add_action(game.view().fold())
    game.end_hand()

    evaluator = Evaluator()
    results = rules.get_result(deal, game.view(), evaluator)
    context, rows = reenforcement_types.make_rows(game, deal, results, evaluator)

    example = make_example(context, rows)

    example_dict = seq_example_to_dict(example)

    assert example_dict['context']['num_players'] == [3]
    assert example_dict['context']['starting_stack_sizes'] == [100, 200, 300]

    # Player 3 (UTG) wins the blinds
    # Shouldn't other players lose 1 and 2?
    assert example_dict['context']['total_rewards'] == [0, 0, 3]



# assert len(example.features.feature) == 33

# There should be 3 decision points that are made
# - 1: The First Bet
# - 2: The First Fold
# - 3: The Second Fold

# x = seq_example_to_dict(example)

#    for k, v in seq_example_to_dict(example)['features'].items():
#        assert len(v) == 3 or len(v) == 3 * 3
