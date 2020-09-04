from pokermon.data import reenforcement_types
from pokermon.poker import rules
from pokermon.poker.cards import (
    Board,
    FullDeal,
    HandType,
    Rank,
    Suit,
    mkcard,
    mkflop,
    mkhand,
)
from pokermon.poker.evaluation import Evaluator
from pokermon.poker.game import Game, Move, Street


def test_full_game_features():
    # A 3-player game that goes to the river.

    # Player 3 wins with a flopped set of jacks.
    deal = FullDeal(
        hole_cards=[mkhand("AcAd"), mkhand("AsKh"), mkhand("JcJh")],
        board=Board(flop=mkflop("KsJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = Game(starting_stacks=[100, 200, 300])

    game.set_street(Street.PREFLOP)
    game.add_action(game.view().small_blind())
    game.add_action(game.view().big_blind())
    game.add_action(game.view().bet_raise(to=10))
    game.add_action(game.view().call())
    game.add_action(game.view().call())

    # Flop
    game.set_street(Street.FLOP)
    game.add_action(game.view().call())
    game.add_action(game.view().call())
    game.add_action(game.view().call())

    # Turn
    game.set_street(Street.TURN)
    game.add_action(game.view().bet_raise(to=20))
    game.add_action(game.view().fold())  # Action Index = 9
    game.add_action(game.view().call())

    # River
    game.set_street(Street.RIVER)
    game.add_action(game.view().call())
    game.add_action(game.view().bet_raise(to=30))
    game.add_action(game.view().call())

    game.end_hand()

    evaluator = Evaluator()
    results = rules.get_result(deal, game.view(), evaluator)

    _, rows = reenforcement_types.make_rows(game, deal, results, evaluator)

    # 12 decisions made throughout the hand
    assert len(rows) == 12

    # The row where player 2 bets preflop
    row = rows[0]
    assert row.state.current_player_mask == [0, 0, 1]
    assert row.state.all_in_player_mask == [0, 0, 0]
    assert row.state.folded_player_mask == [0, 0, 0]
    assert row.state.stack_sizes == [99, 198, 300]
    assert row.state.min_raise_amount == 2
    assert row.state.street == Street.PREFLOP.value
    assert row.state.current_hand_type == -1
    assert row.state.river_rank == -1
    assert row.state.river_suit == -1
    assert row.action.action_encoded == Move.BET_RAISE.value
    assert row.action.amount_added == 10
    assert row.reward.instant_reward == 0
    assert row.reward.cumulative_reward == 70
    assert row.reward.won_hand is True
    assert row.reward.is_players_last_action is False

    # The row where player 1 folds
    row = rows[7]
    assert row.state.current_player_mask == [0, 1, 0]
    assert row.state.all_in_player_mask == [0, 0, 0]
    assert row.state.folded_player_mask == [0, 0, 0]
    assert row.state.stack_sizes == [70, 190, 290]
    assert row.state.min_raise_amount == 20
    assert row.state.street == Street.TURN.value
    assert row.state.current_hand_type == HandType.PAIR.value
    assert row.state.river_rank == -1
    assert row.state.river_suit == -1
    assert row.action.action_encoded == Move.FOLD.value
    assert row.action.amount_added == 0
    assert row.reward.instant_reward == 0
    assert row.reward.cumulative_reward == 0
    assert row.reward.won_hand is False
    assert row.reward.is_players_last_action is True

    # The river bet of player 3
    row = rows[-2]
    assert row.state.hole_card_0_rank == Rank.JACK.value
    assert row.state.hole_card_0_suit == Suit.CLUBS.value
    assert row.state.hole_card_1_rank == Rank.JACK.value
    assert row.state.hole_card_1_suit == Suit.HEARTS.value
    assert row.state.current_player_mask == [0, 0, 1]
    assert row.state.all_in_player_mask == [0, 0, 0]
    assert row.state.folded_player_mask == [0, 1, 0]
    assert row.state.stack_sizes == [70, 190, 270]
    assert row.state.amount_to_call == [0, 0, 0]
    assert row.state.min_raise_amount == 2
    assert row.state.street == Street.RIVER.value
    assert row.state.current_hand_type == HandType.TRIPS.value
    assert row.state.river_rank == Rank.SIX.value
    assert row.state.river_suit == Suit.SPADES.value
    assert row.action.action_encoded == Move.BET_RAISE.value
    assert row.action.amount_added == 30
    assert row.reward.instant_reward == 100
    assert row.reward.cumulative_reward == 100
    assert row.reward.won_hand is True
    assert row.reward.is_players_last_action is True

    # The losing river call of player 0
    row = rows[-1]
    assert row.state.hole_card_0_rank == Rank.ACE.value
    assert row.state.hole_card_0_suit == Suit.CLUBS.value
    assert row.state.hole_card_1_rank == Rank.ACE.value
    assert row.state.hole_card_1_suit == Suit.DIAMONDS.value
    assert row.state.current_player_mask == [1, 0, 0]
    assert row.state.all_in_player_mask == [0, 0, 0]
    assert row.state.folded_player_mask == [0, 1, 0]
    assert row.state.stack_sizes == [70, 190, 240]
    assert row.state.amount_to_call == [30, 30, 0]
    assert row.state.min_raise_amount == 30
    assert row.state.street == Street.RIVER.value
    assert row.state.current_hand_type == HandType.PAIR.value
    assert row.state.river_rank == Rank.SIX.value
    assert row.state.river_suit == Suit.SPADES.value
    assert row.action.action_encoded == Move.CHECK_CALL.value
    assert row.action.amount_added == 30
    assert row.reward.instant_reward == -30
    assert row.reward.cumulative_reward == -30
    assert row.reward.won_hand is False
    assert row.reward.is_players_last_action is True


def test_fold_preflop_features():
    # A 3-player game that goes to the river.

    # Player 3 wins with a flopped set of jacks.
    deal = FullDeal(
        hole_cards=[mkhand("AcAd"), mkhand("AsKh"), mkhand("JcJh")],
        board=Board(flop=mkflop("KsJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = Game(starting_stacks=[100, 200, 300])

    game.set_street(Street.PREFLOP)
    game.add_action(game.view().small_blind())
    game.add_action(game.view().big_blind())
    game.add_action(game.view().bet_raise(to=10))
    game.add_action(game.view().fold())
    game.add_action(game.view().fold())

    game.end_hand()

    evaluator = Evaluator()
    results = rules.get_result(deal, game.view(), evaluator)

    _, rows = reenforcement_types.make_rows(game, deal, results, evaluator)

    assert len(rows) == 3

    # The row where player 3 raises preflop
    row = rows[0]
    assert row.state.current_player_mask == [0, 0, 1]
    assert row.state.all_in_player_mask == [0, 0, 0]
    assert row.state.folded_player_mask == [0, 0, 0]
    assert row.state.stack_sizes == [99, 198, 300]
    assert row.state.min_raise_amount == 2
    assert row.state.street == Street.PREFLOP.value
    assert row.state.current_hand_type == -1
    assert row.state.river_rank == -1
    assert row.state.river_suit == -1
    assert row.action.action_encoded == Move.BET_RAISE.value
    assert row.action.amount_added == 10
    assert row.reward.instant_reward == 3
    assert row.reward.cumulative_reward == 3
    assert row.reward.is_players_last_action is True
    assert row.reward.won_hand is True
    assert row.reward.is_players_last_action is True

    # The row where player 1 folds
    row = rows[1]
    assert row.state.current_player_mask == [1, 0, 0]
    assert row.state.all_in_player_mask == [0, 0, 0]
    assert row.state.folded_player_mask == [0, 0, 0]
    assert row.state.stack_sizes == [99, 198, 290]
    assert row.state.min_raise_amount == 8
    assert row.state.street == Street.PREFLOP.value
    assert row.state.current_hand_type == -1
    assert row.state.river_rank == -1
    assert row.state.river_suit == -1
    assert row.action.action_encoded == Move.FOLD.value
    assert row.action.amount_added == 0
    assert row.reward.instant_reward == 0
    assert row.reward.cumulative_reward == 0
    assert row.reward.won_hand is False
    assert row.reward.is_players_last_action is True

    # The row where player 2 folds
    row = rows[2]
    assert row.state.hole_card_0_rank == Rank.ACE.value
    assert row.state.hole_card_0_suit == Suit.SPADES.value
    assert row.state.hole_card_1_rank == Rank.KING.value
    assert row.state.hole_card_1_suit == Suit.HEARTS.value
    assert row.state.current_player_mask == [0, 1, 0]
    assert row.state.all_in_player_mask == [0, 0, 0]
    assert row.state.folded_player_mask == [1, 0, 0]
    assert row.state.stack_sizes == [99, 198, 290]
    assert row.state.amount_to_call == [9, 8, 0]
    assert row.state.min_raise_amount == 8
    assert row.state.street == Street.PREFLOP.value
    assert row.state.current_hand_type == -1
    assert row.state.river_rank == -1
    assert row.state.river_suit == -1
    assert row.action.action_encoded == Move.FOLD.value
    assert row.action.amount_added == 0
    assert row.reward.instant_reward == 0
    assert row.reward.cumulative_reward == 0
    assert row.reward.won_hand is False
    assert row.reward.is_players_last_action is True
