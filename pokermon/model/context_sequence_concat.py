from typing import Tuple

import tensorflow as tf  # type: ignore

from tensorflow.python.feature_column import sequence_feature_column as sfc  # type: ignore # isort:skip


class ContextSequenceConcat(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super(ContextSequenceConcat, self).__init__(**kwargs)

    def build(self, input_shape):
        pass

    def call(self, tensors: Tuple[tf.Tensor, tf.Tensor], **kwargs):
        ctx, seq = tensors
        return sfc.concatenate_context_input(
            tf.cast(ctx, tf.float32), tf.cast(seq, tf.float32)
        )

    def compute_output_shape(self, input_shape):
        ctx_shape, seq_shape = input_shape
        num_context_features = ctx_shape[-1]
        num_seq_features = seq_shape[-1]

        return tuple(num_seq_features[:-1]) + (num_context_features + num_seq_features,)
