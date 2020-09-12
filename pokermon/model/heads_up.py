import tensorflow as tf
import numpy as np

from pokermon.data import features
from pokermon.data.action import make_last_actions, LastAction
from pokermon.data.context import make_public_context, make_private_context
from pokermon.data.examples import make_example
from pokermon.data.state import make_public_states, make_private_states, PublicState, PrivateState
from pokermon.model import utils
from pokermon.model.action_policy_model import ActionPolicyModel
from pokermon.poker.cards import HoleCards, Board
from pokermon.poker.game import GameView


class HeadsUpModel(ActionPolicyModel):
    def __init__(self, name, player_id, num_bet_bins=20):
        super().__init__(player_id=player_id, num_bet_bins=num_bet_bins)

        self.num_players = 2
        self.player_id = player_id
        self.num_bet_bins = num_bet_bins

        self.context_feature_columns = {}

        self.sequence_feature_columns = {}
        self.sequence_feature_columns.update(
            features.make_feature_config(PublicState, is_sequence=True))
        self.sequence_feature_columns.update(
            features.make_feature_config(PrivateState, is_sequence=True))
        self.sequence_feature_columns.update(
            features.make_feature_config(LastAction, is_sequence=True))

        self.model = tf.keras.Sequential(name=name)
        self.model.add(tf.keras.layers.LSTM(input_dim=self.num_features(),  return_sequences=True,
                                            units=32))
        self.model.add(tf.keras.layers.Dense(64))
        self.model.add(tf.keras.layers.Dense(self.policy_vector_size()))
        self.model.add(tf.keras.layers.Softmax(axis=-1))

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

    def policy_vector_size(self):
        return self.num_bet_bins + 2

    def generate_policy(self, game: GameView, hole_cards: HoleCards, board: Board) -> np.array:

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
        return policy_per_timestamp[0, -1, :].numpy()
