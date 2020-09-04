import dataclasses
from collections import defaultdict
from typing import Any, Dict, List

import tensorflow as tf  # type: ignore

from pokermon.data.features import Row


def _bytes_feature(values: List[str]) -> tf.train.Feature:
    return tf.train.Feature(
        bytes_list=tf.train.BytesList(value=[bytes(v, 'utf-8') for v in values]))


def _float_feature(values: List[float]) -> tf.train.Feature:
    return tf.train.Feature(float_list=tf.train.FloatList(value=values))


def _int64_feature(values: List[int]) -> tf.train.Feature:
    return tf.train.Feature(int64_list=tf.train.Int64List(value=values))


def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


def example_to_dict(example: tf.train.Example) -> Dict[str, Any]:
    feature_map = {}

    for name, feature in example.features.feature.items():

        kind = feature.WhichOneof("kind")

        if kind == 'int64_list':
            feature_map[name] = list(feature.int64_list.value)
        elif kind == 'float_list':
            feature_map[name] = list(feature.float_list.value)
        elif kind == 'bytes_list':
            feature_map[name] = [str(v.decode("utf-8")) for v in feature.bytes_list.value]
        else:
            raise Exception()

    return feature_map


def _make_feature_map(clazz, val_map: Dict[str, Any]) -> Dict[str, tf.train.Feature]:
    feature_map = {}

    for field in dataclasses.fields(clazz):

        name = field.name

        if field.type == List[int]:
            feature_map[name] = _int64_feature(flatten(val_map[name]))
        elif field.type == List[float]:
            feature_map[name] = _float_feature(flatten(val_map[name]))
        elif field.type == int:
            feature_map[name] = _int64_feature(val_map[name])
        elif field.type == float:
            feature_map[name] = _float_feature(val_map[name])
        elif field.type == bool:
            feature_map[name] = _int64_feature([int(x) for x in val_map[name]])
        else:
            raise Exception("Unexpected type %s", field.type)

    return feature_map


def make_example(rows: List[Row]) -> tf.train.Example:
    # example: tf.train.Example = tf.train.Example()

    feature_values: Dict[str, List[Any]] = defaultdict(lambda: list())

    for row in rows:
        for k, v in dataclasses.asdict(row).items():
            feature_values[k].append(v)

    feature_map = _make_feature_map(Row, feature_values)

    # Create a Features message using tf.train.Example.

    # TODO: Update to sequence example
    return tf.train.Example(features=tf.train.Features(feature=feature_map))
