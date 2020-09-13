# There is a State per-action.
# There are two types of state:
# - Public State: The state anyone watching the game would know
# - Private State: The state that requires knowing someone's hole cards
from dataclasses import dataclass
from typing import List, Optional

from pokermon.data.utils import card_order, iter_actions
from pokermon.poker.cards import Board
from pokermon.poker.game import GameView, Street


@dataclass(frozen=True)
class PublicState:
    current_player_index: int
    street: int
    current_player_mask: List[int]
    folded_player_mask: List[int]
    all_in_player_mask: List[int]
    stack_sizes: List[int]

    amount_to_call: List[int]
    min_raise_amount: int

    flop_0_rank: Optional[int]
    flop_0_suit: Optional[int]
    flop_1_rank: Optional[int]
    flop_1_suit: Optional[int]
    flop_2_rank: Optional[int]
    flop_2_suit: Optional[int]
    turn_rank: Optional[int]
    turn_suit: Optional[int]
    river_rank: Optional[int]
    river_suit: Optional[int]


@dataclass(frozen=True)
class PrivateState:
    current_hand_type: int
    current_hand_strength: float
    current_hand_rank: int

    # Desired Features:
    # Post Flop Best Hand index (eg is nuts, etc)
    # Though, I guess current rank doesn't really matter, only equity.
    # Equity % against random hand
    # Possible Solutions:
    # treys
    # https://github.com/ktseng/holdem_calc
    # https://pypi.org/project/PokerSleuth/#history
    # https://github.com/mitpokerbots/pbots_calc


def make_public_states(game: GameView, board: Optional[Board]):
    public_states = []

    for i, a in iter_actions(game):
        game_view = game.view(i)

        if board is None:
            current_board = Board(flop=None, turn=None, river=None)
        else:
            current_board = board.at_street(game_view.street())

        current_player_mask = [0 for _ in range(game_view.num_players())]
        current_player_mask[a.player_index] = 1

        if game_view.street() >= Street.FLOP and current_board.flop is not None:
            flop_0, flop_1, flop_2 = sorted(current_board.flop, key=card_order)
            flop_0_rank = flop_0.rank.value
            flop_0_suit = flop_0.suit.value
            flop_1_rank = flop_1.rank.value
            flop_1_suit = flop_1.suit.value
            flop_2_rank = flop_2.rank.value
            flop_2_suit = flop_2.suit.value
        else:
            flop_0_rank = None
            flop_0_suit = None
            flop_1_rank = None
            flop_1_suit = None
            flop_2_rank = None
            flop_2_suit = None

        if game_view.street() >= Street.TURN and current_board.turn is not None:
            turn = current_board.turn
            turn_rank = turn.rank.value
            turn_suit = turn.suit.value
        else:
            turn_rank = None
            turn_suit = None

        if game_view.street() >= Street.RIVER and current_board.river is not None:
            river = current_board.river
            river_rank = river.rank.value
            river_suit = river.suit.value
        else:
            river_rank = None
            river_suit = None

        public_states.append(
            PublicState(
                current_player_index=a.player_index,
                street=game_view.street().value,
                current_player_mask=current_player_mask,
                folded_player_mask=game_view.is_folded(),
                all_in_player_mask=game_view.is_all_in(),
                stack_sizes=game_view.current_stack_sizes(),
                amount_to_call=game_view.amount_to_call(),
                min_raise_amount=game_view.min_bet_amount(),
                flop_0_rank=flop_0_rank,
                flop_0_suit=flop_0_suit,
                flop_1_rank=flop_1_rank,
                flop_1_suit=flop_1_suit,
                flop_2_rank=flop_2_rank,
                flop_2_suit=flop_2_suit,
                turn_rank=turn_rank,
                turn_suit=turn_suit,
                river_rank=river_rank,
                river_suit=river_suit,
            )
        )

    return public_states


def make_private_states(game: GameView, board: Board):
    private_states = []

    for i, a in iter_actions(game):
        game_view = game.view(i)
        # current_board = board.at_street(game_view.street())

        # TODO: Implement this
        private_states.append(PrivateState(-1, -1, -1))

    return private_states
