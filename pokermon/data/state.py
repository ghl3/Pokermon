# There is a State per-action.
# There are two types of state:
# - Public State: The state anyone watching the game would know
# - Private State: The state that requires knowing someone's hole cards
from dataclasses import dataclass
from typing import List, Optional


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
