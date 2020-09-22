import numpy as np
import tensorflow as tf
from numpy.testing import assert_array_almost_equal

from pokermon.data.examples import make_forward_backward_example, make_forward_example
from pokermon.model import heads_up
from pokermon.poker import result
from pokermon.poker.cards import Board, FullDeal, mkcard, mkflop, mkhand
from pokermon.poker.game_runner import GameRunner


def test_action_probs():
    deal = FullDeal(
        hole_cards=[mkhand("AcAd"), mkhand("AsKh")],
        board=Board(flop=mkflop("KsJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = GameRunner(starting_stacks=[300, 400])
    game.start_game()

    # Preflop
    game.bet_raise(to=10)
    game.call()

    # Flop
    game.bet_raise(to=25)
    game.call()

    # Turn
    game.check()
    game.bet_raise(to=40)
    game.call()

    # River
    game.check()
    game.check()

    model = heads_up.HeadsUpModel("HeadsUp")

    player_index = 1

    example = make_forward_example(
        player_index,
        game.game_view(),
        deal.hole_cards[player_index],
        deal.board,
    )

    logits = model.action_logits(
        model.feature_config.make_feature_tensors([example.SerializeToString()])
    )

    batch_size = 1
    num_steps = 9
    num_possible_actions = 22
    assert logits.shape == [batch_size, num_steps, num_possible_actions]

    probs = model.action_probs(
        model.feature_config.make_feature_tensors([example.SerializeToString()])
    )

    assert_array_almost_equal(
        tf.reduce_sum(probs, -1).numpy(), np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1]])
    )


def test_loss():
    deal = FullDeal(
        hole_cards=[mkhand("AcAd"), mkhand("AsKh")],
        board=Board(flop=mkflop("KsJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = GameRunner(starting_stacks=[300, 400])
    game.start_game()

    # Preflop
    game.bet_raise(to=10)
    game.call()

    # Flop
    game.bet_raise(to=25)
    game.call()

    # Turn
    game.check()
    game.bet_raise(to=40)
    game.call()

    # River
    game.check()
    game.check()

    results = result.get_result(deal, game.game_view())

    model = heads_up.HeadsUpModel("HeadsUp")

    player_index = 1

    example = make_forward_backward_example(
        player_index,
        game.game_view(),
        deal.hole_cards[player_index],
        deal.board,
        results,
    )

    (
        feature_tensors,
        target_tensors,
    ) = model.feature_config.make_features_and_target_tensors(
        [example.SerializeToString()]
    )

    print(tf.cast(target_tensors["reward__cumulative_reward"], tf.float32))

    loss = model.loss(feature_tensors, target_tensors)

    batch_size = 1
    num_steps = 9
    assert loss.shape == [batch_size, num_steps]
