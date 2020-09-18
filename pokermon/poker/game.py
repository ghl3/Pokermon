# All Amounts are relative to the small blind.
# from functools import lru_cache

import random
from collections import defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, Iterable, List, Optional, Union

from pokermon.poker.ordered_enum import OrderedEnum

"""
An important concept in a game is the timestamp.  A timestamp connects two ideas:
- An index into events
- An index for the state of the game BEFORE the ith action was made



So, game.view(i) is the state of the game before the ith event (when only i events have
been made), and action[i] is the action made after the state game_view(i).
 
For example, say the events are the following:
  0 = PREFLOP
  1 = SMALL BLIND
  2 = BIG BLIND
  3 = BET 10
  4 = RAISE TO 25
  5 = ?
  
The current state of the game is game.view(5).  There have already been 5 events.
The next action will be action_index = 5 (making it the 6th action total).
"""


class Street(OrderedEnum):
    PREFLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    OVER = 5


class Move(OrderedEnum):
    SMALL_BLIND = 1
    BIG_BLIND = 2
    FOLD = 3
    CHECK_CALL = 4
    BET_RAISE = 5


SMALL_BLIND_AMOUNT = 1
BIG_BLIND_AMOUNT = 2


@dataclass(frozen=True)
class Action:
    player_index: int
    move: Move

    # The amount this player added to the pot as a part of this action.
    amount_added: int

    # The new total size of the bet after this action.
    total_bet: int


# A street, as an event, represents the dealing of that street.
Event = Union[Action, Street]


cache = lru_cache(2048)


@dataclass
class Game:
    """
    All data for a game that is fully known to all players.

    An observed game is a snapshot of a game at a given action (or possibly after
    all actions are complete and the hand is done).

    Each action in an observed game has a timestamp index (integer).  These
    integers cross streets (so, if the last action on the FLOP is N, then the
    first action on the TURN is N+1).
    """

    # A list of starting player stacks
    starting_stacks: List[int]

    events: List[Event] = field(default_factory=list)

    # A unique id for this game
    id: int = field(default_factory=lambda: random.getrandbits(64))

    def num_players(self) -> int:
        return len(self.starting_stacks)

    def set_street(self, street: Street):
        self.events.append(street)

    def current_street(self) -> Street:
        for e in reversed(self.events):
            if isinstance(e, Street):
                return e
        return Street.PREFLOP

    def end_hand(self):
        self.set_street(Street.OVER)

    def all_action(self) -> List[Action]:
        return [e for e in self.events if isinstance(e, Action)]

    def add_action(self, action: Action) -> None:
        self.events.append(action)

    def timestamp(self) -> int:
        return len(self.events)

    def view(self, timestamp: int = None):
        """Return a view of the game at the given timestamp.

        The meaning of a timestamp is defined as follows:
        - At the ith timestamp, i moves have been made
        - At the ith timestamp, a user is deciding the move with index=i (0 indexed)

        A timestamp represents different states of the game
        Returns a view of the game AFTER the timestamp'th action.  Or, equivalently,
        returns a view of the game when the 0-indexed action is being decided.

        So, if timestamp == 0, then no actions have been done.
        If timestamp==2, then the view is AFTER the big blind is posted.
        The current view is timestamp=len(action) (in other words, length is one
        more than the last action index, which is therefore the current move).
        :param timestamp:
        :return:
        """

        if timestamp is None:
            timestamp = self.timestamp()

        if timestamp > self.timestamp():
            raise Exception("Timestamp out of range")
        else:
            return GameView(self, timestamp)


