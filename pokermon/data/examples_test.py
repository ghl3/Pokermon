# from pokermon.data import reenforcement_types
from pokermon.data.action import make_last_actions, make_next_actions
from pokermon.data.context import (
    PublicContext,
    make_private_context,
    make_public_context,
)
from pokermon.data.examples import make_example, seq_example_to_dict
from pokermon.data.player_state import make_player_states
from pokermon.data.public_state import PublicState, make_public_states
from pokermon.data.rewards import make_rewards
from pokermon.data.target import make_target
from pokermon.poker import rules
from pokermon.poker.cards import Board, FullDeal, mkcard, mkflop, mkhand
from pokermon.poker.game_runner import GameRunner


def test_context() -> None:
    example = make_example(
        public_context=PublicContext(num_players=4, starting_stack_sizes=[1, 2, 3, 4])
    )

    assert seq_example_to_dict(example) == {
        "context": {
            "num_steps": [0],
            "public_context__num_players": [4],
            "public_context__starting_stack_sizes": [
                1,
                2,
                3,
                4,
            ],
        },
        "features": {},
    }


def test_state() -> None:
    example = make_example(
        public_states=[
            PublicState(
                street=0,
                current_player_mask=[1, 0, 0],
                folded_player_mask=[0, 0, 0],
                all_in_player_mask=[0, 0, 0],
                stack_sizes=[1, 2, 3],
                amount_to_call=[10, 10, 15],
                min_raise_amount=12,
                flop_0_rank=None,
                flop_0_suit=None,
                flop_1_rank=None,
                flop_1_suit=None,
                flop_2_rank=None,
                flop_2_suit=None,
                turn_rank=None,
                turn_suit=None,
                river_rank=None,
                river_suit=None,
            ),
            PublicState(
                street=2,
                current_player_mask=[0, 1, 0],
                folded_player_mask=[0, 0, 1],
                all_in_player_mask=[1, 0, 0],
                stack_sizes=[10, 20, 30],
                amount_to_call=[5, 0, 5],
                min_raise_amount=40,
                flop_0_rank=None,
                flop_0_suit=None,
                flop_1_rank=None,
                flop_1_suit=None,
                flop_2_rank=None,
                flop_2_suit=None,
                turn_rank=None,
                turn_suit=None,
                river_rank=None,
                river_suit=None,
            ),
        ]
    )

    assert seq_example_to_dict(example) == {
        "context": {"num_steps": [2]},
        "features": {
            "public_state__all_in_player_mask": [[0, 0, 0], [1, 0, 0]],
            "public_state__amount_to_call": [[10, 10, 15], [5, 0, 5]],
            "public_state__current_player_mask": [[1, 0, 0], [0, 1, 0]],
            "public_state__flop_0_rank": [[-1], [-1]],
            "public_state__flop_0_suit": [[-1], [-1]],
            "public_state__flop_1_rank": [[-1], [-1]],
            "public_state__flop_1_suit": [[-1], [-1]],
            "public_state__flop_2_rank": [[-1], [-1]],
            "public_state__flop_2_suit": [[-1], [-1]],
            "public_state__folded_player_mask": [[0, 0, 0], [0, 0, 1]],
            "public_state__min_raise_amount": [[12], [40]],
            "public_state__river_rank": [[-1], [-1]],
            "public_state__river_suit": [[-1], [-1]],
            "public_state__stack_sizes": [[1, 2, 3], [10, 20, 30]],
            "public_state__street": [[0], [2]],
            "public_state__turn_rank": [[-1], [-1]],
            "public_state__turn_suit": [[-1], [-1]],
        },
    }


