from typing import Tuple

import numpy as np  # type: ignore
import tensorflow as tf  # type: ignore

from pokermon.ai.policy import Policy
from pokermon.features.action import make_action_from_encoded
from pokermon.features.examples import (
    make_forward_backward_example,
    make_forward_example,
)
from pokermon.model import rnn
from pokermon.model.feature_config import FeatureTensors, TargetTensors
from pokermon.model.model_features import make_feature_config
from pokermon.model.rnn import policy_vector_size
from pokermon.model.utils import ensure_all_dense, select_proportionally
from pokermon.poker.board import Board
from pokermon.poker.game import Action, GameView, Street
from pokermon.poker.hands import HoleCards
from pokermon.poker.result import Result


class HeadsUpModel(Policy):
    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name
        self.num_players = 2
        self.feature_config = make_feature_config(self.num_players)
        self.model = rnn.make_model(self.feature_config)
        self.optimizer = tf.keras.optimizers.Adam()

    def name(self) -> str:
        return self.model_name

    def select_action(
        self, player_index: int, game: GameView, hole_cards: HoleCards, board: Board
    ) -> Action:
        """
        Select the next action to take.  This can be a stocastic choice.
        """
        assert game.street() != Street.HAND_OVER
        assert game.current_player() == player_index
        board = board.at_street(game.street())

        example: tf.train.SequenceExample = make_forward_example(
            player_index, game, hole_cards, board
        )

        serialized_example_tensor = tf.convert_to_tensor([example.SerializeToString()])

        # Create the action probabilities at the last time step
        action_probs: np.Array = self._next_action_policy(
            serialized_example_tensor
        ).numpy()
        action_index = select_proportionally(action_probs)
        return make_action_from_encoded(action_index=action_index, game=game)

    def action_probs(self, feature_tensors: FeatureTensors) -> tf.Tensor:
        return tf.nn.softmax(self.action_logits(feature_tensors))

    def action_logits(self, feature_tensors: FeatureTensors) -> tf.Tensor:
        return self.model(feature_tensors)

    def loss(self, feature_tensors: FeatureTensors, target_tensors: TargetTensors):
        """
        Returns the loss for each batch element and each timestep.
        [batch_size, time]
        """

        # TODO: This seems weird/unnecessary...?
        target_tensors = ensure_all_dense(target_tensors)

        # [batch, time]
        next_actions = target_tensors["next_action__action_encoded"]

        next_actions_one_hot = tf.squeeze(
            tf.one_hot(next_actions, depth=policy_vector_size()), axis=2
        )

        policy_logits = self.action_logits(feature_tensors)
        reward = tf.cast(target_tensors["reward__cumulative_reward"], tf.float32)

        # Determine our expectation of the reward we'll get.  Currently, this is just
        # a naive equal splitting of the existing pot.
        # TODO: These shouldn't be 'targets'.  Re-think difference between model input
        # tensors and other data that is available.  Maybe just call it backwards...?

        pot_size = target_tensors["public_state__pot_size"]
        tf.debugging.assert_greater_equal(
            pot_size,
            tf.cast(0, tf.int64),
            "pot size negatve",
        )
        num_players = target_tensors["public_state__num_players_remaining"]
        tf.debugging.assert_greater(
            num_players,
            tf.cast(1, tf.int64),
            "num payers less than 2",
        )
        expected_reward = tf.cast(
            pot_size / num_players,
            tf.float32,
        )

        # We apply a trick to get the REENFORCE loss.
        # The update step is defined as:
        # theta <- theta + reward * grad(log(prob[i])),
        # where i is the index of the action that was actually taken.
        # We can make this using normal neural network optimizations by making
        # a loss of the term:
        # loss = reward * log(prob[i])
        # And since we use softmax to turn our logits into probabilities, we can
        # calculate this loss using the following term (noting that we include a
        # negative sign to counter-act the negative sign in from the definition
        # of cross entropy):
        cross_entropy = tf.nn.softmax_cross_entropy_with_logits(
            labels=next_actions_one_hot, logits=policy_logits
        )

        player_mask = tf.squeeze(
            tf.equal(target_tensors["player_state__is_current_player"], 1), -1
        )

        return tf.where(
            player_mask,
            -1 * tf.squeeze(reward - expected_reward, -1) * cross_entropy,
            tf.zeros_like(cross_entropy),
        )

    def train_step(
        self,
        player_id: int,
        game: GameView,
        hole_cards: HoleCards,
        board: Board,
        result: Result,
    ) -> Tuple[tf.train.SequenceExample, float]:

        example = make_forward_backward_example(
            player_id, game, hole_cards, board, result
        )

        _, loss = self._update_weights(
            tf.convert_to_tensor([example.SerializeToString()])
        )

        return example, loss

    @tf.function(
        input_signature=[tf.TensorSpec(shape=(1,), dtype=tf.string)], autograph=False
    )
    def _next_action_policy(self, serialized_examples):
        fs = self.feature_config.make_feature_tensors(serialized_examples)
        # Create the action probabilities at the last time step
        return self.action_probs(fs)[0, -1, :]

    @tf.function(
        input_signature=[tf.TensorSpec(shape=(1,), dtype=tf.string)], autograph=False
    )
    def _update_weights(self, serialized_examples):
        with tf.GradientTape() as tape:
            (
                feature_tensors,
                target_tensors,
            ) = self.feature_config.make_features_and_target_tensors(
                serialized_examples
            )

            loss_value = tf.reduce_mean(self.loss(feature_tensors, target_tensors))

            gradients = tape.gradient(loss_value, self.model.trainable_variables)
            self.optimizer.apply_gradients(
                zip(gradients, self.model.trainable_variables)
            )

        return gradients, loss_value