@dataclass(frozen=True)
class GameView:
    """
    A view of an observed game at a given timestamp.

    Contains methods to get useful information summarizing the state of the game.

    """

    _game: Game

    # The timestamp is guaranteed to be in the range of the given game.
    timestamp: int

    def __hash__(self):
        return hash((self._game.id, self.timestamp, "364258436582634"))

    @cache
    def num_players(self) -> int:
        return self._game.num_players()

    @cache
    def events(self) -> Iterable[Event]:
        return self._game.events[: self.timestamp]

    @cache
    def starting_stacks(self) -> List[int]:
        return self._game.starting_stacks

    def view(self, timestamp: int = None):
        return self._game.view(timestamp)

    @cache
    def next_action(
        self,
    ) -> Optional[Action]:

        for i in range(self.timestamp, len(self._game.events)):
            if isinstance(self._game.events[i], Action):
                return self._game.events[i]

        return None

    @cache
    def previous_action(
        self,
    ) -> Optional[Action]:

        for i in range(0, self.timestamp):
            if isinstance(self._game.events[i], Action):
                return self._game.events[i]

        return None

    # Nothing below these methods should reference the underlying game

    @cache
    def _player_list(self, starting_player: int = 0) -> List[int]:
        all_players_twice = list(range(self.num_players())) + list(
            range(self.num_players())
        )
        return all_players_twice[starting_player : starting_player + self.num_players()]

    @cache
    def current_player(self) -> int:
        if len(self.street_action()) == 0:
            starting_player = 0
        else:
            starting_player = (
                self.street_action()[-1].player_index + 1
            ) % self.num_players()

        for player in self._player_list(starting_player):
            if not self.is_folded()[player] and not self.is_all_in()[player]:
                return player

        return -1

    @cache
    def street(self) -> Street:

        current_street = Street.PREFLOP

        for event in self.events():

            if isinstance(event, Street):
                current_street = event

        return current_street

    @cache
    def street_action_dict(self) -> Dict[Street, List[Action]]:

        street_actions: Dict[Street, List[Action]] = defaultdict(lambda: [])

        current_street = Street.PREFLOP

        for e in self.events():

            if isinstance(e, Action):
                street_actions[current_street].append(e)

            elif isinstance(e, Street):
                current_street = e

        return street_actions

    @cache
    def street_action(self) -> List[Action]:
        return self.street_action_dict()[self.street()]

    @cache
    def current_street_index(self) -> int:
        return len(self.street_action())

    @cache
    def all_actions(self) -> List[Action]:
        """
        The list of actions before the given timestamp  on the street containing the given action.
        :param timestamp:
        :return:
        """

        return [e for e in self.events() if isinstance(e, Action)]

    @cache
    def amount_added_in_street(self) -> List[int]:
        """
        Return a dictionary of the total amount bet per player so far.
        :return:
        """

        amount = [0 for _ in range(self.num_players())]

        for action in self.street_action():
            player_id = action.player_index

            amount[player_id] += action.amount_added

        return amount

    @cache
    def amount_added_total(self) -> List[int]:
        """
        Return a dictionary of the total amount bet per player so far.
        :return:
        """

        amount = [0 for _ in range(self.num_players())]

        for action in self.all_actions():
            player_id = action.player_index

            amount[player_id] += action.amount_added

        return amount

    @cache
    def pot_size(self) -> int:
        pot = 0
        for amount in self.amount_added_total():
            pot += amount
        return pot

    @cache
    def current_stack_sizes(self) -> List[int]:
        return [
            self.starting_stacks()[i] - amount_bet
            for i, amount_bet in enumerate(self.amount_added_total())
        ]

    @cache
    def current_bet_amount(self) -> int:
        return max(self.amount_added_in_street())

    @cache
    def amount_to_call(self) -> List[int]:
        return [
            self.current_bet_amount() - amount_bet
            for amount_bet in self.amount_added_in_street()
        ]

    @cache
    def last_raise_amount(self) -> int:
        """
        The size of the last raise over the previous bet
        :return:
        """

        if len(self.street_action()) == 0:
            return 0

        current_bet = self.street_action()[-1].total_bet

        for action in reversed(self.street_action()):

            if action.total_bet != current_bet:
                return current_bet - action.total_bet

        return current_bet

    @cache
    def is_folded(self) -> List[bool]:

        folded = [False for _ in range(self.num_players())]

        for a in self.all_actions():
            if a.move == Move.FOLD:
                folded[a.player_index] = True

        return folded

    @cache
    def is_all_in(self) -> List[bool]:
        return [
            current_stack_size == 0 for current_stack_size in self.current_stack_sizes()
        ]

    @cache
    def min_bet_amount(self) -> int:
        """Amount that a player can raise over the last bet.

        Note that, to make this raise, the player may have to put more than this
        amount in the pot.
        """
        return max(BIG_BLIND_AMOUNT, self.last_raise_amount())

    @cache
    def new_bet_size_if_min_raise(self) -> int:
        """Size of the new total bet if a player were to execute a full min raise
        (meaning, they're able to min raise without going all in).
        """
        return self.current_bet_amount() + self.min_bet_amount()

    @cache
    def amount_to_add_for_min_raise(self) -> int:
        """The amount that a player would have to add to the pot in order to execute
        a min raise.  If a player would have to go all in to min raise, this returns
        the all in amount
        """

        amount_remaining = self.current_stack_sizes()[self.current_player()]
        amount_bet_in_street = self.amount_added_in_street()[self.current_player()]

        amount_to_add_for_full_min_raise = (
            self.new_bet_size_if_min_raise() - amount_bet_in_street
        )

        return min(amount_remaining, amount_to_add_for_full_min_raise)

    #
    # Actions
    #

    @cache
    def small_blind(self) -> Action:
        return Action(
            self.current_player(),
            Move.SMALL_BLIND,
            total_bet=SMALL_BLIND_AMOUNT,
            amount_added=SMALL_BLIND_AMOUNT,
        )

    @cache
    def big_blind(self) -> Action:
        return Action(
            self.current_player(),
            Move.BIG_BLIND,
            total_bet=BIG_BLIND_AMOUNT,
            amount_added=BIG_BLIND_AMOUNT,
        )

    @cache
    def call(self) -> Action:
        player_index = self.current_player()

        amount_to_call = self.amount_to_call()[player_index]
        player_stack = self.current_stack_sizes()[player_index]

        if amount_to_call < player_stack:
            return Action(
                player_index,
                Move.CHECK_CALL,
                amount_added=amount_to_call,
                total_bet=self.current_bet_amount(),
            )
        else:
            return Action(
                player_index,
                Move.CHECK_CALL,
                amount_added=player_stack,
                total_bet=self.current_bet_amount(),
            )

    @cache
    def check(self) -> Action:
        return self.call()

    @cache
    def bet_raise(
        self,
        to: Optional[int] = None,
        raise_amount: Optional[int] = None,
        amount_to_add: Optional[int] = None,
    ) -> Action:
        """
        to: The new total bet
        raise_amount: The amount raised OVER the previous bet amount
        amount_to_add: The amount that the player adds to the pot

        Example:
            player A: Bet 5
            player B: Raise To 20
            Player A: Raise to 30

        Before the last move, player A has already put 5 in the pot.  The bet is at 20,
        and they raise it to 50 (30 more than the last bet amount).  This is the same as:

        bet_raise(to=50)
        bet_raise(raise_amount=30)
        bet_raise(amount_to_add=45)

        """

        player_index = self.current_player()

        if sum(bool(x is not None) for x in [to, raise_amount, amount_to_add]) != 1:
            raise Exception()

        elif amount_to_add is not None:
            amount_already_added = self.amount_added_in_street()[player_index]
            new_bet_size = amount_already_added + amount_to_add

        elif to is not None:
            new_bet_size = to
            amount_to_add = to - self.amount_added_in_street()[player_index]

        elif raise_amount is not None:
            new_bet_size = self.current_bet_amount() + raise_amount
            amount_to_add = new_bet_size - self.amount_added_in_street()[player_index]

        else:
            raise Exception()

        # This may be an invalid raise, but this will be caught downstream
        return Action(player_index, Move.BET_RAISE, amount_to_add, new_bet_size)

    # TODO: Ensure these work
    @cache
    def min_raise(self) -> Action:
        return self.bet_raise(amount_to_add=self.amount_to_add_for_min_raise())

    @cache
    def go_all_in(self) -> Action:

        remaining_stack = self.current_stack_sizes()[self.current_player()]
        amount_to_call = self.amount_to_call()[self.current_player()]

        # An all-in may be either a call (if you can't affort a full call) or a raise
        if remaining_stack <= amount_to_call:
            return self.call()
        else:
            return self.bet_raise(amount_to_add=remaining_stack)

    @cache
    def fold(self) -> Action:
        player_index = self.current_player()
        return Action(
            player_index, Move.FOLD, amount_added=0, total_bet=self.current_bet_amount()
        )
