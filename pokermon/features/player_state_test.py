from pytest import approx

from pokermon.features.player_state import PlayerState, make_player_states
from pokermon.poker.board import Board, mkflop
from pokermon.poker.cards import mkcard
from pokermon.poker.deal import FullDeal
from pokermon.poker.game_runner import GameRunner
from pokermon.poker.hands import mkhand


def test_state() -> None:
    deal = FullDeal(
        hole_cards=[mkhand("AhKs"), mkhand("Kc10d")],
        board=Board(flop=mkflop("KdJs3d"), turn=mkcard("7s"), river=mkcard("6s")),
    )

    game = GameRunner(starting_stacks=[300, 400])
    game.start_game()

    # Preflop
    game.bet_raise(to=10)
    game.call()

    # Flop
    game.check()
    game.check()

    # Turn
    game.check()
    game.check()

    # River
    game.check()
    game.check()

    player_index = 0
    private_states = make_player_states(
        player_index, game.game_view(), deal.hole_cards[player_index], deal.board
    )

    assert private_states == [
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=None,
            frac_better_hands=None,
            frac_tied_hands=None,
            frac_worse_hands=None,
            win_odds=None,
            tie_odds=None,
            lose_odds=None,
            win_odds_vs_better=None,
            tie_odds_vs_better=None,
            lose_odds_vs_better=None,
            win_odds_vs_tied=None,
            tie_odds_vs_tied=None,
            lose_odds_vs_tied=None,
            win_odds_vs_worse=None,
            tie_odds_vs_worse=None,
            lose_odds_vs_worse=None,
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            frac_better_hands=None,
            frac_tied_hands=None,
            frac_worse_hands=None,
            win_odds=None,
            tie_odds=None,
            lose_odds=None,
            win_odds_vs_better=None,
            tie_odds_vs_better=None,
            lose_odds_vs_better=None,
            win_odds_vs_tied=None,
            tie_odds_vs_tied=None,
            lose_odds_vs_tied=None,
            win_odds_vs_worse=None,
            tie_odds_vs_worse=None,
            lose_odds_vs_worse=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=2,
            frac_better_hands=approx(0.02867715060710907, abs=0.1),
            frac_tied_hands=approx(0.005550416186451912, abs=0.1),
            frac_worse_hands=approx(0.9657724499702454, abs=0.1),
            win_odds=approx(0.8368927240371704, abs=0.1),
            tie_odds=approx(0.010364476591348648, abs=0.1),
            lose_odds=approx(0.15274283289909363, abs=0.1),
            win_odds_vs_better=approx(0.16899999976158142, abs=0.1),
            tie_odds_vs_better=approx(0.0020000000949949026, abs=0.1),
            lose_odds_vs_better=approx(0.8289999961853027, abs=0.1),
            win_odds_vs_tied=0.0,
            tie_odds_vs_tied=approx(0.9869999885559082, abs=0.1),
            lose_odds_vs_tied=approx(0.013000000268220901, abs=0.1),
            win_odds_vs_worse=approx(0.8840000033378601, abs=0.1),
            tie_odds_vs_worse=approx(0.004000000189989805, abs=0.1),
            lose_odds_vs_worse=approx(0.1120000034570694, abs=0.1),
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            frac_better_hands=None,
            frac_tied_hands=None,
            frac_worse_hands=None,
            win_odds=None,
            tie_odds=None,
            lose_odds=None,
            win_odds_vs_better=None,
            tie_odds_vs_better=None,
            lose_odds_vs_better=None,
            win_odds_vs_tied=None,
            tie_odds_vs_tied=None,
            lose_odds_vs_tied=None,
            win_odds_vs_worse=None,
            tie_odds_vs_worse=None,
            lose_odds_vs_worse=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=2,
            frac_better_hands=approx(0.05603864789009094, abs=0.1),
            frac_tied_hands=approx(0.005797101650387049, abs=0.1),
            frac_worse_hands=approx(0.938164234161377, abs=0.1),
            win_odds=approx(0.8556057810783386, abs=0.1),
            tie_odds=approx(0.005797101650387049, abs=0.1),
            lose_odds=approx(0.13859710097312927, abs=0.1),
            win_odds_vs_better=0.0,
            tie_odds_vs_better=0.0,
            lose_odds_vs_better=1.0,
            win_odds_vs_tied=0.0,
            tie_odds_vs_tied=1.0,
            lose_odds_vs_tied=0.0,
            win_odds_vs_worse=approx(0.9120000004768372, abs=0.1),
            tie_odds_vs_worse=0.0,
            lose_odds_vs_worse=approx(0.08799999952316284, abs=0.1),
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            frac_better_hands=None,
            frac_tied_hands=None,
            frac_worse_hands=None,
            win_odds=None,
            tie_odds=None,
            lose_odds=None,
            win_odds_vs_better=None,
            tie_odds_vs_better=None,
            lose_odds_vs_better=None,
            win_odds_vs_tied=None,
            tie_odds_vs_tied=None,
            lose_odds_vs_tied=None,
            win_odds_vs_worse=None,
            tie_odds_vs_worse=None,
            lose_odds_vs_worse=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=2,
            frac_better_hands=approx(0.14646464586257935, abs=0.1),
            frac_tied_hands=approx(0.0060606058686971664, abs=0.1),
            frac_worse_hands=approx(0.8474747538566589, abs=0.1),
            win_odds=approx(0.8474747538566589, abs=0.1),
            tie_odds=approx(0.0060606058686971664, abs=0.1),
            lose_odds=approx(0.14646464586257935, abs=0.1),
            win_odds_vs_better=0.0,
            tie_odds_vs_better=0.0,
            lose_odds_vs_better=1.0,
            win_odds_vs_tied=0.0,
            tie_odds_vs_tied=1.0,
            lose_odds_vs_tied=0.0,
            win_odds_vs_worse=1.0,
            tie_odds_vs_worse=0.0,
            lose_odds_vs_worse=0.0,
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            frac_better_hands=None,
            frac_tied_hands=None,
            frac_worse_hands=None,
            win_odds=None,
            tie_odds=None,
            lose_odds=None,
            win_odds_vs_better=None,
            tie_odds_vs_better=None,
            lose_odds_vs_better=None,
            win_odds_vs_tied=None,
            tie_odds_vs_tied=None,
            lose_odds_vs_tied=None,
            win_odds_vs_worse=None,
            tie_odds_vs_worse=None,
            lose_odds_vs_worse=None,
        ),
    ]


