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
            current_hand_strength=None,
            current_hand_rank=None,
            frac_hands_better=None,
            frac_hands_tied=None,
            frac_hands_worse=None,
            win_prob_vs_any=None,
            win_prob_vs_better=None,
            win_prob_vs_tied=None,
            win_prob_vs_worse=None,
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            current_hand_strength=None,
            current_hand_rank=None,
            frac_hands_better=None,
            frac_hands_tied=None,
            frac_hands_worse=None,
            win_prob_vs_any=None,
            win_prob_vs_better=None,
            win_prob_vs_tied=None,
            win_prob_vs_worse=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=2,
            current_hand_strength=0.5225140712945591,
            current_hand_rank=3563,
            frac_hands_better=0.028677150786308975,
            frac_hands_tied=0.005550416281221091,
            frac_hands_worse=0.96577243293247,
            win_prob_vs_any=0.8481378353376503,
            win_prob_vs_better=0.175,
            win_prob_vs_tied=0.0,
            win_prob_vs_worse=0.873,
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            current_hand_strength=None,
            current_hand_rank=None,
            frac_hands_better=None,
            frac_hands_tied=None,
            frac_hands_worse=None,
            win_prob_vs_any=None,
            win_prob_vs_better=None,
            win_prob_vs_tied=None,
            win_prob_vs_worse=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=2,
            current_hand_strength=0.5230501206110962,
            current_hand_rank=3559,
            frac_hands_better=0.05603864734299517,
            frac_hands_tied=0.005797101449275362,
            frac_hands_worse=0.9381642512077295,
            win_prob_vs_any=0.8705497584541063,
            win_prob_vs_better=0.116,
            win_prob_vs_tied=0.0,
            win_prob_vs_worse=0.921,
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            current_hand_strength=None,
            current_hand_rank=None,
            frac_hands_better=None,
            frac_hands_tied=None,
            frac_hands_worse=None,
            win_prob_vs_any=None,
            win_prob_vs_better=None,
            win_prob_vs_tied=None,
            win_prob_vs_worse=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=2,
            current_hand_strength=0.5230501206110962,
            current_hand_rank=3559,
            frac_hands_better=0.14646464646464646,
            frac_hands_tied=0.006060606060606061,
            frac_hands_worse=0.8474747474747475,
            win_prob_vs_any=0.8474747474747475,
            win_prob_vs_better=0.0,
            win_prob_vs_tied=0.0,
            win_prob_vs_worse=1.0,
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            current_hand_strength=None,
            current_hand_rank=None,
            frac_hands_better=None,
            frac_hands_tied=None,
            frac_hands_worse=None,
            win_prob_vs_any=None,
            win_prob_vs_better=None,
            win_prob_vs_tied=None,
            win_prob_vs_worse=None,
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
            current_hand_strength=None,
            current_hand_rank=None,
            frac_hands_better=None,
            frac_hands_tied=None,
            frac_hands_worse=None,
            win_prob_vs_any=None,
            win_prob_vs_better=None,
            win_prob_vs_tied=None,
            win_prob_vs_worse=None,
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            current_hand_strength=None,
            current_hand_rank=None,
            frac_hands_better=None,
            frac_hands_tied=None,
            frac_hands_worse=None,
            win_prob_vs_any=None,
            win_prob_vs_better=None,
            win_prob_vs_tied=None,
            win_prob_vs_worse=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=4,
            current_hand_strength=0.752881265076387,
            current_hand_rank=1844,
            frac_hands_better=0.0,
            frac_hands_tied=0.0,
            frac_hands_worse=1.0,
            win_prob_vs_any=0.904,
            win_prob_vs_better=-1,
            win_prob_vs_tied=-1,
            win_prob_vs_worse=0.904,
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            current_hand_strength=None,
            current_hand_rank=None,
            frac_hands_better=None,
            frac_hands_tied=None,
            frac_hands_worse=None,
            win_prob_vs_any=None,
            win_prob_vs_better=None,
            win_prob_vs_tied=None,
            win_prob_vs_worse=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=8,
            current_hand_strength=0.993299383543286,
            current_hand_rank=50,
            frac_hands_better=0.0,
            frac_hands_tied=0.0,
            frac_hands_worse=1.0,
            win_prob_vs_any=1.0,
            win_prob_vs_better=-1,
            win_prob_vs_tied=-1,
            win_prob_vs_worse=1.0,
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            current_hand_strength=None,
            current_hand_rank=None,
            frac_hands_better=None,
            frac_hands_tied=None,
            frac_hands_worse=None,
            win_prob_vs_any=None,
            win_prob_vs_better=None,
            win_prob_vs_tied=None,
            win_prob_vs_worse=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=8,
            current_hand_strength=0.9937014205306888,
            current_hand_rank=47,
            frac_hands_better=0.00101010101010101,
            frac_hands_tied=0.0,
            frac_hands_worse=0.998989898989899,
            win_prob_vs_any=0.998989898989899,
            win_prob_vs_better=0.0,
            win_prob_vs_tied=-1,
            win_prob_vs_worse=1.0,
        ),
        PlayerState(
            is_current_player=False,
            current_player_offset=1,
            current_hand_type=None,
            current_hand_strength=None,
            current_hand_rank=None,
            frac_hands_better=None,
            frac_hands_tied=None,
            frac_hands_worse=None,
            win_prob_vs_any=None,
            win_prob_vs_better=None,
            win_prob_vs_tied=None,
            win_prob_vs_worse=None,
        ),
    ]
