import dataclasses
import typing
from collections import OrderedDict, defaultdict
from typing import Any, Dict, List, Optional

import tensorflow as tf  # type: ignore

from pokermon.data.action import LastAction, NextAction
from pokermon.data.context import PrivateContext, PublicContext
from pokermon.data.rewards import Reward
from pokermon.data.state import PrivateState, PublicState
from pokermon.data.target import Target
from pokermon.data.utils import feature_name


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


def _make_feature_map(clazz, val: Any, default_val=-1) -> Dict[str, tf.train.Feature]:
    feature_map = {}

    val_map = dataclasses.asdict(val)

    for field in dataclasses.fields(clazz):

        name = feature_name(clazz, field)

        val = val_map[field.name]
        field_type = field.type

        if typing.get_origin(field_type) == typing.Union:
            first_type, second_type = typing.get_args(field_type)
            if second_type != type(None):  # noqa: E721
                raise Exception()
            field_type = first_type
            if val is None:
                val = default_val

        if field_type == List[int]:
            feature_map[name] = _int64_feature(val)
        elif field_type == List[float]:
            feature_map[name] = _float_feature(val)
        elif field_type == int:
            feature_map[name] = _int64_feature([val])
        elif field_type == float:
            feature_map[name] = _float_feature([val])
        elif field_type == bool:
            feature_map[name] = _int64_feature([int(val)])
        else:
            raise Exception("Unexpected type %s", field.type)

    return feature_map


def with_prefix(prefix, d):
    return {f"{prefix}__{k}": v for k, v in d.items()}


# dataclass to Dict of Features tf.Example


def zip_or_none(*lists_or_none):
    length = None

    for lst in lists_or_none:
        if lst is not None and length is None:
            length = len(lst)
        if lst is not None:
            if len(lst) != length:
                raise Exception()

    if length is None:
        raise Exception()

    for i in range(length):
        yield tuple(lst[i] if lst else None for lst in lists_or_none)


def make_example(
    public_context: Optional[PublicContext] = None,
    private_context: Optional[PrivateContext] = None,
    target: Optional[Target] = None,
    public_states: Optional[List[PublicState]] = None,
    private_states: Optional[List[PrivateState]] = None,
    last_actions: Optional[List[LastAction]] = None,
    next_actions: Optional[List[NextAction]] = None,
    rewards: Optional[List[Reward]] = None,
) -> tf.train.SequenceExample:
    context_features: Dict[str, tf.train.Feature] = OrderedDict()

    # First, make any context features, if necessary
    if public_context:
        context_features.update(
            _make_feature_map(PublicContext, public_context)

        )

    if private_context:
        context_features.update(
            _make_feature_map(PrivateContext, private_context)

        )

    if target:
        context_features.update(
            _make_feature_map(Target, target)
        )

    timestamp_features: Dict[str, List[tf.train.Feature]] = defaultdict(list)

    if public_states:
        for public_state in public_states:
            for k, v in _make_feature_map(PublicState, public_state).items():
                timestamp_features[k].append(v)

    if private_states:
        for private_state in private_states:
            for k, v in _make_feature_map(PrivateState, private_state).items():
                timestamp_features[k].append(v)

    if last_actions:
        for action in last_actions:
            for k, v in _make_feature_map(LastAction, action).items():
                timestamp_features[k].append(v)

    if next_actions:
        for action in next_actions:
            for k, v in _make_feature_map(NextAction, action).items():
                timestamp_features[k].append(v)

    if rewards:
        for reward in rewards:
            for k, v in _make_feature_map(Reward, reward).items():
                timestamp_features[k].append(v)

    seq_ex = tf.train.SequenceExample(
        context=tf.train.Features(feature=context_features)
    )

    for feature_name, feature_list in timestamp_features.items():
        for feature in feature_list:
            seq_ex.feature_lists.feature_list[feature_name].feature.append(feature)

    return seq_ex
