from pokermon.poker.board import Board, mkflop
from pokermon.poker.cards import mkcard
from pokermon.poker.deal import FullDeal
from pokermon.poker.evaluation import EvaluationResult
from pokermon.poker.game_runner import GameRunner
from pokermon.poker.hands import HandType, mkhand
from pokermon.poker.result import Result, get_result


def test_game_result():
    deal = FullDeal(
        hole_cards=[mkhand("AcAh"), mkhand("KdKs"), mkhand("JhJd")],
        board=Board(flop=mkflop("6dQc2s"), turn=mkcard("6s"), river=mkcard("3c")),
    )

    game = GameRunner(starting_stacks=[100, 200, 300])
    game.start_game()

    # Preflop
    game.bet_raise(to=10)
    game.call()
    game.call()

    # Flop
    game.bet_raise(to=20)
    game.call()
    game.call()

    # Turn
    game.bet_raise(to=30)
    game.call()
    game.call()

    # River
    game.check()
    game.check()
    game.check()

    result = get_result(deal, game.game_view())

    assert result == Result(
        won_hand=[True, False, False],
        hand_results=[
            EvaluationResult(
                hand_type=HandType.TWO_PAIR,
                kicker=33686528,
            ),
            EvaluationResult(hand_type=HandType.TWO_PAIR, kicker=16909312),
            EvaluationResult(hand_type=HandType.TWO_PAIR, kicker=4326400),
        ],
        went_to_showdown=[True, True, True],
        remained_in_hand=[True, True, True],
        earned_from_pot=[180, 0, 0],
        profits=[120, -60, -60],
    )


def test_game_with_tie():
    deal = FullDeal(
        hole_cards=[mkhand("Ac3h"), mkhand("Ad4s"), mkhand("5s5d")],
        board=Board(flop=mkflop("AsAhKc"), turn=mkcard("Kd"), river=mkcard("7h")),
    )

    game = GameRunner(starting_stacks=[100, 200, 300])
    game.start_game()

    # Preflop
    game.bet_raise(to=30)
    game.call()
    game.call()

    # Flop
    game.bet_raise(to=50)
    game.call()
    game.call()

    # Turn
    game.bet_raise(to=20)
    game.call()
    game.call()

    # River
    game.bet_raise(to=100)
    game.call()

    result = get_result(deal, game.game_view())

    assert result == Result(
        won_hand=[True, True, False],
        hand_results=[
            EvaluationResult(hand_type=HandType.FULL_HOUSE, kicker=33556480),
            EvaluationResult(hand_type=HandType.FULL_HOUSE, kicker=33556480),
            EvaluationResult(hand_type=HandType.TWO_PAIR, kicker=50331680),
        ],
        remained_in_hand=[True, True, True],
        went_to_showdown=[True, True, True],
        earned_from_pot=[150, 350, 0],
        profits=[50, 150, -200],
    )
