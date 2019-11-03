import logging

from pokermon.ai.policy import Policy
import random

from pokermon.poker.cards import HoleCards
from pokermon.poker.game import Action, Move, GameView

import pokermon.poker.rules as rules

logger = logging.getLogger(__name__)


class RandomPolicy(Policy):
    def action(self, player_index: int, _: HoleCards, game: GameView) -> Action:

        amount_to_call = game.amount_to_call()[player_index]
        remaining_stack = game.current_stack_sizes()[player_index]

        if amount_to_call >= remaining_stack:
            move = random.choice([Move.FOLD, Move.CHECK_CALL])
        elif amount_to_call > 0:
            move = random.choice([Move.FOLD, Move.CHECK_CALL, Move.BET_RAISE])
        else:
            move = random.choice([Move.CHECK_CALL, Move.BET_RAISE])

        if move == Move.FOLD:
            return game.fold()

        elif move == Move.CHECK_CALL:
            return game.call()

        elif move == Move.BET_RAISE:

            min_raise_amount = rules.min_bet_amount(game)

            amount_needed_to_min_raise = (
                game.current_bet_amount()
                + min_raise_amount
                - game.amount_added_in_street()[player_index]
            )

            min_amount_to_put_in = min(remaining_stack, amount_needed_to_min_raise)
            max_amount_to_put_in = remaining_stack

            # randint is inclusive
            amount_to_add = random.randint(min_amount_to_put_in, max_amount_to_put_in)

            new_bet_amount = game.amount_added_in_street()[player_index] + amount_to_add

            logger.debug(
                (
                    f"Amount To Call: {amount_to_call} "
                    f"Remaining Stack: {remaining_stack} "
                    f"Min Raise Amount: {min_raise_amount} "
                    f"Amount needed to min raise: {amount_needed_to_min_raise} "
                    f"Amount To Add: {amount_to_add} "
                    f"New Bet Amount: {new_bet_amount} "
                )
            )

            return game.bet_raise(to=new_bet_amount)

        else:
            raise Exception()
