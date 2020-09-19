import dataclasses
import typing
from itertools import chain
from typing import Dict, List

import tensorflow as tf  # type: ignore

from pokermon.data.utils import field_feature_name
from pokermon.model.utils import (
    make_sequence_dense,
    make_sequence_dense_from_context,
    make_sequence_dict_of_dense,
    make_sequence_dict_of_dense_from_context,
)

FeatureTensors = Dict[str, tf.Tensor]
TargetTensors = Dict[str, tf.Tensor]


def make_num_steps_features():
    return {"num_steps": tf.io.FixedLenFeature([], tf.int64)}


def make_feature_definition_dict(
    clazz, is_sequence=False
) -> Dict[str, tf.train.Feature]:
    feature_map = {}

    if is_sequence:
        fixed_len_feature = tf.io.FixedLenSequenceFeature
    else:
        fixed_len_feature = tf.io.FixedLenFeature

    for field in dataclasses.fields(clazz):

        name = field_feature_name(clazz, field)
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
            raise Exception(f"Unexpected type {field_type} on class {clazz}")

    return feature_map


@dataclasses.dataclass
class FeatureConfig:

    context_features: Dict[str, tf.train.Feature] = dataclasses.field(
        default_factory=dict
    )
    sequence_features: Dict[str, tf.train.Feature] = dataclasses.field(
        default_factory=dict
    )

    context_targets: Dict[str, tf.train.Feature] = dataclasses.field(
        default_factory=dict
    )
    sequence_targets: Dict[str, tf.train.Feature] = dataclasses.field(
        default_factory=dict
    )

    def num_features(self, num_players):
        num = 0

        for _, feature_col in chain(
            self.sequence_features.items(), self.context_features.items()
        ):
            if isinstance(feature_col, tf.io.FixedLenSequenceFeature):
                num += 1
            elif isinstance(feature_col, tf.io.FixedLenFeature):
                num += 1
            elif isinstance(feature_col, tf.io.VarLenFeature):
                num += num_players
            else:
                raise Exception()

        return num

    def make_feature_tensors(self, serialized_example: str) -> FeatureTensors:

        context_features = make_num_steps_features()
        context_features.update(self.context_features)

        sequence_features = {}
        sequence_features.update(self.sequence_features)

        context_dict, sequence_dict = tf.io.parse_single_sequence_example(
            serialized_example,
            context_features=context_features,
            sequence_features=sequence_features,
            example_name=None,
            name=None,
        )

        dense_features = {}
        dense_features.update(make_sequence_dict_of_dense(sequence_dict))
        dense_features.update(make_sequence_dict_of_dense_from_context(context_dict))

        return dense_features

    def make_features_and_target_tensors(
        self, serialized_example: str
    ) -> typing.Tuple[FeatureTensors, TargetTensors]:
        """
        All tensors have shape:
        [batch_size=1, time, 1 OR num_players=2]
        """

        context_features = make_num_steps_features()
        context_features.update(self.context_features)
        context_features.update(self.context_targets)

        sequence_features = {}
        sequence_features.update(self.sequence_features)
        sequence_features.update(self.sequence_targets)

        context_dict, sequence_dict = tf.io.parse_single_sequence_example(
            serialized_example,
            context_features=context_features,
            sequence_features=sequence_features,
            example_name=None,
            name=None,
        )

        num_steps = context_dict["num_steps"]

        feature_dict = {}
        target_dict = {}

        for (name, tensor) in sequence_dict.items():
            if name in self.sequence_features:
                feature_dict[name] = make_sequence_dense(tensor)
            elif name in self.sequence_targets:
                target_dict[name] = make_sequence_dense(tensor)
            else:
                raise Exception()

        for (name, tensor) in context_dict.items():
            if name == "num_steps":
                continue
            elif name in self.context_features:
                feature_dict[name] = make_sequence_dense_from_context(tensor, num_steps)
            elif name in self.sequence_targets:
                target_dict[name] = make_sequence_dense_from_context(tensor, num_steps)
            else:
                raise Exception()

        return feature_dict, target_dict
