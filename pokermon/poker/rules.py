import logging
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from pokermon.poker.evaluation import EvaluationResult
from pokermon.poker.game import (
    BIG_BLIND_AMOUNT,
    SMALL_BLIND_AMOUNT,
    Action,
    GameView,
    Move,
)

logger = logging.getLogger(__name__)


class Error(Enum):
    UNKNOWN_MOVE = 1
    SMALL_BLIND_REQUIRED = 2
    BIG_BLIND_REQUIRED = 3
    INVALID_AMOUNT_ADDED = 4
    INVAID_TOTAL_BET = 5
    INVALID_PLAYER = 6
    MIN_RAISE_REQUIRED = 7
    WRONG_PLAYER = 8
    INVALID_MOVE = 9


class Metadata(Enum):
    TYPE = 1
    BLIND_AMOUNT = 2
    AMOUNT_ADDED_SHOULD_BE = 3
    AMOUNT_ADDED_SHOULD_BE_GE = 4
    AMOUNT_ADDED_SHOULD_BE_LE = 5
    TOTAL_BET_SHOULD_BE = 6
    MIN_BET_RAISE_AMOUNT = 7
    RAISE_MUST_BE_GE = 8
    CURRENT_PLAYER_SHOULD_BE = 9
    ALLOWED_MOVES_ARE = 10


@dataclass
class ValidationResult:
    error: Optional[Error]

    metadata: Dict[Metadata, Any]

    def is_valid(self):
        return self.error is None


MOVE_OK = ValidationResult(None, {})


def min_bet_amount(game: GameView) -> int:
    """The minimim amount that can be raised above the last bet"""
    return max(BIG_BLIND_AMOUNT, game.last_raise_amount())


def action_valid(
    action_index: int, player_index: int, action: Action, game: GameView
) -> ValidationResult:
    if action.total_bet < 0:
        raise Exception()

    elif action.amount_added < 0:
        raise Exception()

    elif action_index == 0:
        if action.move != Move.SMALL_BLIND:
            return ValidationResult(
                Error.SMALL_BLIND_REQUIRED, {Metadata.BLIND_AMOUNT: SMALL_BLIND_AMOUNT}
            )
        if action.amount_added != SMALL_BLIND_AMOUNT:
            return ValidationResult(
                Error.INVALID_AMOUNT_ADDED, {Metadata.BLIND_AMOUNT: SMALL_BLIND_AMOUNT}
            )
        if action.total_bet != SMALL_BLIND_AMOUNT:
            return ValidationResult(
                Error.INVAID_TOTAL_BET, {Metadata.BLIND_AMOUNT: SMALL_BLIND_AMOUNT}
            )
        return MOVE_OK

    elif action_index == 1:
        if action.move != Move.BIG_BLIND:
            return ValidationResult(
                Error.BIG_BLIND_REQUIRED, {Metadata.BLIND_AMOUNT: BIG_BLIND_AMOUNT}
            )
        if action.amount_added != BIG_BLIND_AMOUNT:
            return ValidationResult(
                Error.INVALID_AMOUNT_ADDED, {Metadata.BLIND_AMOUNT: BIG_BLIND_AMOUNT}
            )
        if action.total_bet != BIG_BLIND_AMOUNT:
            return ValidationResult(
                Error.INVAID_TOTAL_BET, {Metadata.BLIND_AMOUNT: BIG_BLIND_AMOUNT}
            )
        return MOVE_OK

    else:
        if player_index != game.current_player():
            return ValidationResult(
                Error.WRONG_PLAYER,
                {Metadata.CURRENT_PLAYER_SHOULD_BE: game.current_player()},
            )
        else:

            return voluntary_action_allowed(action, game)


def voluntary_action_allowed(action: Action, game: GameView) -> ValidationResult:
    """
    Assumes that the right player is making the given action
    """

    if action.move == Move.SMALL_BLIND or action.move == Move.BIG_BLIND:
        raise Exception()

    elif action.move == Move.FOLD:
        return _validate_fold(action, game)

    elif action.move == Move.CHECK_CALL:
        return _validate_check_call(action, game)

    elif action.move == Move.BET_RAISE:
        return _validate_bet_raise(action, game)

    else:
        return ValidationResult(Error.UNKNOWN_MOVE, {})


