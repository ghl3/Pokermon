from typing import Dict

import tensorflow as tf

from pokermon.data import features
from pokermon.data.action import make_last_actions, LastAction
from pokermon.data.context import make_public_context, make_private_context
from pokermon.data.examples import make_example
from pokermon.data.state import make_public_states, make_private_states, PublicState, PrivateState
from pokermon.model import utils
from pokermon.model.action_policy_model import ActionPolicyModel, policy_vector_size
from pokermon.poker.cards import HoleCards, Board
from pokermon.poker.game import GameView


class HeadsUpModel(ActionPolicyModel):
    def __init__(self, name, player_id, ):
        super().__init__(player_id=player_id)

        self.num_players = 2
        self.player_id = player_id

        self.context_feature_columns = {}

        self.sequence_feature_columns = {}
        self.sequence_feature_columns.update(
            features.make_feature_config(PublicState, is_sequence=True))
        self.sequence_feature_columns.update(
            features.make_feature_config(PrivateState, is_sequence=True))
        self.sequence_feature_columns.update(
            features.make_feature_config(LastAction, is_sequence=True))

        self.model = tf.keras.Sequential(name=name)
        self.model.add(tf.keras.layers.LSTM(input_dim=self.num_features(), return_sequences=True,
                                            units=32))
        self.model.add(tf.keras.layers.Dense(64))
        self.model.add(tf.keras.layers.Dense(policy_vector_size()))

    def num_features(self):

        num = 0

        for _, feature_col in self.sequence_feature_columns.items():
            if isinstance(feature_col, tf.io.FixedLenSequenceFeature):
                num += 1
            elif isinstance(feature_col, tf.io.VarLenFeature):
                num += self.num_players
            else:
                raise Exception()
        return num

    def get_tensor_dict(self, game: GameView, hole_cards: HoleCards, board: Board) -> Dict[
        str, tf.Tensor]:

        assert game.num_players() == self.num_players

        example = make_example(
            public_context=make_public_context(game),
            private_context=make_private_context(hole_cards),
            public_states=make_public_states(game, board=board),
            private_states=make_private_states(game, board=board),
            last_actions=make_last_actions(game),
        )

        context_dict, sequence_dict = tf.io.parse_single_sequence_example(
            example.SerializeToString(), context_features=self.context_feature_columns,
            sequence_features=self.sequence_feature_columns, example_name=None,
            name=None
        )

        tensor_dict: Dict[str, tf.Tensor] = {}
        tensor_dict.update(context_dict)
        tensor_dict.update(sequence_dict)
        return tensor_dict

    def make_features(self, tensor_dict: Dict[str, tf.Tensor]):
        return utils.make_fixed_player_sequence_tensor(tensor_dict)

    def make_logits(self, tensor_dict: Dict[str, tf.Tensor]):
        return self.model(self.make_features(tensor_dict))

    def generate_policy(self, game: GameView, hole_cards: HoleCards, board: Board) -> tf.Tensor:

        assert game.num_players() == self.num_players

        example = make_example(
            public_context=make_public_context(game),
            private_context=make_private_context(hole_cards),
            public_states=make_public_states(game, board=board),
            private_states=make_private_states(game, board=board),
            last_actions=make_last_actions(game),
        )

        _, sequence_vals = tf.io.parse_single_sequence_example(
            example.SerializeToString(), context_features=self.context_feature_columns,
            sequence_features=self.sequence_feature_columns, example_name=None,
            name=None
        )

        sequence_tensor = utils.make_fixed_player_sequence_tensor(sequence_vals)

        policy_per_timestamp = self.model(sequence_tensor)

        # Pick the last
        return policy_per_timestamp[0, -1, :]

    def reenforce_loss(self, tensor_dict):

        # [batch, time]
        next_actions = tensor_dict['next_action__action_encoded']
        next_actions_one_hot = tf.one_hot(next_actions, depth=policy_vector_size(), axis=-1)
        policy_logits = self.make_logits(tensor_dict)
        reward = tensor_dict['reward__cumulative_reward']

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
        return -1 * reward * tf.nn.softmax_cross_entropy_with_logits(
            labels=next_actions_one_hot, logits=policy_logits)
