# from pokermon.data import reenforcement_types
from pokermon.data.action import make_actions
from pokermon.data.context import (
    PublicContext,
    make_private_context,
    make_public_context,
)
from pokermon.data.examples import make_example, seq_example_to_dict
from pokermon.data.rewards import make_rewards, make_target
from pokermon.data.state import PublicState, make_public_states
from pokermon.poker import rules
from pokermon.poker.cards import Board, FullDeal, mkcard, mkflop, mkhand
from pokermon.poker.game_runner import GameRunner


def test_context() -> None:
    example = make_example(
        public_context=PublicContext(num_players=4, starting_stack_sizes=[1, 2, 3, 4])
    )

    assert seq_example_to_dict(example) == {
        "context": {
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
                current_player_index=0,
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
                current_player_index=1,
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
        "context": {},
        "features": {
            "public_state__all_in_player_mask": [[0, 0, 0], [1, 0, 0]],
            "public_state__amount_to_call": [[10, 10, 15], [5, 0, 5]],
            "public_state__current_player_index": [[0], [1]],
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

    example = make_example(
        public_context=make_public_context(game.game),
        private_context=make_private_context(deal.hole_cards[1]),
        target=make_target(deal, results),
        public_states=make_public_states(game.game, deal.board),
        private_states=None,
        actions=make_actions(game.game),
        rewards=make_rewards(game.game, results),
    )
    example_dict = seq_example_to_dict(example)

    assert example_dict == {
        "context": {
            "public_context__num_players": [3],
            "private_context__hole_card_0_rank": [14],
            "target__hole_cards": [12, 168, 9],
            "private_context__hole_card_1_rank": [13],
            "target__total_rewards": [-1, -2, 3],
            "public_context__starting_stack_sizes": [200, 250, 100],
            "private_context__hole_card_1_suit": [4],
            "private_context__hole_card_0_suit": [1],
        },
        "features": {
            "public_state__street": [[1], [1], [1]],
            "action__action_index": [[3], [4], [5]],
            "public_state__turn_suit": [[-1], [-1], [-1]],
            "public_state__stack_sizes": [
                [199, 248, 100],
                [199, 248, 90],
                [199, 248, 90],
            ],
            "public_state__river_suit": [[-1], [-1], [-1]],
            "reward__cumulative_reward": [[3], [0], [0]],
            "public_state__folded_player_mask": [[0, 0, 0], [0, 0, 0], [1, 0, 0]],
            "public_state__flop_1_rank": [[-1], [-1], [-1]],
            "action__amount_added": [[10], [0], [0]],
            "reward__instant_reward": [[3], [0], [0]],
            "public_state__amount_to_call": [[1, 0, 2], [9, 8, 0], [9, 8, 0]],
            "reward__is_players_last_action": [[1], [1], [1]],
            "public_state__all_in_player_mask": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            "public_state__flop_0_suit": [[-1], [-1], [-1]],
            "public_state__flop_1_suit": [[-1], [-1], [-1]],
            "public_state__min_raise_amount": [[2], [8], [8]],
            "reward__won_hand": [[1], [0], [0]],
            "public_state__current_player_mask": [[0, 0, 1], [1, 0, 0], [0, 1, 0]],
            "public_state__river_rank": [[-1], [-1], [-1]],
            "public_state__flop_0_rank": [[-1], [-1], [-1]],
            "public_state__flop_2_suit": [[-1], [-1], [-1]],
            "public_state__current_player_index": [[2], [0], [1]],
            "public_state__turn_rank": [[-1], [-1], [-1]],
            "action__action_encoded": [[5], [3], [3]],
            "public_state__flop_2_rank": [[-1], [-1], [-1]],
        },
    }

    # assert example_dict["context"]["num_players"] == [3]
    # assert example_dict["context"]["starting_stack_sizes"] == [200, 200, 200]
    #
    # # Player 3 (UTG) wins the blinds, the others lose their blinds
    # assert example_dict["context"]["total_rewards"] == [-1, -2, 3]
    #
    # # Bet, Fold, Fold
    # assert example_dict["features"]["action__action_encoded"] == [[5], [3], [3]]
    #
    # # Bet 10, fold, fold
    # assert example_dict["features"]["action__amount_added"] == [[10], [0], [0]]
    #
    # # These are the states before the action (the blinds have already taken place)
    # assert example_dict["features"]["state__stack_sizes"] == [
    #     [199, 198, 200],
    #     [199, 198, 190],
    #     [199, 198, 190],
    # ]
    #
    # # Hole Cards 0: Jc Ac As
    # # Hole Cards 1: Jh Ad Kh
    # assert example_dict["features"]["state__hole_card_0_rank"] == [[11], [14], [14]]
    # assert example_dict["features"]["state__hole_card_0_suit"] == [[2], [2], [1]]
    # assert example_dict["features"]["state__hole_card_1_rank"] == [[11], [14], [13]]
    # assert example_dict["features"]["state__hole_card_1_suit"] == [[4], [3], [4]]
    #
    # # These are the indices of the actions
    # assert example_dict["features"]["state__action_index"] == [[3], [4], [5]]


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

    example = make_example(
        public_context=make_public_context(game.game),
        private_context=make_private_context(deal.hole_cards[1]),
        target=make_target(deal, results),
        public_states=make_public_states(game.game, deal.board),
        private_states=None,
        actions=make_actions(game.game),
        rewards=make_rewards(game.game, results),
    )
    example_dict = seq_example_to_dict(example)

    print(example_dict)

    assert example_dict == {
        "context": {
            "private_context__hole_card_0_rank": [13],
            "private_context__hole_card_0_suit": [2],
            "target__total_rewards": [250, -225, -25, 0],
            "public_context__num_players": [4],
            "private_context__hole_card_1_suit": [3],
            "target__hole_cards": [168, 140, 3, 36],
            "public_context__starting_stack_sizes": [300, 300, 300, 300],
            "private_context__hole_card_1_rank": [10],
        },
        "features": {
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
            "action__action_encoded": [
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
            "action__action_index": [
                [3],
                [4],
                [5],
                [6],
                [7],
                [9],
                [10],
                [11],
                [13],
                [14],
                [15],
                [17],
                [18],
                [19],
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
            "public_state__current_player_index": [
                [2],
                [3],
                [0],
                [1],
                [2],
                [0],
                [1],
                [2],
                [0],
                [1],
                [0],
                [0],
                [1],
                [0],
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
            "action__amount_added": [
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
        },
    }

    assert example_dict["features"]["action__action_encoded"] == [
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
    ]

    assert example_dict["features"]["action__amount_added"] == [
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
    ]

    # These are the states before the action (the blinds have already taken place)
    assert example_dict["features"]["public_state__stack_sizes"] == [
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
    ]

    # These are the indices of the actions
    assert example_dict["features"]["action__action_index"] == [
        [3],
        [4],
        [5],
        [6],
        [7],
        [9],
        [10],
        [11],
        [13],
        [14],
        [15],
        [17],
        [18],
        [19],
    ]
