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
from pokermon.poker.game import Move, Street
from pokermon.poker.game_runner import GameRunner


def test_full_game_features():
    # A 3-player game that goes to the river.

    # Player 3 wins with a flopped set of jacks.
    deal = FullDeal(
        hole_cards=[mkhand("AcAd"), mkhand("AsKh"), mkhand("JcJh")],
        board=Board(flop=mkflop("KsJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = GameRunner(starting_stacks=[300, 300, 300])
    game.start_game()

    # Preflop
    game.bet_raise(to=10)
    game.call()
    game.call()

    # Flop
    game.check()
    game.check()
    game.check()

    # Turn
    game.bet_raise(to=20)
    game.fold()
    game.call()

    # River
    game.check()
    game.bet_raise(to=30)
    game.call()

    # Player 0 loses with Aces.  They called 10 on the flop, bet 20 on te turn, and called 30 on
    # the river. Player 1 called 10 on the flop but folded the turn. Player 2 wins with a flush.
    # They called 10 on the flop, called 20 on the turn, and bet 30 on the river. Player 2 should
    # net 2*10 + 20 + 30 = 70 total.  The total pot at the end is 3*10 + 2*20 + 2*30 = 130

    evaluator = Evaluator()
    results = rules.get_result(deal, game.game_view(), evaluator)

    _, rows = reenforcement_types.make_rows(game.game, deal, results, evaluator)

    # 12 decisions made throughout the hand
    assert len(rows) == 12

    # The row where player 2 bets preflop
    row = rows[0]
    assert row.state.current_player_mask == [0, 0, 1]
    assert row.state.all_in_player_mask == [0, 0, 0]
    assert row.state.folded_player_mask == [0, 0, 0]
    assert row.state.stack_sizes == [299, 298, 300]
    assert row.state.min_raise_amount == 2
    assert row.state.street == Street.PREFLOP.value
    assert row.state.current_hand_type == -1
    assert row.state.river_rank == -1
    assert row.state.river_suit == -1
    assert row.action.action_encoded == Move.BET_RAISE.value
    assert row.action.amount_added == 10
    assert row.reward.instant_reward == -10
    assert row.reward.cumulative_reward == 70
    assert row.reward.won_hand is True
    assert row.reward.is_players_last_action is False

    # The row where player 1 folds
    row = rows[7]
    assert row.state.current_player_mask == [0, 1, 0]
    assert row.state.all_in_player_mask == [0, 0, 0]
    assert row.state.folded_player_mask == [0, 0, 0]
    assert row.state.stack_sizes == [270, 290, 290]
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
    assert row.state.stack_sizes == [270, 290, 270]
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
    assert row.state.stack_sizes == [270, 290, 240]
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

    game = GameRunner(starting_stacks=[300, 300, 300])
    game.start_game()
    game.bet_raise(to=10)
    game.fold()
    game.fold()

    evaluator = Evaluator()
    results = rules.get_result(deal, game.game_view(), evaluator)

    _, rows = reenforcement_types.make_rows(game.game, deal, results, evaluator)

    assert len(rows) == 3

    # The row where player 3 raises preflop
    row = rows[0]
    assert row.state.current_player_mask == [0, 0, 1]
    assert row.state.all_in_player_mask == [0, 0, 0]
    assert row.state.folded_player_mask == [0, 0, 0]
    assert row.state.stack_sizes == [299, 298, 300]
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
    assert row.state.stack_sizes == [299, 298, 290]
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
    assert row.state.stack_sizes == [299, 298, 290]
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