def _validate_fold(action: Action, game: GameView) -> ValidationResult:
    if action.amount_added != 0:
        return ValidationResult(
            Error.INVALID_AMOUNT_ADDED, {Metadata.AMOUNT_ADDED_SHOULD_BE: 0}
        )
    if action.total_bet != game.current_bet_amount():
        return ValidationResult(
            Error.INVALID_AMOUNT_ADDED,
            {Metadata.TOTAL_BET_SHOULD_BE: game.current_bet_amount()},
        )
    return MOVE_OK


def _validate_check_call(action: Action, game: GameView) -> ValidationResult:
    amount_to_call = game.amount_to_call()[game.current_player()]
    player_stack = game.current_stack_sizes()[game.current_player()]

    if amount_to_call <= player_stack:

        if action.amount_added != amount_to_call:
            return ValidationResult(
                Error.INVALID_AMOUNT_ADDED,
                {Metadata.AMOUNT_ADDED_SHOULD_BE: amount_to_call},
            )

        if action.total_bet != game.current_bet_amount():
            return ValidationResult(
                Error.INVAID_TOTAL_BET,
                {Metadata.TOTAL_BET_SHOULD_BE: game.current_bet_amount()},
            )

        return MOVE_OK

    else:
        # Player calls all in

        if action.amount_added != player_stack:
            return ValidationResult(
                Error.INVALID_AMOUNT_ADDED,
                {Metadata.AMOUNT_ADDED_SHOULD_BE: player_stack},
            )

        if action.total_bet != game.current_bet_amount():
            return ValidationResult(
                Error.INVAID_TOTAL_BET,
                {Metadata.TOTAL_BET_SHOULD_BE: game.current_bet_amount()},
            )

        return MOVE_OK


def _validate_bet_raise(action: Action, game: GameView) -> ValidationResult:
    amount_to_call = game.amount_to_call()[game.current_player()]
    player_stack = game.current_stack_sizes()[game.current_player()]
    amount_already_added = game.amount_added_in_street()[game.current_player()]

    # This should be a CALL, not a BET/RAISE
    if action.amount_added <= amount_to_call:
        return ValidationResult(
            Error.INVALID_MOVE,
            {Metadata.ALLOWED_MOVES_ARE: [Move.FOLD, Move.CHECK_CALL]},
        )

    elif action.amount_added > player_stack:
        return ValidationResult(
            Error.INVALID_AMOUNT_ADDED,
            {Metadata.AMOUNT_ADDED_SHOULD_BE_LE: player_stack},
        )

    # Player goes all in.  You can always call all in.
    elif action.amount_added == player_stack:
        # TODO: Check the total bet size here is consistent

        required_total_bet = player_stack + amount_already_added

        if action.total_bet != required_total_bet:
            return ValidationResult(
                Error.INVAID_TOTAL_BET,
                {Metadata.TOTAL_BET_SHOULD_BE: required_total_bet},
            )

        return MOVE_OK

    else:

        # Must bet at least the big blind OR must raise at least as much as the
        # last bet/raise
        # min_bet_amount = max(BIG_BLIND_AMOUNT, game.last_raise_amount())

        # Player must raise at least as much as the previous raise.
        if action.amount_added < game.amount_to_add_for_min_raise():
            return ValidationResult(
                Error.MIN_RAISE_REQUIRED,
                {Metadata.RAISE_MUST_BE_GE: game.min_bet_amount()},
            )

        return MOVE_OK


def street_over(game: GameView) -> bool:
    players_acted_this_street = set()
    for action in game.street_action():
        players_acted_this_street.add(action.player_index)

    active_players = [
        i
        for i in range(game.num_players())
        if not game.is_folded()[i] and not game.is_all_in()[i]
    ]

    # If everyone is folded or all-in at the start of the street, no need
    # for further action
    if len(game.street_action()) == 0:
        if len(active_players) < 2:
            return True

    for player_index in active_players:

        if player_index not in players_acted_this_street:
            return False

        if game.amount_to_call()[player_index] > 0:
            return False

    return True


