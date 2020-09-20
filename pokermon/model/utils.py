from typing import Dict

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


def context_tensor_to_sequence():
    pass


def make_sequence_dense(t: tf.Tensor):
    t = ensure_dense(t)
    if len(t.shape) == 1:
        t = tf.expand_dims(t, -1)
    return tf.expand_dims(t, 0)


def make_sequence_dict_of_dense(
    tensor_dict: Dict[str, tf.Tensor]
) -> Dict[str, tf.Tensor]:
    """
    All tensors have shape [time, 1 OR num_players]
    """
    updated_dict = {}

    for name, t in tensor_dict.items():
        updated_dict[name] = make_sequence_dense(t)

    #        t = ensure_dense(t)
    #        if len(t.shape) == 1:
    #            t = tf.expand_dims(t, -1)

    #        updated_dict[name] = tf.expand_dims(t, 0)

    return updated_dict


def make_context_dense(t: tf.Tensor):
    t = ensure_dense(t)
    if t.shape == []:
        t = tf.expand_dims(t, -1)
    return tf.expand_dims(t, 0)


def make_sequence_dense_from_context(t: tf.Tensor, num_steps: int):
    return tf.tile(tf.expand_dims(make_context_dense(t), 1), [1, num_steps, 1])


def make_context_dict_of_dense(
    tensor_dict: Dict[str, tf.Tensor]
) -> Dict[str, tf.Tensor]:
    """
    All tensors have shape [1 OR num_players]
    """
    updated_dict = {}

    for name, t in tensor_dict.items():
        updated_dict[name] = make_context_dense(t)
    #        t = ensure_dense(t)
    #        if t.shape == []:
    #            t = tf.expand_dims(t, 0)
    #
    #        updated_dict[name] = tf.expand_dims(t, 0)

    return updated_dict


def make_sequence_dict_of_dense_from_context(context_dict):
    num_steps = context_dict["num_steps"]

    d = {}

    for name, t in context_dict.items():
        if name == "num_steps":
            continue

        d[name] = make_sequence_dense_from_context(t, num_steps)

    return d


def concat_feature_tensors(tensor_dict):

    tensors = []

    for name, val in sorted(tensor_dict.items()):
        val = tf.cast(val, dtype=tf.float32)
        tensors.append(val)

    return tf.concat(tensors, axis=-1)
