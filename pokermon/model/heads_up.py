from typing import Tuple

import numpy as np
import tensorflow as tf

from pokermon.ai.policy import Policy
from pokermon.data.action import (
    NUM_ACTION_BET_BINS,
    LastAction,
    NextAction,
    make_action_from_encoded,
    make_last_actions,
    make_next_actions,
)
from pokermon.data.context import (
    PrivateContext,
    PublicContext,
    make_private_context,
    make_public_context,
)
from pokermon.data.examples import make_example
from pokermon.data.player_state import PlayerState, make_player_states
from pokermon.data.public_state import PublicState, make_public_states
from pokermon.data.rewards import Reward, make_rewards
from pokermon.model import features, utils
from pokermon.model.features import FeatureConfig, FeatureTensors, TargetTensors
from pokermon.model.utils import select_proportionally
from pokermon.poker.cards import Board, HoleCards
from pokermon.poker.game import Action, GameView, Street
from pokermon.poker.result import Result


def policy_vector_size():
    return NUM_ACTION_BET_BINS + 2


class HeadsUpModel(Policy):
    def __init__(
        self,
        name,
    ):
        super().__init__()

        self.name = name
        self.num_players = 2

        context_features = {}
        context_features.update(
            features.make_feature_definition_dict(PublicContext, is_sequence=False)
        )
        context_features.update(
            features.make_feature_definition_dict(PrivateContext, is_sequence=False)
        )

        sequence_features = {}
        sequence_features.update(
            features.make_feature_definition_dict(PlayerState, is_sequence=True)
        )
        sequence_features.update(
            features.make_feature_definition_dict(PublicState, is_sequence=True)
        )
        sequence_features.update(
            features.make_feature_definition_dict(LastAction, is_sequence=True)
        )

        context_targets = {}

        sequence_targets = {}
        sequence_targets.update(
            features.make_feature_definition_dict(NextAction, is_sequence=True)
        )
        sequence_targets.update(
            features.make_feature_definition_dict(Reward, is_sequence=True)
        )

        self.feature_config = FeatureConfig(
            context_features=context_features,
            sequence_features=sequence_features,
            context_targets=context_targets,
            sequence_targets=sequence_targets,
        )

        self.model = tf.keras.Sequential(name=name)
        self.model.add(
            tf.keras.layers.LSTM(
                input_dim=self.num_features(), return_sequences=True, units=32
            )
        )
        self.model.add(tf.keras.layers.Dense(64, name="hidden"))
        self.model.add(tf.keras.layers.Dense(policy_vector_size(), name="logits"))

        self.optimizer = None

    def checkpoint(self):
        return tf.train.Checkpoint(
            step=tf.Variable(1), optimizer=self.optimizer, model=self.model
        )

    def checkpoint_manager(self, path):
        if getattr(self, "manager", None) is None:
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

        example: tf.train.SequenceExample = self.make_forward_example(
            player_index, game, hole_cards, board
        )

        feature_tensors = self.feature_config.make_feature_tensors(
            example.SerializeToString()
        )
        # Create the action probabilities at the last timestep
        action_probs: np.Array = self.action_probs(feature_tensors)[0, -1, :].numpy()
        action_index = select_proportionally(action_probs)
        return make_action_from_encoded(action_index=action_index, game=game)

    def num_features(self):
        return self.feature_config.num_features(self.num_players)

    def make_forward_example(
        self, player_index: int, game: GameView, hole_cards: HoleCards, board: Board
    ) -> tf.train.SequenceExample:
        """
        All tensors have shape:
        [batch_size=1, time, 1 OR num_players=2]
        """

        assert game.num_players() == self.num_players

        return make_example(
            public_context=make_public_context(game),
            private_context=make_private_context(hole_cards),
            public_states=make_public_states(game, board=board),
            player_states=make_player_states(player_index, game, hole_cards, board),
            last_actions=make_last_actions(game),
        )

    def make_forward_backward_example(
        self,
        player_index: int,
        game: GameView,
        hole_cards: HoleCards,
        board: Board,
        result: Result,
    ) -> tf.train.SequenceExample:
        """
        All tensors have shape:
        [batch_size=1, time, 1 OR num_players=2]
        """

        assert game.num_players() == self.num_players
        assert game.street() == Street.HAND_OVER

        return make_example(
            public_context=make_public_context(game),
            private_context=make_private_context(hole_cards),
            public_states=make_public_states(game, board=board),
            player_states=make_player_states(player_index, game, hole_cards, board),
            last_actions=make_last_actions(game),
            next_actions=make_next_actions(game),
            rewards=make_rewards(game, result),
        )

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
            tf.equal(feature_tensors["player_state__is_current_player"], 1), -1
        )

        return tf.where(
            player_mask,
            -1 * tf.squeeze(reward, -1) * cross_entropy,
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

        example = self.make_forward_backward_example(
            player_id, game, hole_cards, board, result
        )

        _, loss = self._update_weights(
            tf.convert_to_tensor(example.SerializeToString())
        )

        return example, loss

    @tf.function(experimental_relax_shapes=True)
    def _update_weights(self, serialized_example):

        with tf.GradientTape() as tape:
            (
                feature_tensors,
                target_tensors,
            ) = self.feature_config.make_features_and_target_tensors(serialized_example)

            loss_value = tf.reduce_mean(self.loss(feature_tensors, target_tensors))

            gradients = tape.gradient(loss_value, self.model.trainable_variables)
            self.optimizer.apply_gradients(
                zip(gradients, self.model.trainable_variables)
            )

        return gradients, loss_value
