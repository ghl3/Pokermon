import numpy as np
import tensorflow as tf


def select_proportionally(policy_probabilities: np.array) -> int:
    return np.random.choice(len(policy_probabilities), size=1, p=policy_probabilities)[
        0
    ]


def ensure_dense(t):
    if isinstance(t, tf.sparse.SparseTensor):
        return tf.sparse.to_dense(t)
    else:
        return t


def make_fixed_player_context_tensor(context_val_map):
    sequence_tensors = []

    for name, val in context_val_map.items():
        val = ensure_dense(val)
        val = tf.cast(val, dtype=tf.float32)
        if val.shape == []:
            val = tf.expand_dims(val, 0)
        sequence_tensors.append(val)

    return tf.expand_dims(tf.concat(sequence_tensors, axis=0), 0)


def make_fixed_player_sequence_tensor(sequence_val_map):
    sequence_tensors = []

    for name, val in sequence_val_map.items():
        val = ensure_dense(val)
        val = tf.cast(val, dtype=tf.float32)
        if len(val.shape) == 1:
            val = tf.expand_dims(val, -1)
        sequence_tensors.append(val)

    # Concatenate the tensors, add a dummy batch dimension
    return tf.expand_dims(tf.concat(sequence_tensors, axis=-1), 0)
