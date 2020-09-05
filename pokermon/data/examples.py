import dataclasses
from collections import OrderedDict, defaultdict
from typing import Any, Dict, List

import tensorflow as tf  # type: ignore

from pokermon.data.reenforcement_types import Context, Row


def _bytes_feature(values: List[str]) -> tf.train.Feature:
    return tf.train.Feature(
        bytes_list=tf.train.BytesList(value=[bytes(v, "utf-8") for v in values])
    )


def _float_feature(values: List[float]) -> tf.train.Feature:
    return tf.train.Feature(float_list=tf.train.FloatList(value=values))


def _int64_feature(values: List[int]) -> tf.train.Feature:
    return tf.train.Feature(int64_list=tf.train.Int64List(value=values))


def _feature_value_to_vals(feature: tf.train.Feature):
    kind = feature.WhichOneof("kind")

    if kind == "int64_list":
        return list(feature.int64_list.value)
    elif kind == "float_list":
        return list(feature.float_list.value)
    elif kind == "bytes_list":
        return [str(v.decode("utf-8")) for v in feature.bytes_list.value]
    else:
        raise Exception()


def _features_to_dict(features: tf.train.Features):
    feature_map = {}

    for name, feature in features.feature.items():
        feature_map[name] = _feature_value_to_vals(feature)

    return feature_map


def seq_example_to_dict(example: tf.train.SequenceExample) -> Dict[str, Any]:
    feature_map = {
        "context": _features_to_dict(example.context),
        "features": defaultdict(lambda: list()),
    }

    for name, feature_list in example.feature_lists.feature_list.items():

        for feature in feature_list.feature:
            feature_map["features"][name].append(_feature_value_to_vals(feature))

    feature_map["features"] = dict(feature_map["features"])

    return feature_map


def _make_feature_map(clazz, val: Any) -> Dict[str, tf.train.Feature]:
    feature_map = {}

    val_map = dataclasses.asdict(val)

    for field in dataclasses.fields(clazz):

        name = field.name

        if field.type == List[int]:
            feature_map[name] = _int64_feature(val_map[name])
        elif field.type == List[float]:
            feature_map[name] = _float_feature(val_map[name])
        elif field.type == int:
            feature_map[name] = _int64_feature([val_map[name]])
        elif field.type == float:
            feature_map[name] = _float_feature([val_map[name]])
        elif field.type == bool:
            feature_map[name] = _int64_feature([int(val_map[name])])
        else:
            raise Exception("Unexpected type %s", field.type)

    return feature_map


def with_prefix(prefix, d):
    return {f"{prefix}__{k}": v for k, v in d.items()}


# dataclass to Dict of Features tf.Example


def make_example(context: Context, rows: List[Row]) -> tf.train.Example:
    # Map of feature name to repeated field of features
    feature_values: Dict[str, List[Any]] = defaultdict(lambda: list())

    # Convert to a row-form to a column-form
    for row in rows:
        feature_map: Dict[str, tf.train.Feature] = OrderedDict()
        feature_map.update(
            with_prefix("state", _make_feature_map(Row.State, row.state))
        )
        feature_map.update(
            with_prefix("action", _make_feature_map(Row.Action, row.action))
        )
        feature_map.update(
            with_prefix("reward", _make_feature_map(Row.Reward, row.reward))
        )

        for k, v in feature_map.items():
            feature_values[k].append(v)

    # TODO: Update to sequence example
    seq_ex = tf.train.SequenceExample(
        context=tf.train.Features(feature=_make_feature_map(Context, context))
    )

    for feature_name, feature_list in feature_values.items():
        for feature in feature_list:
            seq_ex.feature_lists.feature_list[feature_name].feature.append(feature)

    return seq_ex
