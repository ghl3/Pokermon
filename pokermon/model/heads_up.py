from typing import Tuple

import numpy as np
import tensorflow as tf
from tensorflow.python.feature_column import feature_column_v2 as fc
from tensorflow.python.feature_column import sequence_feature_column as sfc
from tensorflow.python.keras.feature_column import sequence_feature_column as ksfc

from pokermon.ai.policy import Policy
from pokermon.data.action import NUM_ACTION_BET_BINS, make_action_from_encoded
from pokermon.data.examples import make_forward_backward_example, make_forward_example
from pokermon.model.context_sequence_concat import ContextSequenceConcat
from pokermon.model.feature_config import FeatureConfig, FeatureTensors, TargetTensors
from pokermon.model.utils import ensure_all_dense, select_proportionally
from pokermon.poker.cards import Board, HoleCards
from pokermon.poker.game import Action, GameView, Street
from pokermon.poker.result import Result


def policy_vector_size():
    return NUM_ACTION_BET_BINS + 2


class HeadsUpModel(Policy):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.num_players = 2
        self.feature_config = self.make_feature_config(self.num_players)
        self.model = self.make_model(self.feature_config)
        self.optimizer = None
        self.manager = None

    @staticmethod
    def make_feature_config(num_players):
        return FeatureConfig(
            context_features=[
                fc.numeric_column(
                    "public_context__starting_stack_sizes",
                    shape=num_players,
                    dtype=tf.int64,
                ),
                # fc.numeric_column("private_context__hand_encoded", dtype=tf.int64),
                tf.feature_column.embedding_column(
                    tf.feature_column.categorical_column_with_vocabulary_list(
                        "private_context__hand_encoded", range(1326)
                    ),
                    dimension=4,
                ),
            ],
            sequence_features=[
                sfc.sequence_numeric_column(
                    "last_action__amount_added", dtype=tf.int64, default_value=-1
                ),
                sfc.sequence_numeric_column(
                    "public_state__all_in_player_mask",
                    dtype=tf.int64,
                    default_value=-1,
                    shape=2,
                ),
            ],
            context_targets=[
                fc.numeric_column(
                    "public_context__num_players", shape=1, dtype=tf.int64
                ),
            ],
            sequence_targets=[
                sfc.sequence_numeric_column(
                    "next_action__action_encoded", dtype=tf.int64, default_value=-1
                ),
                sfc.sequence_numeric_column(
                    "reward__cumulative_reward", dtype=tf.int64, default_value=-1
                ),
                sfc.sequence_numeric_column(
                    "public_state__pot_size", dtype=tf.int64, default_value=-1
                ),
                sfc.sequence_numeric_column(
                    "player_state__is_current_player", dtype=tf.int64, default_value=-1
                ),
            ],
        )

    @staticmethod
    def make_model(feature_config):

        ctx_inputs, seq_inputs = feature_config.make_model_input_configs()
        x = tf.keras.layers.DenseFeatures(feature_config.context_features)(ctx_inputs)
        y, _ = ksfc.SequenceFeatures(feature_config.sequence_features)(seq_inputs)
        z = ContextSequenceConcat()((x, y))
        z = tf.keras.layers.LSTM(units=32, return_sequences=True)(z)
        z = tf.keras.layers.Dense(64)(z)
        z = tf.keras.layers.Dense(policy_vector_size(), name="logits")(z)

        all_inputs = list(ctx_inputs.values()) + list(seq_inputs.values())
        return tf.keras.Model(inputs=all_inputs, outputs=z)

    def checkpoint(self):
        return tf.train.Checkpoint(
            step=tf.Variable(1), optimizer=self.optimizer, model=self.model
        )

    def checkpoint_manager(self, path):
        if self.manager is None:
            self.manager = tf.train.CheckpointManager(
                self.checkpoint(), path, max_to_keep=5
            )
        return self.manager

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

        serialized_example_tensor = tf.convert_to_tensor(example.SerializeToString())

        # Create the action probabilities at the last time step
        action_probs: np.Array = self._next_action_policy(
            [serialized_example_tensor]
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
        expected_reward = tf.cast(
            target_tensors["public_state__pot_size"]
            / target_tensors["public_context__num_players"],
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

        if self.optimizer is None:
            self.optimizer = tf.keras.optimizers.Adam()

        example = make_forward_backward_example(
            player_id, game, hole_cards, board, result
        )

        _, loss = self._update_weights(
            tf.convert_to_tensor([example.SerializeToString()])
        )

        return example, loss

    @tf.function(experimental_relax_shapes=True)
    def _next_action_policy(self, serialized_examples):
        fs = self.feature_config.make_feature_tensors(serialized_examples)
        # Create the action probabilities at the last time step
        return self.action_probs(fs)[0, -1, :]

    @tf.function(experimental_relax_shapes=True)
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
