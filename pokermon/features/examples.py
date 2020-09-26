import dataclasses
import typing
from collections import OrderedDict, defaultdict
from typing import Any, Dict, List, Optional

import tensorflow as tf  # type: ignore

from pokermon.features.action import (
    LastAction,
    NextAction,
    make_last_actions,
    make_next_actions,
)
from pokermon.features.context import (
    PrivateContext,
    PublicContext,
    make_private_context,
    make_public_context,
)
from pokermon.features.player_state import PlayerState, make_player_states
from pokermon.features.public_state import PublicState, make_public_states
from pokermon.features.rewards import Reward, make_rewards
from pokermon.features.target import Target
from pokermon.features.utils import field_feature_name
from pokermon.poker.board import Board
from pokermon.poker.game import GameView, Street
from pokermon.poker.hands import HoleCards
from pokermon.poker.result import Result


def make_forward_example(
    player_index: int, game: GameView, hole_cards: HoleCards, board: Board
) -> tf.train.SequenceExample:
    return make_example(
        public_context=make_public_context(game),
        private_context=make_private_context(hole_cards),
        public_states=make_public_states(game, board=board),
        player_states=make_player_states(player_index, game, hole_cards, board),
        last_actions=make_last_actions(game),
    )


def make_forward_backward_example(
    player_index: int,
    game: GameView,
    hole_cards: HoleCards,
    board: Board,
    result: Result,
) -> tf.train.SequenceExample:
    """
    All tensors have shape:
    [batch_size=1, time, 1 OR num_players=2]
    """

    # assert game.num_players() == self.num_players
    assert game.street() == Street.HAND_OVER

    return make_example(
        public_context=make_public_context(game),
        private_context=make_private_context(hole_cards),
        public_states=make_public_states(game, board=board),
        player_states=make_player_states(player_index, game, hole_cards, board),
        last_actions=make_last_actions(game),
        next_actions=make_next_actions(game),
        rewards=make_rewards(game, result),
    )


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

    feature_map["context"] = dict(sorted(feature_map["context"].items()))
    feature_map["features"] = dict(sorted(feature_map["features"].items()))

    return feature_map


def _make_feature_map(clazz, val: Any, default_val=-1) -> Dict[str, tf.train.Feature]:
    feature_map = {}

    val_map = dataclasses.asdict(val)

    for field in dataclasses.fields(clazz):

        name = field_feature_name(clazz, field)

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
    player_states: Optional[List[PlayerState]] = None,
    last_actions: Optional[List[LastAction]] = None,
    next_actions: Optional[List[NextAction]] = None,
    rewards: Optional[List[Reward]] = None,
) -> tf.train.SequenceExample:

    context_features: Dict[str, tf.train.Feature] = OrderedDict()

    # First, make any context features, if necessary
    if public_context:
        context_features.update(_make_feature_map(PublicContext, public_context))

    if private_context:
        context_features.update(_make_feature_map(PrivateContext, private_context))

    if target:
        context_features.update(_make_feature_map(Target, target))

    timestamp_features: Dict[str, List[tf.train.Feature]] = defaultdict(list)

    if public_states:
        for public_state in public_states:
            for k, v in _make_feature_map(PublicState, public_state).items():
                timestamp_features[k].append(v)

    if player_states:
        for player_state in player_states:
            for k, v in _make_feature_map(PlayerState, player_state).items():
                timestamp_features[k].append(v)

    if last_actions:
        for last_action in last_actions:
            for k, v in _make_feature_map(LastAction, last_action).items():
                timestamp_features[k].append(v)

    if next_actions:
        for next_action in next_actions:
            for k, v in _make_feature_map(NextAction, next_action).items():
                timestamp_features[k].append(v)

    if rewards:
        for reward in rewards:
            for k, v in _make_feature_map(Reward, reward).items():
                timestamp_features[k].append(v)

    num_steps = None
    for name, feature_list in timestamp_features.items():
        if num_steps is None:
            num_steps = len(feature_list)
        elif len(feature_list) != num_steps:
            raise Exception(f"Invalid number of features for {name}")

    context_features["num_steps"] = _int64_feature([num_steps or 0])

    seq_ex = tf.train.SequenceExample(
        context=tf.train.Features(feature=context_features)
    )

    for feature_name, feature_list in timestamp_features.items():
        for feature in feature_list:
            seq_ex.feature_lists.feature_list[feature_name].feature.append(feature)

    return seq_ex
