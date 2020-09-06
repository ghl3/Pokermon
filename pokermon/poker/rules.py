import logging
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from pokermon.poker.cards import FullDeal
from pokermon.poker.evaluation import EvaluationResult, Evaluator
from pokermon.poker.game import (
    BIG_BLIND_AMOUNT,
    SMALL_BLIND_AMOUNT,
    Action,
    GameView,
    Move,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GameResults:
    # If multiple players have the best hand (a tie), return a list of all player indices.
    best_hand_index: List[int]

    # A map of the player indices to their final hand (is this for all players
    # or just players who went to showdown?)
    hands: List[EvaluationResult]

    # Whether each player went to showdown (or, if they were the last player
    # after everyone else folded, which we consider to be a 1-player showdown).
    # In other words, showdown == !folded
    went_to_showdown: List[bool]

    # The amount of money won by each player at the end of the hand (not profit)
    earned_at_showdown: List[int]

    # The actual profits, in small blinds, won or list by each player during this game
    profits: List[int]


class Error(Enum):
    UNKNOWN_MOVE = 1
    SMALL_BLIND_REQUIRED = 2
    BIG_BLIND_REQUIRED = 3
    INVALID_AMOUNT_ADDED = 4
    INVAID_TOTAL_BET = 5
    INVALID_PLAYER = 6
    MIN_RAISE_REQUIRED = 7


class Metadata(Enum):
    TYPE = 1
    BLIND_AMOUNT = 2
    AMOUNT_ADDED_SHOULD_BE = 3
    AMOUNT_ADDED_SHOULD_BE_GE = 4
    AMOUNT_ADDED_SHOULD_BE_LE = 5
    TOTAL_BET_SHOULD_BE = 6
    MIN_BE_RAISE_AMOUNT = 7
    RAISE_MUST_BE_GE = 8


@dataclass
class ValidationResult:
    error: Optional[Error]

    metadata: Dict[Metadata, Any]

    def is_valid(self):
        return self.error is None


MOVE_OK = ValidationResult(None, {})


def min_bet_amount(game: GameView) -> int:
    """The minimim amount that can be raised above the last bet
  """
    return max(BIG_BLIND_AMOUNT, game.last_raise_amount())


def action_valid(
    action_index: int, player_index: int, action: Action, game: GameView
) -> ValidationResult:
    amount_to_call = game.amount_to_call()[player_index]
    player_stack = game.current_stack_sizes()[player_index]
    amount_already_addded = game.amount_added_in_street()[player_index]

    if action_index == 0:
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

    elif action.move == Move.FOLD:
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

    elif action.move == Move.CHECK_CALL:

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

    elif action.move == Move.BET_RAISE:

        if action.amount_added > player_stack:
            return ValidationResult(
                Error.INVALID_AMOUNT_ADDED,
                {Metadata.AMOUNT_ADDED_SHOULD_BE_LE: player_stack},
            )

        # Player goes all in.  You can always call all in.
        elif action.amount_added == player_stack:
            # TODO: Check the total bet size here is consistent

            required_total_bet = player_stack + amount_already_addded

            if action.total_bet != required_total_bet:
                return ValidationResult(
                    Error.INVAID_TOTAL_BET,
                    {Metadata.TOTAL_BET_SHOULD_BE: required_total_bet},
                )

            return MOVE_OK

        else:

            # Must bet at least the big blind OR must raise at least as much as the
            # last bet/raise
            min_bet_amount = max(BIG_BLIND_AMOUNT, game.last_raise_amount())

            # Player must raise at least as much as the previous raise.
            if action.total_bet - game.current_bet_amount() < min_bet_amount:
                return ValidationResult(
                    Error.MIN_RAISE_REQUIRED,
                    {Metadata.RAISE_MUST_BE_GE: min_bet_amount},
                )

            return MOVE_OK

    return ValidationResult(Error.UNKNOWN_MOVE, {})


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


def get_winning_players(hands: Dict[int, EvaluationResult]) -> List[int]:
    """
    Returns the order of winning players (among all players who went to showdown) in order (the
    first player index returned as the best hand, the second the next best, etc)
    :param hands:
    :return:
    """
    # Lower ranks are better
    winning_rank = min([res.rank for _, res in hands.items()])
    return [player_idx for player_idx, h in hands.items() if h.rank == winning_rank]


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

    hand_ranks = defaultdict(list)
    for player_idx, res in hands.items():
        hand_ranks[res.rank].append(player_idx)

    # The 'lowest' rank is the best hand
    return list(sorted(hand_ranks.items(), key=lambda x: x[0]))


def get_pot_payouts(ranked_hand_groups: List[List[int]],
                    amount_added_per_player: List[int]):
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

    amount_remaining_per_player = dict(enumerate(amount_added_per_player))

    winnings_per_player = defaultdict(lambda: 0)

    # Iterate through equivalent groups of winning players
    for winning_players in ranked_hand_groups:

        # Handle ties later
        assert len(winning_players) == 1

        player_id = winning_players[0]

        # Get the amount this player contributed to the remaining pot
        amount_added = amount_remaining_per_player[player_id]

        # Subtract this amount from all players

        # Move the money this player contributed to the winnings map (they get their
        # own money back)
        winnings_per_player[player_id] += amount_added
        amount_remaining_per_player[player_id] -= amount_added

        for other_player_id, amount_remaining in amount_remaining_per_player.items():
            if other_player_id == player_id:
                continue

            # Take this player's money from all other player's contributions, up to a
            # max of the amount this player contributed
            amount_to_subtract = min(amount_added, amount_remaining)
            amount_remaining_per_player[other_player_id] -= amount_to_subtract
            winnings_per_player[player_id] += amount_to_subtract

    return dict(winnings_per_player)


def pot_per_winning_player(pot_size: int, winning_players: List[int]) -> Dict[int, int]:
    pot_even_division = pot_size // len(winning_players)
    leftover = pot_size - pot_even_division

    winning_per_player = {
        player_index: pot_even_division for player_index in winning_players
    }

    while leftover > 0:
        for player_index in sorted(winning_players):
            winning_per_player[player_index] += 1
            leftover -= 1
            if leftover == 0:
                break

    return winning_per_player


def get_result(cards: FullDeal, game: GameView, evaluator: Evaluator) -> GameResults:
    # Calculate who has the best hand

    all_hands: List[EvaluationResult] = []

    went_to_showdown: List[bool] = []

    for player_index in range(game.num_players()):
        hole_cards = cards.hole_cards[player_index]
        board = cards.board

        eval_result: EvaluationResult = evaluator.evaluate(hole_cards, board)

        all_hands.append(eval_result)

        went_to_showdown.append(not game.is_folded()[player_index])

    winning_players = get_winning_players(
        {idx: hand for idx, hand in enumerate(all_hands) if went_to_showdown[idx]}
    )

    profit_per_player = [-1 * amount_bet for amount_bet in game.amount_added_total()]

    # TODO: Support side pots
    pot_size = 0
    for amount in game.amount_added_total():
        pot_size += amount

    earned_at_showdown = [0 for _ in range(game.num_players())]
    for player_index, earning in pot_per_winning_player(
        pot_size, winning_players
    ).items():
        earned_at_showdown[player_index] += earning
        profit_per_player[player_index] += earning

    return GameResults(
        best_hand_index=winning_players,
        hands=all_hands,
        went_to_showdown=went_to_showdown,
        earned_at_showdown=earned_at_showdown,
        profits=profit_per_player,
    )
