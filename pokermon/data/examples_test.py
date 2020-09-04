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

    # Context Features
    assert example_dict['context']['num_players'] == [3]
    assert example_dict['context']['starting_stack_sizes'] == [100, 200, 300]

    # Player 3 (UTG) wins the blinds, the others lose their blinds
    assert example_dict['context']['total_rewards'] == [-1, -2, 3]

    # Bet, Fold, Fold
    assert example_dict['features']['action__action_encoded'] == [[5], [3], [3]]

    # Bet 10, fold, fold
    assert example_dict['features']['action__amount_added'] == [[10], [0], [0]]

    # These are the states before the action (the blinds have already taken place)
    assert example_dict['features']['state__stack_sizes'] == [[99, 198, 300], [99, 198, 290],
                                                              [99, 198, 290]]

    # Hole Cards 0: Jc Ac As
    # Hole Cards 1: Jh Ad Kh
    assert example_dict['features']['state__hole_card_0_rank'] == [[11], [14], [14]]
    assert example_dict['features']['state__hole_card_0_suit'] == [[2], [2], [1]]
    assert example_dict['features']['state__hole_card_1_rank'] == [[11], [14], [13]]
    assert example_dict['features']['state__hole_card_1_suit'] == [[4], [3], [4]]

    # These are the indices of the actions
    assert example_dict['features']['state__action_index'] == [[3], [4], [5]]