def test_fold_preflop() -> None:
    # Player 3 wins with a flopped set of jacks.
    deal = FullDeal(
        hole_cards=[mkhand("AcAd"), mkhand("AsKh"), mkhand("JcJh")],
        board=Board(flop=mkflop("KsJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = GameRunner(starting_stacks=[200, 250, 100])
    game.start_game()
    game.bet_raise(to=10)
    game.fold()
    game.fold()

    results = rules.get_result(deal, game.game_view())

    player_index = 1

    example = make_example(
        public_context=make_public_context(game.game_view()),
        private_context=make_private_context(deal.hole_cards[1]),
        target=make_target(deal, results),
        public_states=make_public_states(game.game_view(), deal.board),
        player_states=make_player_states(
            player_index, game.game_view(), deal.hole_cards[player_index], deal.board
        ),
        last_actions=make_last_actions(game.game_view()),
        next_actions=make_next_actions(game.game_view()),
        rewards=make_rewards(game.game_view(), results),
    )
    example_dict = seq_example_to_dict(example)

    assert example_dict == {
        "context": {
            "num_steps": [3],
            "private_context__hand_encoded": [168],
            "private_context__hole_card_0_rank": [14],
            "private_context__hole_card_0_suit": [1],
            "private_context__hole_card_1_rank": [13],
            "private_context__hole_card_1_suit": [4],
            "public_context__num_players": [3],
            "public_context__starting_stack_sizes": [200, 250, 100],
            "target__hole_cards": [12, 168, 9],
            "target__total_rewards": [-1, -2, 3],
        },
        "features": {
            "last_action__action_encoded": [[-1], [4], [0]],
            "last_action__amount_added": [[-1], [10], [0]],
            "last_action__amount_added_percent_of_remaining": [[-1], [10], [0]],
            "last_action__amount_raised": [[-1], [8], [0]],
            "last_action__amount_raised_percent_of_pot": [[-1], [266], [0]],
            "last_action__move": [[-1], [5], [3]],
            "next_action__action_encoded": [[4], [0], [0]],
            "next_action__amount_added": [[10], [0], [0]],
            "next_action__amount_raised": [[8], [0], [0]],
            "next_action__move": [[5], [3], [3]],
            "next_action__new_total_bet": [[10], [10], [10]],
            "player_state__current_hand_rank": [[-1], [-1], [-1]],
            "player_state__current_hand_strength": [[-1.0], [-1.0], [-1.0]],
            "player_state__current_hand_type": [[-1], [-1], [-1]],
            "player_state__current_player_offset": [[1], [-1], [0]],
            "player_state__is_current_player": [[0], [0], [1]],
            "player_state__num_hands_better": [[-1], [-1], [-1]],
            "player_state__num_hands_tied": [[-1], [-1], [-1]],
            "player_state__num_hands_worse": [[-1], [-1], [-1]],
            "player_state__win_prob_vs_random": [[-1.0], [-1.0], [-1.0]],
            "public_state__all_in_player_mask": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            "public_state__amount_to_call": [[1, 0, 2], [9, 8, 0], [9, 8, 0]],
            "public_state__current_player_mask": [[0, 0, 1], [1, 0, 0], [0, 1, 0]],
            "public_state__flop_0_rank": [[-1], [-1], [-1]],
            "public_state__flop_0_suit": [[-1], [-1], [-1]],
            "public_state__flop_1_rank": [[-1], [-1], [-1]],
            "public_state__flop_1_suit": [[-1], [-1], [-1]],
            "public_state__flop_2_rank": [[-1], [-1], [-1]],
            "public_state__flop_2_suit": [[-1], [-1], [-1]],
            "public_state__folded_player_mask": [[0, 0, 0], [0, 0, 0], [1, 0, 0]],
            "public_state__min_raise_amount": [[2], [8], [8]],
            "public_state__river_rank": [[-1], [-1], [-1]],
            "public_state__river_suit": [[-1], [-1], [-1]],
            "public_state__stack_sizes": [
                [199, 248, 100],
                [199, 248, 90],
                [199, 248, 90],
            ],
            "public_state__street": [[1], [1], [1]],
            "public_state__turn_rank": [[-1], [-1], [-1]],
            "public_state__turn_suit": [[-1], [-1], [-1]],
            "reward__cumulative_reward": [[3], [0], [0]],
            "reward__instant_reward": [[3], [0], [0]],
            "reward__is_players_last_action": [[1], [1], [1]],
            "reward__won_hand": [[1], [0], [0]],
        },
    }


def test_full_hand() -> None:
    # Player 3 wins with a flopped set of jacks.
    deal = FullDeal(
        hole_cards=[mkhand("AhKs"), mkhand("Kc10d"), mkhand("5h5c"), mkhand("7s3d")],
        board=Board(flop=mkflop("KdJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = GameRunner(starting_stacks=[300, 300, 300, 300])
    game.start_game()

    # Preflop
    game.bet_raise(to=10)
    game.fold()
    game.bet_raise(to=25)
    game.call()
    game.call()

    # Flop
    game.bet_raise(to=40)
    game.call()
    game.fold()

    # Turn
    game.check()
    game.bet_raise(to=60)
    game.call()

    # River
    game.check()
    game.bet_raise(to=100)
    game.call()

    results = rules.get_result(deal, game.game_view())

    player_index = 1

    example = make_example(
        public_context=make_public_context(game.game_view()),
        private_context=make_private_context(deal.hole_cards[1]),
        target=make_target(deal, results),
        public_states=make_public_states(game.game_view(), deal.board),
        player_states=make_player_states(
            player_index, game.game_view(), deal.hole_cards[player_index], deal.board
        ),
        last_actions=make_last_actions(game.game_view()),
        next_actions=make_next_actions(game.game_view()),
        rewards=make_rewards(game.game_view(), results),
    )
    example_dict = seq_example_to_dict(example)

    assert example_dict == {
        "context": {
            "num_steps": [14],
            "private_context__hand_encoded": [140],
            "private_context__hole_card_0_rank": [13],
            "private_context__hole_card_0_suit": [2],
            "private_context__hole_card_1_rank": [10],
            "private_context__hole_card_1_suit": [3],
            "public_context__num_players": [4],
            "public_context__starting_stack_sizes": [300, 300, 300, 300],
            "target__hole_cards": [168, 140, 3, 36],
            "target__total_rewards": [250, -225, -25, 0],
        },
        "features": {
            "last_action__action_encoded": [
                [-1],
                [3],
                [0],
                [3],
                [1],
                [1],
                [5],
                [1],
                [0],
                [1],
                [7],
                [1],
                [1],
                [14],
            ],
            "last_action__amount_added": [
                [-1],
                [10],
                [0],
                [24],
                [23],
                [15],
                [40],
                [40],
                [0],
                [0],
                [60],
                [60],
                [0],
                [100],
            ],
            "last_action__amount_added_percent_of_remaining": [
                [-1],
                [3],
                [0],
                [8],
                [7],
                [5],
                [14],
                [14],
                [0],
                [0],
                [25],
                [25],
                [0],
                [57],
            ],
            "last_action__amount_raised": [
                [-1],
                [8],
                [0],
                [15],
                [0],
                [0],
                [40],
                [0],
                [0],
                [0],
                [60],
                [0],
                [0],
                [100],
            ],
            "last_action__amount_raised_percent_of_pot": [
                [-1],
                [266],
                [0],
                [115],
                [0],
                [0],
                [53],
                [0],
                [0],
                [0],
                [38],
                [0],
                [0],
                [36],
            ],
            "last_action__move": [
                [-1],
                [5],
                [3],
                [5],
                [4],
                [4],
                [5],
                [4],
                [3],
                [4],
                [5],
                [4],
                [4],
                [5],
            ],
            "next_action__action_encoded": [
                [3],
                [0],
                [3],
                [1],
                [1],
                [5],
                [1],
                [0],
                [1],
                [7],
                [1],
                [1],
                [14],
                [1],
            ],
            "next_action__amount_added": [
                [10],
                [0],
                [24],
                [23],
                [15],
                [40],
                [40],
                [0],
                [0],
                [60],
                [60],
                [0],
                [100],
                [100],
            ],
            "next_action__amount_raised": [
                [8],
                [0],
                [15],
                [0],
                [0],
                [40],
                [0],
                [0],
                [0],
                [60],
                [0],
                [0],
                [100],
                [0],
            ],
            "next_action__move": [
                [5],
                [3],
                [5],
                [4],
                [4],
                [5],
                [4],
                [3],
                [4],
                [5],
                [4],
                [4],
                [5],
                [4],
            ],
            "next_action__new_total_bet": [
                [10],
                [10],
                [25],
                [25],
                [25],
                [40],
                [40],
                [40],
                [0],
                [60],
                [60],
                [0],
                [100],
                [100],
            ],
            "player_state__current_hand_rank": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [3652],
                [-1],
                [-1],
                [3648],
                [-1],
                [-1],
                [3648],
                [-1],
            ],
            "player_state__current_hand_strength": [
                [-1.0],
                [-1.0],
                [-1.0],
                [-1.0],
                [-1.0],
                [-1.0],
                [0.5105869770050049],
                [-1.0],
                [-1.0],
                [0.51112300157547],
                [-1.0],
                [-1.0],
                [0.51112300157547],
                [-1.0],
            ],
            "player_state__current_hand_type": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [2],
                [-1],
                [-1],
                [2],
                [-1],
                [-1],
                [2],
                [-1],
            ],
            "player_state__current_player_offset": [
                [1],
                [2],
                [-1],
                [0],
                [1],
                [-1],
                [0],
                [1],
                [-1],
                [0],
                [-1],
                [-1],
                [0],
                [-1],
            ],
            "player_state__is_current_player": [
                [0],
                [0],
                [0],
                [1],
                [0],
                [0],
                [1],
                [0],
                [0],
                [1],
                [0],
                [0],
                [1],
                [0],
            ],
            "player_state__num_hands_better": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [66],
                [-1],
                [-1],
                [96],
                [-1],
                [-1],
                [192],
                [-1],
            ],
            "player_state__num_hands_tied": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [11],
                [-1],
                [-1],
                [11],
                [-1],
                [-1],
                [10],
                [-1],
            ],
            "player_state__num_hands_worse": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [1098],
                [-1],
                [-1],
                [1020],
                [-1],
                [-1],
                [878],
                [-1],
            ],
            "player_state__win_prob_vs_random": [
                [-1.0],
                [-1.0],
                [-1.0],
                [-1.0],
                [-1.0],
                [-1.0],
                [0.828000009059906],
                [-1.0],
                [-1.0],
                [0.8389999866485596],
                [-1.0],
                [-1.0],
                [0.8029999732971191],
                [-1.0],
            ],
            "public_state__all_in_player_mask": [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            "public_state__amount_to_call": [
                [1, 0, 2, 2],
                [9, 8, 0, 10],
                [9, 8, 0, 10],
                [0, 23, 15, 25],
                [0, 0, 15, 25],
                [0, 0, 0, 0],
                [0, 40, 40, 40],
                [0, 0, 40, 40],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [60, 0, 60, 60],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [100, 0, 100, 100],
            ],
            "public_state__current_player_mask": [
                [0, 0, 1, 0],
                [0, 0, 0, 1],
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [1, 0, 0, 0],
            ],
            "public_state__flop_0_rank": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [13],
                [13],
                [13],
                [13],
                [13],
                [13],
                [13],
                [13],
                [13],
            ],
            "public_state__flop_0_suit": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [3],
                [3],
                [3],
                [3],
                [3],
                [3],
                [3],
                [3],
                [3],
            ],
            "public_state__flop_1_rank": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [11],
                [11],
                [11],
                [11],
                [11],
                [11],
                [11],
                [11],
                [11],
            ],
            "public_state__flop_1_suit": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [1],
                [1],
                [1],
                [1],
                [1],
                [1],
                [1],
                [1],
                [1],
            ],
            "public_state__flop_2_rank": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [3],
                [3],
                [3],
                [3],
                [3],
                [3],
                [3],
                [3],
                [3],
            ],
            "public_state__flop_2_suit": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [3],
                [3],
                [3],
                [3],
                [3],
                [3],
                [3],
                [3],
                [3],
            ],
            "public_state__folded_player_mask": [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
            ],
            "public_state__min_raise_amount": [
                [2],
                [8],
                [8],
                [15],
                [15],
                [2],
                [40],
                [40],
                [2],
                [2],
                [60],
                [2],
                [2],
                [100],
            ],
            "public_state__river_rank": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [6],
                [6],
                [6],
            ],
            "public_state__river_suit": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [1],
                [1],
                [1],
            ],
            "public_state__stack_sizes": [
                [299, 298, 300, 300],
                [299, 298, 290, 300],
                [299, 298, 290, 300],
                [275, 298, 290, 300],
                [275, 275, 290, 300],
                [275, 275, 275, 300],
                [235, 275, 275, 300],
                [235, 235, 275, 300],
                [235, 235, 275, 300],
                [235, 235, 275, 300],
                [235, 175, 275, 300],
                [175, 175, 275, 300],
                [175, 175, 275, 300],
                [175, 75, 275, 300],
            ],
            "public_state__street": [
                [1],
                [1],
                [1],
                [1],
                [1],
                [2],
                [2],
                [2],
                [3],
                [3],
                [3],
                [4],
                [4],
                [4],
            ],
            "public_state__turn_rank": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [7],
                [7],
                [7],
                [7],
                [7],
                [7],
            ],
            "public_state__turn_suit": [
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [-1],
                [1],
                [1],
                [1],
                [1],
                [1],
                [1],
            ],
            "reward__cumulative_reward": [
                [-25],
                [0],
                [251],
                [-223],
                [-15],
                [275],
                [-200],
                [0],
                [315],
                [-160],
                [315],
                [375],
                [-100],
                [375],
            ],
            "reward__instant_reward": [
                [-10],
                [0],
                [-24],
                [-23],
                [-15],
                [-40],
                [-40],
                [0],
                [0],
                [-60],
                [-60],
                [0],
                [-100],
                [375],
            ],
            "reward__is_players_last_action": [
                [0],
                [1],
                [0],
                [0],
                [0],
                [0],
                [0],
                [1],
                [0],
                [0],
                [0],
                [0],
                [1],
                [1],
            ],
            "reward__won_hand": [
                [0],
                [0],
                [1],
                [0],
                [0],
                [1],
                [0],
                [0],
                [1],
                [0],
                [1],
                [1],
                [0],
                [1],
            ],
        },
    }
