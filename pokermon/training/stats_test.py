from pokermon.poker import result
from pokermon.poker.board import Board, mkflop
from pokermon.poker.cards import mkcard
from pokermon.poker.deal import FullDeal
from pokermon.poker.game_runner import GameRunner
from pokermon.poker.hands import mkhand
from pokermon.training.stats import Stats


def test_fold_preflop() -> None:
    # Player 3 wins with a flopped set of jacks.
    deal = FullDeal(
        hole_cards=[mkhand("AcAd"), mkhand("AsKh"), mkhand("JcJh")],
        board=Board(flop=mkflop("KsJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = GameRunner(starting_stacks=[200, 250, 300])
    game.start_game()
    game.bet_raise(to=10)
    game.fold()
    game.fold()

    results = result.get_result(deal, game.game_view())

    s = Stats()
    s.update_stats(game.game_view(), results, player_id=0)
    assert s == Stats(
        num_hands=1,
        reward=-1,
        num_wins=0,
        num_losses=1,
        num_flops=0,
        num_turns=0,
        num_rivers=0,
        num_showdowns=0,
        num_decisions=1,
        num_check=0,
        num_call=0,
        total_amount_called=0,
        num_bet=0,
        total_amount_bet=0,
        num_fold=1,
    )

    s = Stats()
    s.update_stats(game.game_view(), results, player_id=1)
    assert s == Stats(
        num_hands=1,
        reward=-2,
        num_wins=0,
        num_losses=1,
        num_flops=0,
        num_turns=0,
        num_rivers=0,
        num_showdowns=0,
        num_decisions=1,
        num_check=0,
        num_call=0,
        total_amount_called=0,
        num_bet=0,
        total_amount_bet=0,
        num_fold=1,
    )

    s = Stats()
    s.update_stats(game.game_view(), results, player_id=2)
    assert s == Stats(
        num_hands=1,
        reward=3,
        num_wins=1,
        num_losses=0,
        num_flops=0,
        num_turns=0,
        num_rivers=0,
        num_showdowns=0,
        num_decisions=1,
        num_check=0,
        num_call=0,
        total_amount_called=0,
        num_bet=1,
        total_amount_bet=10,
        num_fold=0,
    )


def test_fold_turn() -> None:
    # Player 3 wins with a flopped set of jacks.
    deal = FullDeal(
        hole_cards=[mkhand("AcAd"), mkhand("AsKh"), mkhand("JcJh")],
        board=Board(flop=mkflop("KsJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = GameRunner(starting_stacks=[200, 250, 300])
    game.start_game()

    # Prefop
    game.bet_raise(to=10)
    game.fold()
    game.call()

    # Flop
    game.bet_raise(to=20)
    game.call()

    # Turn
    game.check()
    game.bet_raise(to=50)
    game.fold()

    results = result.get_result(deal, game.game_view())

    s = Stats()
    s.update_stats(game.game_view(), results, player_id=0)
    assert s == Stats(
        num_hands=1,
        reward=-1,
        num_wins=0,
        num_losses=1,
        num_flops=0,
        num_turns=0,
        num_rivers=0,
        num_showdowns=0,
        num_decisions=1,
        num_check=0,
        num_call=0,
        total_amount_called=0,
        num_bet=0,
        total_amount_bet=0,
        num_fold=1,
    )

    s = Stats()
    s.update_stats(game.game_view(), results, player_id=1)
    assert s == Stats(
        num_hands=1,
        reward=-30,
        num_wins=0,
        num_losses=1,
        num_flops=1,
        num_turns=1,
        num_rivers=0,
        num_showdowns=0,
        num_decisions=4,
        num_check=1,
        num_call=1,
        total_amount_called=8,
        num_bet=1,
        total_amount_bet=20,
        num_fold=1,
    )

    s = Stats()
    s.update_stats(game.game_view(), results, player_id=2)
    assert s == Stats(
        num_hands=1,
        reward=31,
        num_wins=1,
        num_losses=0,
        num_flops=1,
        num_turns=1,
        num_rivers=0,
        num_showdowns=0,
        num_decisions=3,
        num_check=0,
        num_call=1,
        total_amount_called=20,
        num_bet=2,
        total_amount_bet=60,
        num_fold=0,
    )


def test_showdown() -> None:
    # Player 3 wins with a flopped set of jacks.
    deal = FullDeal(
        hole_cards=[mkhand("AcAd"), mkhand("AsKh"), mkhand("JcJh")],
        board=Board(flop=mkflop("KsJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = GameRunner(starting_stacks=[200, 250, 300])
    game.start_game()

    # Prefop
    game.bet_raise(to=10)
    game.fold()
    game.call()

    # Flop
    game.bet_raise(to=20)
    game.call()

    # Turn
    game.check()
    game.bet_raise(to=50)
    game.call()

    # River
    game.check()
    game.check()

    results = result.get_result(deal, game.game_view())

    s = Stats()
    s.update_stats(game.game_view(), results, player_id=0)
    assert s == Stats(
        num_hands=1,
        reward=-1,
        num_wins=0,
        num_losses=1,
        num_flops=0,
        num_turns=0,
        num_rivers=0,
        num_showdowns=0,
        num_decisions=1,
        num_check=0,
        num_call=0,
        total_amount_called=0,
        num_bet=0,
        total_amount_bet=0,
        num_fold=1,
    )

    s = Stats()
    s.update_stats(game.game_view(), results, player_id=1)
    assert s == Stats(
        num_hands=1,
        reward=81,
        num_wins=1,
        num_losses=0,
        num_flops=1,
        num_turns=1,
        num_rivers=1,
        num_showdowns=1,
        num_decisions=5,
        num_check=2,
        num_call=2,
        total_amount_called=58,
        num_bet=1,
        total_amount_bet=20,
        num_fold=0,
    )

    s = Stats()
    s.update_stats(game.game_view(), results, player_id=2)
    assert s == Stats(
        num_hands=1,
        reward=-80,
        num_wins=0,
        num_losses=1,
        num_flops=1,
        num_turns=1,
        num_rivers=1,
        num_showdowns=1,
        num_decisions=4,
        num_check=1,
        num_call=1,
        total_amount_called=20,
        num_bet=2,
        total_amount_bet=60,
        num_fold=0,
    )
