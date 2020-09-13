import math
from dataclasses import dataclass
from typing import List

from pokermon.data.utils import iter_actions
from pokermon.poker.game import GameView, Action, Move

NUM_ACTION_BET_BINS = 20


# At timestamp i, this was the action made at i-1
@dataclass(frozen=True)
class LastAction:
    move: int
    action_encoded: int
    amount_added: int
    amount_added_percent_of_remaining: int
    amount_raised: int
    amount_raised_percent_of_pot: int


# At timestamp i, the action that will be made
@dataclass(frozen=True)
class NextAction:
    move: int
    action_encoded: int
    amount_added: int
    amount_raised: int
    new_total_bet: int


def encode_action(action: Action, game: GameView) -> int:
    # 0 = Fold
    # 1 = Call
    # 2 = Min Raise (+ 0 * delta)
    # 3 = Raise Min + 1*delta
    # 4 = Raise Min + 2*delta
    # 5 = Raise Min + 3*delta
    # 6 = Raise Min + 4*delta
    # 7 = Raise Min + 5*delta = ALL IN
    if action.move == Move.FOLD:
        return 0
    elif action.move == Move.CHECK_CALL:
        return 1
    else:
        min_raise = game.min_bet_amount()
        remaining_stack = game.current_stack_sizes()[game.current_player()]
        range = (remaining_stack - min_raise)
        delta = range / NUM_ACTION_BET_BINS
        amount_raised = action.amount_added
        num_deltas = int(math.floor((amount_raised - min_raise) / delta))
        return 2 + num_deltas


def make_action_from_encoded(action_index: int, game: GameView) -> Action:
    # Example with
    # NUM_ACTION_BET_BINS = 20:
    # Amount_remaining = 82
    # Min Bet Amount = 2
    # Max Bet Amount = 82
    # Range = 80
    # Delta = 4
    # 0 = Fold
    # 1 = Call
    # 2 = Min Raise (+ 0 * delta) = 2
    # 3 = Raise Min + 1*delta = 6
    # 4 = Raise Min + 2*delta = 10
    # 5 = Raise Min + 3*delta = 14
    # 6 = Raise Min + 4*delta = 18
    # 7 = Raise Min + 5*delta = ALL IN

    # TODO: Assert min raise < all in amount

    if action_index == 0:
        return game.fold()
    elif action_index == 1:
        return game.call()
    elif action_index == 2:
        return game.min_raise()
    elif action_index == NUM_ACTION_BET_BINS + 2:
        return game.go_all_in()
    else:
        max_add = game.current_stack_sizes()[game.current_player()]
        min_add = min(max_add, game.min_bet_amount())
        delta = (max_add - min_add) / NUM_ACTION_BET_BINS
        num_deltas = (action_index - 2)
        amount_to_add = int(math.floor(min_add + num_deltas * delta))
        return game.bet_raise(amount_to_add=amount_to_add)


def make_last_actions(game: GameView) -> List[LastAction]:
    # We need a dummy entry for the first voluntary action
    actions = [LastAction(move=-1,
                          action_encoded=-1,
                          amount_added=-1,
                          amount_added_percent_of_remaining=-1,
                          amount_raised=-1,
                          amount_raised_percent_of_pot=-1)]

    for i, a in list(iter_actions(game))[:-1]:
        game_view = game.view(i)

        stack_size = game_view.current_stack_sizes()[game_view.current_player()]
        pot_size = game_view.pot_size()
        current_bet = game_view.current_bet_amount()
        raise_amount = a.total_bet - current_bet

        actions.append(
            LastAction(
                move=a.move.value,
                action_encoded=encode_action(a, game),
                amount_added=a.amount_added,
                amount_added_percent_of_remaining=100 * a.amount_added // stack_size,
                amount_raised=raise_amount,
                amount_raised_percent_of_pot=100 * raise_amount // pot_size
            )
        )

    return actions


def make_next_actions(game: GameView) -> List[NextAction]:
    actions = []

    for i, a in iter_actions(game):
        game_view = game.view(i)

        current_bet = game_view.current_bet_amount()
        raise_amount = a.total_bet - current_bet

        actions.append(
            NextAction(
                move=a.move.value,
                action_encoded=encode_action(a, game),
                amount_added=a.amount_added,
                new_total_bet=a.total_bet,
                amount_raised=raise_amount
            )
        )

    return actions
