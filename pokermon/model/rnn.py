import tensorflow as tf
from tensorflow.python.keras.feature_column import sequence_feature_column as ksfc

from pokermon.data.action import NUM_ACTION_BET_BINS
from pokermon.model.context_sequence_concat import ContextSequenceConcat
from pokermon.model.feature_config import FeatureConfig


def policy_vector_size():
    return NUM_ACTION_BET_BINS + 2


def make_model(feature_config: FeatureConfig):

    ctx_inputs, seq_inputs = feature_config.make_model_input_configs()
    x = tf.keras.layers.DenseFeatures(feature_config.context_features)(ctx_inputs)
    y, _ = ksfc.SequenceFeatures(feature_config.sequence_features)(seq_inputs)
    z = ContextSequenceConcat()((x, y))
    z = tf.keras.layers.LSTM(units=32, return_sequences=True)(z)
    z = tf.keras.layers.Dense(64)(z)
    z = tf.keras.layers.Dense(policy_vector_size(), name="logits")(z)

    all_inputs = list(ctx_inputs.values()) + list(seq_inputs.values())
    return tf.keras.Model(inputs=all_inputs, outputs=z)
