from typing import Dict, Tuple

import numpy as np
import tensorflow as tf

from pokermon.ai.policy import Policy
from pokermon.data import features
from pokermon.data.action import (
    NUM_ACTION_BET_BINS,
    LastAction,
    NextAction,
    make_action_from_encoded,
    make_last_actions,
    make_next_actions,
)
from pokermon.data.examples import make_example
from pokermon.data.rewards import Reward, make_rewards
from pokermon.data.state import (
    PrivateState,
    PublicState,
    make_private_states,
    make_public_states,
)
from pokermon.model import utils
from pokermon.model.utils import make_sequence_dict_of_dense, select_proportionally
from pokermon.poker.cards import Board, HoleCards
from pokermon.poker.game import Action, GameView, Street
from pokermon.poker.rules import GameResults


def policy_vector_size():
    return NUM_ACTION_BET_BINS + 2


FeatureTensors = Dict[str, tf.Tensor]
TargetTensors = Dict[str, tf.Tensor]


class HeadsUpModel(Policy):
    def __init__(
        self,
        name,
        player_id,
    ):
        super().__init__()

        self.num_players = 2
        self.player_id = player_id

        self.features = {}
        self.features.update(
            features.make_feature_config(PublicState, is_sequence=True)
        )
        self.features.update(
            features.make_feature_config(PrivateState, is_sequence=True)
        )
        self.features.update(features.make_feature_config(LastAction, is_sequence=True))

        self.targets = {}
        self.targets.update(features.make_feature_config(NextAction, is_sequence=True))
        self.targets.update(features.make_feature_config(Reward, is_sequence=True))

        self.model = tf.keras.Sequential(name=name)
        self.model.add(
            tf.keras.layers.LSTM(
                input_dim=self.num_features(), return_sequences=True, units=32
            )
        )
        self.model.add(tf.keras.layers.Dense(64))
        self.model.add(tf.keras.layers.Dense(policy_vector_size()))

        self.optimizer = None

    def select_action(
        self, player_index: int, game: GameView, hole_cards: HoleCards, board: Board
    ) -> Action:
        """
        Select the next action to take.  This can be a stocastic choice.
        """
        assert game.street() != Street.OVER
        assert game.current_player() == self.player_id
        assert player_index == self.player_id
        board = board.at_street(game.street())

        example: tf.train.SequenceExample = self.make_forward_example(game, hole_cards, board)

        feature_tensors = self.make_feature_tensors(example.SerializeToString())
        # Create the action probabilities at the last timestep
        action_probs: np.Array = self.action_probs(feature_tensors)[0, -1, :].numpy()
        action_index = select_proportionally(action_probs)
        return make_action_from_encoded(action_index=action_index, game=game)

    def num_features(self):

        num = 0

        for _, feature_col in self.features.items():
            if isinstance(feature_col, tf.io.FixedLenSequenceFeature):
                num += 1
            elif isinstance(feature_col, tf.io.VarLenFeature):
                num += self.num_players
            else:
                raise Exception()
        return num

    def make_forward_example(
        self, game: GameView, hole_cards: HoleCards, board: Board
    ) -> tf.train.SequenceExample:
        """
        All tensors have shape:
        [batch_size=1, time, 1 OR num_players=2]
        """

        assert game.num_players() == self.num_players

        return make_example(
            public_states=make_public_states(game, board=board),
            private_states=make_private_states(game, board=board, hole_cards=hole_cards),
            last_actions=make_last_actions(game),
        )

    def make_feature_tensors(self, serialized_example: str) -> FeatureTensors:
        context_dict, sequence_dict = tf.io.parse_single_sequence_example(
            serialized_example,
            context_features={},
            sequence_features=self.features,
            example_name=None,
            name=None,
        )

        return make_sequence_dict_of_dense(sequence_dict)

    def make_forward_backward_example(
        self, game: GameView, hole_cards: HoleCards, board: Board, results: GameResults
    ) -> tf.train.SequenceExample:
        """
        All tensors have shape:
        [batch_size=1, time, 1 OR num_players=2]
        """

        assert game.num_players() == self.num_players
        assert game.street() == Street.OVER

        return make_example(
            public_states=make_public_states(game, board=board),
            private_states=make_private_states(game, board=board, hole_cards=hole_cards),
            last_actions=make_last_actions(game),
            next_actions=make_next_actions(game), rewards=make_rewards(game, results)
        )

    def make_features_and_target_tensors(
        self, serialized_example: str
    ) -> Tuple[FeatureTensors, TargetTensors]:
        """
        All tensors have shape:
        [batch_size=1, time, 1 OR num_players=2]
        """

        sequence_features = {}
        sequence_features.update(self.features)
        sequence_features.update(self.targets)

        context_dict, sequence_dict = tf.io.parse_single_sequence_example(
            serialized_example,
            context_features={},
            sequence_features=sequence_features,
            example_name=None,
            name=None,
        )

        feature_dict = {name: tensor for (name, tensor) in sequence_dict.items()
                        if name in self.features}

        target_dict = {name: tensor for (name, tensor) in sequence_dict.items()
                       if name in self.targets}

        return make_sequence_dict_of_dense(feature_dict), make_sequence_dict_of_dense(
            target_dict)

    def action_probs(self, feature_tensors: FeatureTensors) -> tf.Tensor:
        return tf.nn.softmax(self.make_action_logits(feature_tensors))

    def make_action_logits(self, feature_tensors: FeatureTensors) -> tf.Tensor:
        return self.model(utils.concat_feature_tensors(feature_tensors))

    def loss(self, feature_tensors: FeatureTensors, target_tensors: TargetTensors):
        """
        Returns the loss for each batch element and each timestep.
        [batch_size, time]
        """

        # [batch, time]
        next_actions = target_tensors["next_action__action_encoded"]

        next_actions_one_hot = tf.squeeze(
            tf.one_hot(next_actions, depth=policy_vector_size()), axis=2
        )

        policy_logits = self.make_action_logits(feature_tensors)
        reward = tf.cast(target_tensors["reward__cumulative_reward"], tf.float32)

        # We apply a trick to get teh REENFORCE loss.
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
            feature_tensors["public_state__current_player_index"] == self.player_id, -1
        )

        return tf.where(
            player_mask,
            -1 * tf.squeeze(reward, -1) * cross_entropy,
            tf.zeros_like(cross_entropy),
        )

    def train_step(
        self, game: GameView, hole_cards: HoleCards, board: Board, results: GameResults
    ):

        if self.optimizer is None:
            self.optimizer = tf.keras.optimizers.Adam()

        example = self.make_forward_backward_example(game, hole_cards, board, results)

        self._update_weights(example.SerializeToString())


    @tf.function
    def _update_weights(self, serialized_example):

        with tf.GradientTape() as tape:
            feature_tensors, target_tensors = self.make_features_and_target_tensors(
                serialized_example)

            loss_value = tf.reduce_mean(self.loss(feature_tensors, target_tensors))

            gradients = tape.gradient(loss_value, self.model.trainable_variables)
            self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))

        return loss_value
