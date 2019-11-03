from pokermon.data import features
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


def test_basic_features():
    # A 3-player game that goes to the river.

    # Player 3 wins with a flopped set of jacks.
    deal = FullDeal(
        hole_cards=[mkhand("AcAd"), mkhand("AsKh"), mkhand("JcJh")],
        board=Board(flop=mkflop("KsJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = Game(starting_stacks=[100, 200, 300])

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

    evaluator = Evaluator()
    results = rules.get_result(deal, game.view(), evaluator)

    rows = features.make_rows(game, deal, results, evaluator)

    assert len(rows) == len(game.all_action())

    # The row where player 1 folds
    row = rows[9]
    assert row.current_player_mask == [0, 1, 0]
    assert row.all_in_player_mask == [0, 0, 0]
    assert row.folded_player_mask == [0, 0, 0]
    assert row.stack_sizes == [70, 190, 290]
    assert row.min_raise_amount == 20
    assert row.street == Street.TURN.value
    assert row.current_hand_type == HandType.PAIR.value
    assert row.river_rank == -1
    assert row.river_suit == -1
    assert row.action_encoded == Move.FOLD.value
    assert row.amount_added == 0
    assert row.instant_reward == 0
    assert row.cumulative_reward == 0
    assert row.won_hand is False

    # The river bet of player 3
    row = rows[-2]
    assert row.hole_card_0_rank == Rank.JACK.value
    assert row.hole_card_0_suit == Suit.CLUBS.value
    assert row.hole_card_1_rank == Rank.JACK.value
    assert row.hole_card_1_suit == Suit.HEARTS.value
    assert row.current_player_mask == [0, 0, 1]
    assert row.all_in_player_mask == [0, 0, 0]
    assert row.folded_player_mask == [0, 1, 0]
    assert row.stack_sizes == [70, 190, 270]
    assert row.amount_to_call == [0, 0, 0]
    assert row.min_raise_amount == 2
    assert row.street == Street.RIVER.value
    assert row.current_hand_type == HandType.TRIPS.value
    assert row.river_rank == Rank.SIX.value
    assert row.river_suit == Suit.SPADES.value
    assert row.action_encoded == Move.BET_RAISE.value
    assert row.amount_added == 30
    assert row.instant_reward == 100
    assert row.cumulative_reward == 100
    assert row.won_hand is True

    # The losing river call of player 0
    row = rows[-1]
    assert row.hole_card_0_rank == Rank.ACE.value
    assert row.hole_card_0_suit == Suit.CLUBS.value
    assert row.hole_card_1_rank == Rank.ACE.value
    assert row.hole_card_1_suit == Suit.DIAMONDS.value
    assert row.current_player_mask == [1, 0, 0]
    assert row.all_in_player_mask == [0, 0, 0]
    assert row.folded_player_mask == [0, 1, 0]
    assert row.stack_sizes == [70, 190, 240]
    assert row.amount_to_call == [30, 30, 0]
    assert row.min_raise_amount == 30
    assert row.street == Street.RIVER.value
    assert row.current_hand_type == HandType.PAIR.value
    assert row.river_rank == Rank.SIX.value
    assert row.river_suit == Suit.SPADES.value
    assert row.action_encoded == Move.CHECK_CALL.value
    assert row.amount_added == 30
    assert row.instant_reward == -30
    assert row.cumulative_reward == -30
    assert row.won_hand is False
