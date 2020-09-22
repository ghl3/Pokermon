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


def ensure_all_dense(tensor_dict):
    return {k: ensure_dense(t) for k, t in tensor_dict.items()}