def get_ranked_hand_groups(hands: Dict[int, EvaluationResult]) -> List[List[int]]:
    """
    Takes a map of integer players to their evaluation results and returns
    an ordered list of winning hands.  Each entry in the list represents all players
    who have the same hand value (usually this is only 1 player unless there is a tie).
    The first group has the best hand, and the second group has the second best hand,
    etc.
    :param hands: A map of player_index to evaluation result for hands that went to
    showdown.
    :return:
    """

    hand_ranks: Dict[int, List[int]] = defaultdict(list)
    for player_idx, eval in hands.items():
        hand_ranks[(eval.hand_type, eval.kicker)].append(player_idx)

    # The 'lowest' rank is the best hand
    return [players for rank, players in sorted(hand_ranks.items(), reverse=True)]


def create_tied_player_sidepots(
    winning_player_ids: List[int], amount_added_per_player: Dict[int, int]
) -> List[Tuple[int, Set[int]]]:
    # Create an ordered list of the distinct amounts contributed by these winners
    amounts = sorted(set([amount_added_per_player[i] for i in winning_player_ids]))

    sidepots = []

    previous_amount = 0

    for amount in amounts:

        player_set = set()

        # For each amount, find the players who contributed at least this much
        # and how much it was OVER the previous amount.
        for id in winning_player_ids:
            if amount_added_per_player[id] >= amount:
                player_set.add(id)

        sidepots.append((amount - previous_amount, player_set))
        previous_amount += amount

    return sidepots


def split_winnings(winnings: int, players: List[int]) -> Dict[int, int]:
    amount_per_player = winnings // len(players)

    remainder = winnings - amount_per_player * len(players)

    winnings_per_player = {id: amount_per_player for id in players}

    # Split the remainder in order
    for i in range(remainder):
        winnings_per_player[players[i]] += 1

    return winnings_per_player


def get_pot_payouts(
    ranked_hand_groups: List[List[int]], amount_added_per_player: List[int]
) -> Dict[int, int]:
    """

    :param ranked_hand_groups: Ordered list of winning player groups, with the first
     group representing players with the equivalant winning best hand, the second
     group the second best hand, etc.
    :param amount_added: The amount that ALL players added to the pot (not just the
    winning players).
    :return:
    """

    # We implement this function by taking the money all players contributed to the
    # pot and assigning it to winners in descending order.  Any one winner can only
    # make as much money as they put in per-player.  Ties are split evenly.
    #
    #

    amount_remaining_per_player: Dict[int, int] = dict(
        enumerate(amount_added_per_player)
    )

    winnings_per_player: Dict[int, int] = defaultdict(lambda: 0)

    # Iterate through equivalent groups of winning players
    for winning_players in ranked_hand_groups:

        # All these players have the equivalant hand, but there may be sidepots among
        # them.  Create a list of pairs of sidepots (represented by the amount added per player
        # to that sidepot) and the players who are involved  with the sidepot.
        # We then iterate over these in increasing sidepot size order.
        tied_sidepots = create_tied_player_sidepots(
            winning_players, amount_remaining_per_player
        )

        for amount_added, winning_player_set in tied_sidepots:

            # First, we take the per-player amount each of these players added to the sidepot
            # and add it to their winnings (they get their own money back).
            for player_id in winning_player_set:
                winnings_per_player[player_id] += amount_added
                amount_remaining_per_player[player_id] -= amount_added

            amount_from_other_players = 0

            # Next, we iterate over the non-winning players, take the per-player amount from them,
            # and split it evenly among the winning players
            for (
                other_player_id,
                amount_remaining,
            ) in amount_remaining_per_player.items():
                if other_player_id in winning_players:
                    continue

                # Take this player's money from all other player's contributions, up to a
                # max of the amount this player contributed.
                amount_to_subtract = min(amount_added, amount_remaining)
                amount_remaining_per_player[other_player_id] -= amount_to_subtract
                amount_from_other_players += amount_to_subtract

            # Split the winnings amount the players
            for player_to_get, split_amount in split_winnings(
                amount_from_other_players, list(winning_player_set)
            ).items():
                winnings_per_player[player_to_get] += split_amount

    return dict(winnings_per_player)
