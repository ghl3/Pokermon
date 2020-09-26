import math
from dataclasses import dataclass
from typing import List

from pokermon.features.utils import iter_game_states
from pokermon.poker.game import Action, GameView, Move

NUM_ACTION_BET_BINS = 20


# At timestamp i, this was the action made at i-1
@dataclass(frozen=True)
class LastAction:
    move: int
    action_encoded: int
    amount_added: int
    amount_added_percent_of_remaining: float
    amount_raised: int
    amount_raised_percent_of_pot: float


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
        min_raise = game.amount_to_add_for_min_raise()
        remaining_stack = game.current_stack_sizes()[game.current_player()]

        if action.amount_added == remaining_stack:
            return 22
        elif action.amount_added < min_raise or action.amount_added > remaining_stack:
            raise Exception(
                f"Cannot make action {action} {min_raise=} {remaining_stack=}"
            )
        elif action.amount_added == min_raise:
            return 2

        delta = (remaining_stack - min_raise) / NUM_ACTION_BET_BINS
        amount_raised = action.amount_added
        num_deltas = int(math.ceil((amount_raised - min_raise) / delta))
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

    min_raise_amount = game.amount_to_add_for_min_raise()
    remaining_stack = game.current_stack_sizes()[game.current_player()]

    amount_to_call = game.amount_to_call()[game.current_player()]

    if action_index == 0:
        # Don't fold for no money!
        if amount_to_call > 0:
            return game.fold()
        else:
            return game.call()
    elif action_index == 1:
        return game.call()
    # If any raise is an all-in, then we return an all-in
    elif min_raise_amount >= remaining_stack:
        return game.go_all_in()
    elif action_index == 2:
        return game.min_raise()
    elif action_index == NUM_ACTION_BET_BINS + 2:
        return game.go_all_in()
    else:
        min_add = min_raise_amount
        max_add = remaining_stack
        if max_add == min_add:
            return game.go_all_in()
        delta = (max_add - min_add) / NUM_ACTION_BET_BINS
        if delta == 0:
            raise Exception(f"{min_add} {max_add} {NUM_ACTION_BET_BINS} {delta}")
        num_deltas = action_index - 2
        amount_to_add = int(math.floor(min_add + num_deltas * delta))
        return game.bet_raise(amount_to_add=amount_to_add)


def make_last_actions(game: GameView) -> List[LastAction]:
    # We need a dummy entry for the first voluntary action
    actions = [
        LastAction(
            move=-1,
            action_encoded=-1,
            amount_added=-1,
            amount_added_percent_of_remaining=-1,
            amount_raised=-1,
            amount_raised_percent_of_pot=-1,
        )
    ]

    # Iterate over states shifted by one
    for i in list(iter_game_states(game))[:-1]:
        game_view = game.view(i)
        a: Action = game_view.next_action()

        stack_size = game_view.current_stack_sizes()[game_view.current_player()]
        pot_size = game_view.pot_size()
        current_bet = game_view.current_bet_amount()
        raise_amount = a.total_bet - current_bet

        actions.append(
            LastAction(
                move=a.move.value,
                action_encoded=encode_action(a, game_view),
                amount_added=a.amount_added,
                amount_added_percent_of_remaining=a.amount_added / stack_size,
                amount_raised=raise_amount,
                amount_raised_percent_of_pot=raise_amount / pot_size,
            )
        )

    return actions


def make_next_actions(game: GameView) -> List[NextAction]:
    actions: List[NextAction] = []

    for i in iter_game_states(game):
        game_view = game.view(i)

        a: Action = game_view.next_action()

        current_bet = game_view.current_bet_amount()
        raise_amount = a.total_bet - current_bet

        actions.append(
            NextAction(
                move=a.move.value,
                action_encoded=encode_action(a, game_view),
                amount_added=a.amount_added,
                new_total_bet=a.total_bet,
                amount_raised=raise_amount,
            )
        )

    return actions
