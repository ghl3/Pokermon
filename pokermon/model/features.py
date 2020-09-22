import dataclasses
import typing
from typing import Dict, List
from tensorflow.python.ops import parsing_ops
from tensorflow.python.feature_column import feature_column_v2 as fc
from tensorflow.python.feature_column.feature_column_v2 import FeatureColumn

import tensorflow as tf  # type: ignore

from pokermon.data.utils import field_feature_name


FeatureTensors = Dict[str, tf.Tensor]
TargetTensors = Dict[str, tf.Tensor]


@dataclasses.dataclass
class FeatureConfig:

    # These are gathered for the forward pass
    context_features: List[FeatureColumn] = dataclasses.field(default_factory=list)

    # These are gathered for the forward pass
    # These should all be sparse...
    sequence_features: List[FeatureColumn] = dataclasses.field(default_factory=list)

    # These are only gathered in the backwards pass
    context_targets: List[FeatureColumn] = dataclasses.field(default_factory=list)

    sequence_targets: List[FeatureColumn] = dataclasses.field(default_factory=list)

    def make_model_input_configs(self):
        context_inputs = {}
        for col in self.context_features:
            context_inputs[col.name] = tf.keras.Input(
                shape=col.shape,
                sparse=False,
                name=col.name,
                dtype=col.dtype,
            )

        sequence_inputs = {}
        for col in self.sequence_features:
            sequence_inputs[col.name] = tf.keras.Input(
                shape=(None,) + col.shape,
                sparse=True,
                name=col.name,
                dtype=col.dtype,
            )

        return context_inputs, sequence_inputs

    def make_feature_tensors(self, serialized_examples_tensor):
        ctx, seq, _ = parsing_ops.parse_sequence_example(
            serialized_examples_tensor,
            context_features=fc.make_parse_example_spec_v2(self.context_features),
            sequence_features=fc.make_parse_example_spec_v2(self.sequence_features),
        )

        fs = {}
        fs.update(ctx)
        fs.update(seq)
        return fs

    def make_features_and_target_tensors(self, serialized_examples_tensor):

        context_features = fc.make_parse_example_spec_v2(self.context_features)
        context_targets = fc.make_parse_example_spec_v2(self.context_targets)
        context_data = {}
        context_data.update(context_features)
        context_data.update(context_targets)

        sequence_features = fc.make_parse_example_spec_v2(self.sequence_features)
        sequence_targets = fc.make_parse_example_spec_v2(self.sequence_targets)
        sequence_data = {}
        sequence_data.update(sequence_features)
        sequence_data.update(sequence_targets)

        ctx, seq, _ = parsing_ops.parse_sequence_example(
            serialized_examples_tensor,
            context_features=context_data,
            sequence_features=sequence_data,
        )

        fs = {}
        fs.update({name: t for name, t in ctx.items() if name in context_features})
        fs.update({name: t for name, t in seq.items() if name in sequence_features})

        ts = {}
        ts.update({name: t for name, t in ctx.items() if name in context_targets})
        ts.update({name: t for name, t in seq.items() if name in sequence_targets})

        return fs, ts

    # return ctx, seq

    # def num_features(self, num_players):
    #     num = 0
    #
    #     for _, feature_col in chain(
    #         self.sequence_features.items(), self.context_features.items()
    #     ):
    #         if isinstance(feature_col, tf.io.FixedLenSequenceFeature):
    #             num += 1
    #         elif isinstance(feature_col, tf.io.FixedLenFeature):
    #             num += 1
    #         elif isinstance(feature_col, tf.io.VarLenFeature):
    #             num += num_players
    #         else:
    #             raise Exception()
    #
    #     return num

    # def make_feature_tensors(self, serialized_example: str) -> FeatureTensors:
    #
    #     context_features = make_num_steps_features()
    #     context_features.update(self.context_features)
    #
    #     sequence_features = {}
    #     sequence_features.update(self.sequence_features)
    #
    #     context_dict, sequence_dict = tf.io.parse_single_sequence_example(
    #         serialized_example,
    #         context_features=context_features,
    #         sequence_features=sequence_features,
    #         example_name=None,
    #         name=None,
    #     )
    #
    #     dense_features = {}
    #     dense_features.update(make_sequence_dict_of_dense(sequence_dict))
    #     dense_features.update(make_sequence_dict_of_dense_from_context(context_dict))
    #
    #     return dense_features

    # def make_features_and_target_tensors(
    #     self, serialized_example: str
    # ) -> typing.Tuple[FeatureTensors, TargetTensors]:
    #     """
    #     All tensors have shape:
    #     [batch_size=1, time, 1 OR num_players=2]
    #     """
    #
    #     context_features = make_num_steps_features()
    #     context_features.update(self.context_features)
    #     context_features.update(self.context_targets)
    #
    #     sequence_features = {}
    #     sequence_features.update(self.sequence_features)
    #     sequence_features.update(self.sequence_targets)
    #
    #     context_dict, sequence_dict = tf.io.parse_single_sequence_example(
    #         serialized_example,
    #         context_features=context_features,
    #         sequence_features=sequence_features,
    #         example_name=None,
    #         name=None,
    #     )
    #
    #     num_steps = context_dict["num_steps"]
    #
    #     feature_dict = {}
    #     target_dict = {}
    #
    #     for (name, tensor) in sequence_dict.items():
    #         if name in self.sequence_features:
    #             feature_dict[name] = make_sequence_dense(tensor)
    #         elif name in self.sequence_targets:
    #             target_dict[name] = make_sequence_dense(tensor)
    #         else:
    #             raise Exception()
    #
    #     for (name, tensor) in context_dict.items():
    #         if name == "num_steps":
    #             continue
    #         elif name in self.context_features:
    #             feature_dict[name] = make_sequence_dense_from_context(tensor, num_steps)
    #         elif name in self.sequence_targets:
    #             target_dict[name] = make_sequence_dense_from_context(tensor, num_steps)
    #         else:
    #             raise Exception()
    #
    #     return feature_dict, target_dict


# def make_num_steps_features():
#    return {"num_steps": tf.io.FixedLenFeature([], tf.int64)}


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
