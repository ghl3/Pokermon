import logging
from dataclasses import dataclass
from typing import Optional

import pokermon.poker.rules as rules
from pokermon.poker.game import Action, Game, Street

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Result:
    street: Street

    current_player: Optional[int] = None

    total_bet: Optional[int] = None

    amount_to_call: Optional[int] = None


class GameRunner:
    def __init__(self, starting_stacks):
        # For now, only support players having the same starting stacks.
        # This avoids having to implement side pots.
        # TODO: Support Side Pots
        assert len(set(starting_stacks)) == 1

        # Must have at least 1 player
        assert len(starting_stacks) > 1

        self.game_started = False
        self.action_index = 0
        self.game = Game(starting_stacks=starting_stacks)

    def game_view(self):
        return self.game.view()

    def current_player(self):
        return self.game_view().current_player()

    def street(self):
        return self.game_view().street()

    def start_game(self):
        # Small/Big Blind
        self.game_started = True
        self.game.set_street(Street.PREFLOP)
        self.add_small_blind()
        self.add_big_blind()

    # TODO: Make this more fluent.  It can either take an action OR
    # it can take moves which will build an action, eg raise_to=50, etc
    # These must be validated...
    def advance(self, action: Action) -> Result:
        if not self.game_started:
            raise Exception("Game not started")

        player_index = self.game_view().current_player()

        action_result = rules.action_valid(
            action_index=self.action_index,
            player_index=player_index,
            action=action,
            game=self.game_view(),
        )

        # Validate the action
        if player_index != action.player_index:
            raise Exception("Wrong Player")

        if not action_result.is_valid():
            logger.error("Action is invalid %s %s", action, action_result)
            raise Exception("Action is invalid", action, action_result)

        self.game.add_action(action)
        self.action_index += 1
        player_index = self.game_view().current_player()

        while rules.street_over(self.game_view()):
            self._advance_street()
            if self.street() == Street.OVER:
                break

        # Return the current state of the game

        if self.game_view().street() == Street.OVER:
            return Result(street=self.game_view().street())
        else:
            return Result(
                street=self.game_view().street(),
                current_player=self.game_view().current_player(),
                total_bet=self.game_view().current_bet_amount(),
                amount_to_call=self.game_view().amount_to_call()[player_index],
            )

    def add_small_blind(self) -> Result:
        return self.advance(self.game_view().small_blind())

    def add_big_blind(self) -> Result:
        return self.advance(self.game_view().big_blind())

    def call(self) -> Result:
        return self.advance(self.game_view().call())

    def check(self) -> Result:
        return self.advance(self.game_view().check())

    def bet_raise(
        self, to: Optional[int] = None, raise_amount: Optional[int] = None
    ) -> Result:
        return self.advance(
            self.game_view().bet_raise(to=to, raise_amount=raise_amount)
        )

    def fold(self) -> Result:
        return self.advance(self.game_view().fold())

    def _advance_street(self):

        if self.game_view().street() == Street.PREFLOP:
            self.game.set_street(Street.FLOP)
        elif self.game_view().street() == Street.FLOP:
            self.game.set_street(Street.TURN)
        elif self.game_view().street() == Street.TURN:
            self.game.set_street(Street.RIVER)

        elif self.game_view().street() == Street.RIVER:
            self.game.set_street(Street.OVER)
        else:
            raise Exception()
