import dataclasses
from typing import Dict, List

import tensorflow as tf  # type: ignore
from tensorflow.python.feature_column import feature_column_v2 as fc
from tensorflow.python.feature_column.feature_column_v2 import FeatureColumn
from tensorflow.python.ops import parsing_ops

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
        for name, col in fc.make_parse_example_spec_v2(self.context_features).items():
            context_inputs[name] = tf.keras.Input(
                shape=(None,),
                sparse=False,
                name=name,
                dtype=col.dtype,
            )

        sequence_inputs = {}
        for name, col in fc.make_parse_example_spec_v2(self.sequence_features).items():
            sequence_inputs[name] = tf.keras.Input(
                shape=(None, None),
                sparse=True,
                name=name,
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
