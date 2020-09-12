import dataclasses
from typing import Dict
import tensorflow as tf
import typing
from typing import List

from pokermon.data.utils import feature_name


def make_feature_config(clazz, is_sequence=False) -> Dict[str, tf.train.Feature]:
    feature_map = {}

    if is_sequence:
      fixed_len_feature = tf.io.FixedLenSequenceFeature
    else:
        fixed_len_feature = tf.io.FixedLenFeature

    for field in dataclasses.fields(clazz):

        name = feature_name(clazz, field)
        field_type = field.type

        if typing.get_origin(field_type) == typing.Union:
            first_type, second_type = typing.get_args(field_type)
            if second_type != type(None):  # noqa: E721
                raise Exception()
            field_type = first_type

        if field_type == List[int]:
            feature_map[name] = tf.io.VarLenFeature(tf.int64)
        elif field_type == List[float]:
            feature_map[name] = tf.io.VarLenFeature(tf.float32)
        elif field_type == int:
            feature_map[name] = fixed_len_feature([], tf.int64)
        elif field_type == float:
            feature_map[name] = fixed_len_feature([], tf.float32)
        elif field_type == bool:
            feature_map[name] = fixed_len_feature([], tf.int64)
        else:
            raise Exception("Unexpected type %s", field.type)

    return feature_map


def make_fixed_player_context_tensor(context_val_map):
    sequence_tensors = []

    for name, val in context_val_map.items():
        if val.shape == []:
            val = tf.expand_dims(val, 0)
        sequence_tensors.append(val)

    return tf.concat(sequence_tensors, axis=0)


def make_fixed_player_sequence_tensor(sequence_val_map):
    sequence_tensors = []

    for name, val in sequence_val_map.items():
        if len(val.shape) == 1:
            val = tf.expand_dims(val, -1)
        sequence_tensors.append(val)

    return tf.concat(sequence_tensors, axis=-1)