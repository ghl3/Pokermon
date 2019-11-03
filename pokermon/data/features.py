from dataclasses import dataclass
from typing import List

from pokermon.poker import rules
from pokermon.poker.cards import FullDeal
from pokermon.poker.evaluation import Evaluator
from pokermon.poker.game import Action, Game, Street
from pokermon.poker.rules import GameResults


@dataclass(frozen=True)
class Row:
    #
    # State Features
    #

    num_players: int
    street: int
    current_player_mask: List[int]
    stack_sizes: List[int]

    amount_to_call: int
    min_raise_amount: int

    # Cards are ordered by:
    # Rank, [S, C, D, H]
    hole_card_0_rank: int
    hole_card_0_suit: int
    hole_card_1_rank: int
    hole_card_1_suit: int

    flop_0_rank: int
    flop_0_suit: int
    flop_1_rank: int
    flop_1_suit: int
    flop_2_rank: int
    flop_2_suit: int
    turn_rank: int
    turn_suit: int
    river_rank: int
    river_suit: int

    current_hand_type: int
    current_hand_strength: float
    current_hand_rank: int

    #
    # Action Features
    #

    action_encoded: int
    amount_added: int

    #
    # Targets
    #

    # The amount earned as a result of this move.  Will be negative if the player
    # bets on this turn and it isn't their last turn.  May be negative or positive
    # if it's their last turn (depending on whether they bet and whether they win).
    instant_reward: int

    # The net amount the player earns or loses for the rest of the hand, including
    # the result of the current action (a bet/raise).
    cumulative_reward: int

    won_hand: bool


def make_rows(
    game: Game, deal: FullDeal, results: GameResults, evaluator: Evaluator
) -> List[Row]:
    rows = []

    # Profits at the end of the game
    cumulative_rewards: List[int] = results.winnings

    is_last_action: List[bool] = [True for _ in range(game.num_players())]

    for i, e in reversed(list(enumerate(game.events))):

        if isinstance(e, Action):
            a = e
        else:
            continue

        # Subtract the amount lost after taking the given action, which is a part
        # of the future cumulative winnings / losses
        # print(cumulative_rewards, a.player_index, a.amount_added)
        cumulative_rewards[a.player_index] -= a.amount_added

        game_view = game.view(i)

        num_players = game.num_players()
        current_player_mask = [0 for _ in range(num_players)]
        current_player_mask[a.player_index] = 1

        hc_0, hc_1 = sorted(deal.hole_cards[a.player_index])

        hole_card_0_rank = hc_0.rank.value
        hole_card_0_suit = hc_0.suit.value
        hole_card_1_rank = hc_1.rank.value
        hole_card_1_suit = hc_1.suit.value

        if game_view.street() >= Street.FLOP and deal.board.flop is not None:
            flop_0, flop_1, flop_2 = sorted(deal.board.flop)
            flop_0_rank = flop_0.rank.value
            flop_0_suit = flop_0.suit.value
            flop_1_rank = flop_1.rank.value
            flop_1_suit = flop_1.suit.value
            flop_2_rank = flop_2.rank.value
            flop_2_suit = flop_2.suit.value
        else:
            flop_0_rank = -1
            flop_0_suit = -1
            flop_1_rank = -1
            flop_1_suit = -1
            flop_2_rank = -1
            flop_2_suit = -1

        if game_view.street() >= Street.TURN and deal.board.turn is not None:
            turn = deal.board.turn
            turn_rank = turn.rank.value
            turn_suit = turn.suit.value
        else:
            turn_rank = -1
            turn_suit = -1

        if game_view.street() >= Street.RIVER and deal.board.turn is not None:
            river = deal.board.turn
            river_rank = river.rank.value
            river_suit = river.suit.value
        else:
            river_rank = -1
            river_suit = -1

        board_at_street = deal.board.at_street(game_view.street())

        if game_view.street() >= Street.FLOP:
            evaluation_result = evaluator.evaluate(
                deal.hole_cards[a.player_index], board_at_street
            )
            current_hand_strength = evaluation_result.percentage
            current_hand_type = evaluation_result.hand_type.value
            current_hand_rank = evaluation_result.rank
        else:
            current_hand_strength = -1
            current_hand_type = -1
            current_hand_rank = -1

        instant_reward = 0
        if is_last_action[a.player_index]:
            instant_reward = results.winnings[a.player_index]

        won_hand = a.player_index in set(results.best_hand_index)

        row = Row(
            num_players=game.num_players(),
            stack_sizes=game_view.current_stack_sizes(),
            current_player_mask=current_player_mask,
            street=game_view.street().value,
            amount_to_call=game_view.amount_to_call(),
            min_raise_amount=rules.min_bet_amount(game_view),
            hole_card_0_rank=hole_card_0_rank,
            hole_card_0_suit=hole_card_0_suit,
            hole_card_1_rank=hole_card_1_rank,
            hole_card_1_suit=hole_card_1_suit,
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
            current_hand_strength=current_hand_strength,
            current_hand_type=current_hand_type,
            current_hand_rank=current_hand_rank,
            action_encoded=a.move.value,
            amount_added=a.amount_added,
            cumulative_reward=cumulative_rewards[a.player_index],
            instant_reward=instant_reward,
            won_hand=won_hand,
        )

        rows.append(row)

        is_last_action[a.player_index] = False

    return list(reversed(rows))