def test_monster() -> None:
    deal = FullDeal(
        hole_cards=[mkhand("JcJd"), mkhand("Kc10d")],
        board=Board(flop=mkflop("JsTs3h"), turn=mkcard("Jh"), river=mkcard("As")),
    )

    game = GameRunner(starting_stacks=[300, 400])
    game.start_game()

    # Preflop
    game.bet_raise(to=10)
    game.call()

    # Flop
    game.check()
    game.check()

    # Turn
    game.check()
    game.check()

    # River
    game.check()
    game.check()

    player_index = 0
    private_states = make_player_states(
        player_index, game.game_view(), deal.hole_cards[player_index], deal.board
    )

    assert private_states == [
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=None,
            frac_better_hands=None,
            frac_tied_hands=None,
            frac_worse_hands=None,
            win_odds=None,
            tie_odds=None,
            lose_odds=None,
            win_odds_vs_better=None,
            tie_odds_vs_better=None,
            lose_odds_vs_better=None,
            win_odds_vs_tied=None,
            tie_odds_vs_tied=None,
            lose_odds_vs_tied=None,
            win_odds_vs_worse=None,
            tie_odds_vs_worse=None,
            lose_odds_vs_worse=None,
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            frac_better_hands=None,
            frac_tied_hands=None,
            frac_worse_hands=None,
            win_odds=None,
            tie_odds=None,
            lose_odds=None,
            win_odds_vs_better=None,
            tie_odds_vs_better=None,
            lose_odds_vs_better=None,
            win_odds_vs_tied=None,
            tie_odds_vs_tied=None,
            lose_odds_vs_tied=None,
            win_odds_vs_worse=None,
            tie_odds_vs_worse=None,
            lose_odds_vs_worse=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=4,
            frac_better_hands=0.0,
            frac_tied_hands=0.0,
            frac_worse_hands=1.0,
            win_odds=approx(0.9300000071525574, abs=0.1),
            tie_odds=0.0,
            lose_odds=approx(0.07000000029802322, abs=0.1),
            win_odds_vs_better=0.0,
            tie_odds_vs_better=0.0,
            lose_odds_vs_better=0.0,
            win_odds_vs_tied=0.0,
            tie_odds_vs_tied=0.0,
            lose_odds_vs_tied=0.0,
            win_odds_vs_worse=approx(0.9300000071525574, abs=0.1),
            tie_odds_vs_worse=0.0,
            lose_odds_vs_worse=approx(0.07000000029802322, abs=0.1),
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            frac_better_hands=None,
            frac_tied_hands=None,
            frac_worse_hands=None,
            win_odds=None,
            tie_odds=None,
            lose_odds=None,
            win_odds_vs_better=None,
            tie_odds_vs_better=None,
            lose_odds_vs_better=None,
            win_odds_vs_tied=None,
            tie_odds_vs_tied=None,
            lose_odds_vs_tied=None,
            win_odds_vs_worse=None,
            tie_odds_vs_worse=None,
            lose_odds_vs_worse=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=8,
            frac_better_hands=0.0,
            frac_tied_hands=0.0,
            frac_worse_hands=1.0,
            win_odds=approx(0.9990000128746033, abs=0.1),
            tie_odds=0.0,
            lose_odds=approx(0.0010000000474974513, abs=0.1),
            win_odds_vs_better=0.0,
            tie_odds_vs_better=0.0,
            lose_odds_vs_better=0.0,
            win_odds_vs_tied=0.0,
            tie_odds_vs_tied=0.0,
            lose_odds_vs_tied=0.0,
            win_odds_vs_worse=approx(0.9990000128746033, abs=0.1),
            tie_odds_vs_worse=0.0,
            lose_odds_vs_worse=approx(0.0010000000474974513, abs=0.1),
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            frac_better_hands=None,
            frac_tied_hands=None,
            frac_worse_hands=None,
            win_odds=None,
            tie_odds=None,
            lose_odds=None,
            win_odds_vs_better=None,
            tie_odds_vs_better=None,
            lose_odds_vs_better=None,
            win_odds_vs_tied=None,
            tie_odds_vs_tied=None,
            lose_odds_vs_tied=None,
            win_odds_vs_worse=None,
            tie_odds_vs_worse=None,
            lose_odds_vs_worse=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=8,
            frac_better_hands=approx(0.001010101055726409, abs=0.1),
            frac_tied_hands=0.0,
            frac_worse_hands=approx(0.9989898800849915, abs=0.1),
            win_odds=approx(0.9989898800849915, abs=0.1),
            tie_odds=0.0,
            lose_odds=approx(0.001010101055726409, abs=0.1),
            win_odds_vs_better=0.0,
            tie_odds_vs_better=0.0,
            lose_odds_vs_better=1.0,
            win_odds_vs_tied=0.0,
            tie_odds_vs_tied=0.0,
            lose_odds_vs_tied=0.0,
            win_odds_vs_worse=1.0,
            tie_odds_vs_worse=0.0,
            lose_odds_vs_worse=0.0,
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            frac_better_hands=None,
            frac_tied_hands=None,
            frac_worse_hands=None,
            win_odds=None,
            tie_odds=None,
            lose_odds=None,
            win_odds_vs_better=None,
            tie_odds_vs_better=None,
            lose_odds_vs_better=None,
            win_odds_vs_tied=None,
            tie_odds_vs_tied=None,
            lose_odds_vs_tied=None,
            win_odds_vs_worse=None,
            tie_odds_vs_worse=None,
            lose_odds_vs_worse=None,
        ),
    ]
