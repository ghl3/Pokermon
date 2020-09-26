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
            win_prob_vs_random=None,
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
            win_prob_vs_random=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=2,
            current_hand_strength=0.5225140712945591,
            current_hand_rank=3563,
            frac_hands_better=0.03574468085106383,
            frac_hands_tied=0.009361702127659575,
            frac_hands_worse=0.9548936170212766,
            win_prob_vs_random=0.82,
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
            win_prob_vs_random=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=2,
            current_hand_strength=0.5230501206110962,
            current_hand_rank=3559,
            frac_hands_better=0.06388642413487133,
            frac_hands_tied=0.009760425909494233,
            frac_hands_worse=0.9263531499556344,
            win_prob_vs_random=0.88,
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
            win_prob_vs_random=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=2,
            current_hand_strength=0.5230501206110962,
            current_hand_rank=3559,
            frac_hands_better=0.1574074074074074,
            frac_hands_tied=0.009259259259259259,
            frac_hands_worse=0.8333333333333334,
            win_prob_vs_random=0.81,
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
            win_prob_vs_random=None,
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
            win_prob_vs_random=None,
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
            win_prob_vs_random=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=4,
            current_hand_strength=0.752881265076387,
            current_hand_rank=1844,
            frac_hands_better=0.0,
            frac_hands_tied=0.001702127659574468,
            frac_hands_worse=0.9982978723404256,
            win_prob_vs_random=0.97,
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
            win_prob_vs_random=None,
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
            win_prob_vs_random=1.0,
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
            win_prob_vs_random=None,
        ),
        PlayerState(
            is_current_player=True,
            current_player_offset=0,
            current_hand_type=8,
            current_hand_strength=0.9937014205306888,
            current_hand_rank=47,
            frac_hands_better=0.000925925925925926,
            frac_hands_tied=0.0,
            frac_hands_worse=0.9990740740740741,
            win_prob_vs_random=1.0,
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
            win_prob_vs_random=None,
        ),
    ]
