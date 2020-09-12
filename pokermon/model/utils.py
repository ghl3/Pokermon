import math
import numpy as np
import tensorflow as tf

from pokermon.poker.game import GameView, Action


def make_action(action_index: int, game: GameView, num_bet_bins: int) -> Action:
    # 0 = Fold
    # 1 = Call
    # 2 = Min Raise (+ 0 * delta)
    # 3 = Raise Min + 1*delta
    # 4 = Raise Min + 2*delta
    # 5 = Raise Min + 3*delta
    # 6 = Raise Min + 4*delta
    # 7 = Raise Min + 5*delta = ALL IN

    if action_index == 0:
        return game.fold()
    elif action_index == 1:
        return game.call()
    elif action_index == 2:
        return game.min_raise()
    elif action_index == num_bet_bins + 2:
        return game.go_all_in()
    else:
        min_raise = game.min_bet_amount()
        remaining_stack = game.current_stack_sizes()[game.current_player()]
        delta = (remaining_stack - min_raise) / num_bet_bins
        num_deltas = (action_index - 2)
        raise_amount = int(math.floor(num_deltas * delta))
        return game.bet_raise(raise_amount=raise_amount)


def select_proportionally(policy_probabilities: np.array) -> int:
    return np.random.choice(len(policy_probabilities), size=1, p=policy_probabilities)[0]


def ensure_dense(t):
    if isinstance(t, tf.sparse.SparseTensor):
        return tf.sparse.to_dense(t)
    else:
        return t


def make_fixed_player_context_tensor(context_val_map):
    sequence_tensors = []

    for name, val in context_val_map.items():
        val = ensure_dense(val)
        val = tf.cast(val,  dtype=tf.float32)
        if val.shape == []:
            val = tf.expand_dims(val, 0)
        sequence_tensors.append(val)

    return tf.expand_dims(tf.concat(sequence_tensors, axis=0), 0)


def make_fixed_player_sequence_tensor(sequence_val_map):
    sequence_tensors = []

    for name, val in sequence_val_map.items():
        val = ensure_dense(val)
        val = tf.cast(val,  dtype=tf.float32)
        if len(val.shape) == 1:
            val = tf.expand_dims(val, -1)
        sequence_tensors.append(val)

    # Concatenate the tensors, add a dummy batch dimension
    return tf.expand_dims(tf.concat(sequence_tensors, axis=-1), 0)
