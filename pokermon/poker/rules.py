import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional

from pokermon.poker.evaluation import Evaluator, EvaluationResult
from pokermon.poker.game import GameView, Action, Move, SMALL_BLIND_AMOUNT
from pokermon.poker.game import BIG_BLIND_AMOUNT
from pokermon.poker.cards import FullDeal

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GameResults:
    # If multiple players have the best hand (a tie), return a list of all player indices.
    best_hand_index: List[int]

    hands: Dict[int, EvaluationResult]

    # The amount of money won by this player at the end of the hand (not profit)
    winnings: List[int]

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
class Result:
    error: Optional[Error]

    metadata: Dict[Metadata, Any]

    def is_valid(self):
        return self.error is None


MOVE_OK = Result(None, {})


def min_bet_amount(game: GameView) -> int:
    """The minimim amount that can be raised above the last bet
  """
    return max(BIG_BLIND_AMOUNT, game.last_raise_amount())


def action_valid(
    action_index: int, player_index: int, action: Action, game: GameView
) -> Result:
    amount_to_call = game.amount_to_call()[player_index]
    player_stack = game.current_stack_sizes()[player_index]
    amount_already_addded = game.amount_added_in_street()[player_index]

    if action_index == 0:
        if action.move != Move.SMALL_BLIND:
            return Result(
                Error.SMALL_BLIND_REQUIRED, {Metadata.BLIND_AMOUNT: SMALL_BLIND_AMOUNT}
            )
        if action.amount_added != SMALL_BLIND_AMOUNT:
            return Result(
                Error.INVALID_AMOUNT_ADDED, {Metadata.BLIND_AMOUNT: SMALL_BLIND_AMOUNT}
            )
        if action.total_bet != SMALL_BLIND_AMOUNT:
            return Result(
                Error.INVAID_TOTAL_BET, {Metadata.BLIND_AMOUNT: SMALL_BLIND_AMOUNT}
            )
        return MOVE_OK
        # return action.move == Move.SMALL_BLIND and action.amount_added == SMALL_BLIND_AMOUNT and action.total_bet == SMALL_BLIND_AMOUNT

    elif action_index == 1:
        if action.move != Move.BIG_BLIND:
            return Result(
                Error.BIG_BLIND_REQUIRED, {Metadata.BLIND_AMOUNT: BIG_BLIND_AMOUNT}
            )
        if action.amount_added != BIG_BLIND_AMOUNT:
            return Result(
                Error.INVALID_AMOUNT_ADDED, {Metadata.BLIND_AMOUNT: BIG_BLIND_AMOUNT}
            )
        if action.total_bet != BIG_BLIND_AMOUNT:
            return Result(
                Error.INVAID_TOTAL_BET, {Metadata.BLIND_AMOUNT: BIG_BLIND_AMOUNT}
            )
        return MOVE_OK

    elif action.move == Move.FOLD:
        if action.amount_added != 0:
            return Result(
                Error.INVALID_AMOUNT_ADDED, {Metadata.AMOUNT_ADDED_SHOULD_BE: 0}
            )
        if action.total_bet != game.current_bet_amount():
            return Result(
                Error.INVALID_AMOUNT_ADDED,
                {Metadata.TOTAL_AMOUNT_SHOULD_BE: game.current_bet_amount()},
            )
        return MOVE_OK

    elif action.move == Move.CHECK_CALL:

        if amount_to_call <= player_stack:

            if action.amount_added != amount_to_call:
                return Result(
                    Error.INVALID_AMOUNT_ADDED,
                    {Metadata.AMOUNT_ADDED_SHOULD_BE: amount_to_call},
                )

            if action.total_bet != game.current_bet_amount():
                return Result(
                    Error.INVAID_TOTAL_BET,
                    {Metadata.TOTAL_BET_SHOULD_BE: game.current_bet_amount()},
                )

            return MOVE_OK

        else:
            # Player calls all in

            if action.amount_added != player_stack:
                return Result(
                    Error.INVALID_AMOUNT_ADDED,
                    {Metadata.AMOUNT_ADDED_SHOULD_BE: player_stack},
                )

            if action.total_bet != game.current_bet_amount():
                return Result(
                    Error.INVAID_TOTAL_BET,
                    {Metadata.TOTAL_BET_SHOULD_BE: game.current_bet_amount()},
                )

            return MOVE_OK

    elif action.move == Move.BET_RAISE:

        if action.amount_added > player_stack:
            return Result(
                Error.INVALID_AMOUNT_ADDED,
                {Metadata.AMOUNT_ADDED_SHOULD_BE_LE: player_stack},
            )

        # Player goes all in.  You can always call all in.
        elif action.amount_added == player_stack:
            # TODO: Check the total bet size here is consistent

            required_total_bet = player_stack + amount_already_addded

            if action.total_bet != required_total_bet:
                return Result(
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
                return Result(
                    Error.MIN_RAISE_REQUIRED,
                    {Metadata.RAISE_MUST_BE_GE: min_bet_amount},
                )

            return MOVE_OK

    return Result(Error.UNKNOWN_MOVE, {})


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
    # Lower ranks are better
    winning_rank = min([res.rank for _, res in hands.items()])
    return [player_idx for player_idx, h in hands.items() if h.rank == winning_rank]


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

    showdown_hands: Dict[int, EvaluationResult] = {}

    for player_index in range(game.num_players()):

        if not game.is_folded()[player_index]:
            hole_cards = cards.hole_cards[player_index]
            board = cards.board

            eval_result: EvaluationResult = evaluator.evaluate(hole_cards, board)

            showdown_hands[player_index] = eval_result

    winning_players = get_winning_players(showdown_hands)

    profit_per_player = [-1 * amount_bet for amount_bet in game.amount_added_total()]

    # TODO: Support side pots
    pot_size = 0
    for amount in game.amount_added_total():
        pot_size += amount

    winnings_per_player = [0 for _ in range(game.num_players())]
    for player_index, winnings in pot_per_winning_player(
        pot_size, winning_players
    ).items():
        winnings_per_player[player_index] += winnings
        profit_per_player[player_index] += winnings

    return GameResults(
        best_hand_index=winning_players,
        hands=showdown_hands,
        winnings=winnings_per_player,
        profits=[
            profit_per_player[player_index]
            for player_index in range(game.num_players())
        ],
    )
