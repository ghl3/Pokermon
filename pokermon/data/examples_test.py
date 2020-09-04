import pytest
import tensorflow as tf  # type: ignore

from pokermon.data import features
from pokermon.data.examples import make_example, _int64_feature, _float_feature, _bytes_feature, \
    example_to_dict
from pokermon.poker import rules
from pokermon.poker.cards import Board, FullDeal, mkcard, mkflop, mkhand
from pokermon.poker.evaluation import Evaluator
from pokermon.poker.game import Game


def test_example_to_dict() -> None:
    example = tf.train.Example(features=tf.train.Features(feature=dict(
        foo=_int64_feature([1, 2, 3]), bar=_float_feature([.4, .5, .6]),
        baz=_bytes_feature(["Fish"]))))

    assert example_to_dict(example) == {'foo': [1, 2, 3], 'bar': pytest.approx([.4, .5, .6]),
                                        'baz': ["Fish"]}


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
    game.end_hand()

    evaluator = Evaluator()
    results = rules.get_result(deal, game.view(), evaluator)
    rows = features.make_rows(game, deal, results, evaluator)

    example = make_example(rows)

    assert len(example.features.feature) == 33

    # Assert that all features have length:
    # num_actions or num_actions*num_players
    for k, v in example_to_dict(example).items():
        assert len(v) == 5 or len(v) == 5 * 3
