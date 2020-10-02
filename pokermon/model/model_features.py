import tensorflow as tf  # type: ignore
from tensorflow.python.feature_column import feature_column_v2 as fc  # type: ignore
from tensorflow.python.feature_column import (
    sequence_feature_column as sfc,  # type: ignore
)

from pokermon.model.feature_config import FeatureConfig


def make_float(t):
    return tf.cast(t, tf.float32)


def make_feature_config(num_players):
    return FeatureConfig(
        context_features=[
            fc.numeric_column(
                "public_context__starting_stack_sizes",
                shape=num_players,
                dtype=tf.int64,
            ),
            fc.embedding_column(
                tf.feature_column.categorical_column_with_vocabulary_list(
                    "private_context__hand_encoded", range(1326)
                ),
                dimension=4,
            ),
        ],
        sequence_features=[
            fc.indicator_column(
                sfc.sequence_categorical_column_with_identity(
                    "last_action__action_encoded", 22
                )
            ),
            fc.indicator_column(
                sfc.sequence_categorical_column_with_identity("last_action__move", 5)
            ),
            sfc.sequence_numeric_column(
                "last_action__amount_added",
                dtype=tf.int64,
                default_value=-1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "last_action__amount_added_percent_of_remaining",
                dtype=tf.float32,
                default_value=-1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "last_action__amount_raised",
                dtype=tf.int64,
                default_value=-1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "last_action__amount_raised_percent_of_pot",
                dtype=tf.float32,
                default_value=-1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "public_state__all_in_player_mask",
                dtype=tf.int64,
                default_value=-1,
                shape=num_players,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "public_state__stack_sizes",
                dtype=tf.int64,
                default_value=-1,
                shape=num_players,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "public_state__amount_to_call",
                dtype=tf.int64,
                default_value=-1,
                shape=num_players,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "public_state__current_player_mask",
                dtype=tf.int64,
                default_value=-1,
                shape=num_players,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "public_state__min_raise_amount",
                dtype=tf.int64,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "public_state__pot_size",
                dtype=tf.int64,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "public_state__street",
                dtype=tf.int64,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "player_state__is_current_player",
                dtype=tf.int64,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "player_state__current_hand_rank",
                dtype=tf.int64,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "player_state__current_hand_strength",
                dtype=tf.float32,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
            fc.indicator_column(
                sfc.sequence_categorical_column_with_identity(
                    "player_state__current_hand_type", 9
                )
            ),
            sfc.sequence_numeric_column(
                "player_state__current_player_offset",
                dtype=tf.int64,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "player_state__win_prob_vs_any",
                dtype=tf.float32,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "player_state__win_prob_vs_better",
                dtype=tf.float32,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "player_state__win_prob_vs_tied",
                dtype=tf.float32,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "player_state__win_prob_vs_worse",
                dtype=tf.float32,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "player_state__frac_hands_better",
                dtype=tf.float32,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "player_state__frac_hands_tied",
                dtype=tf.float32,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
            sfc.sequence_numeric_column(
                "player_state__frac_hands_worse",
                dtype=tf.float32,
                default_value=-1,
                shape=1,
                normalizer_fn=make_float,
            ),
        ],
        context_targets=[
            fc.numeric_column("public_context__num_players", shape=1, dtype=tf.int64),
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
