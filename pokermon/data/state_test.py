from pokermon.data.state import PrivateState, make_private_states
from pokermon.poker.cards import Board, FullDeal, mkcard, mkflop, mkhand
from pokermon.poker.game_runner import GameRunner


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
    private_states = make_private_states(
        game.game_view(), deal.hole_cards[player_index], deal.board
    )

    assert private_states == [
        PrivateState(current_hand_type=None, current_hand_strength=None, current_hand_rank=None,
                     num_hands_better=None, num_hands_tied=None, num_hands_worse=None,
                     win_prob_vs_random=None),
        PrivateState(current_hand_type=None, current_hand_strength=None, current_hand_rank=None,
                     num_hands_better=None, num_hands_tied=None, num_hands_worse=None,
                     win_prob_vs_random=None),
        PrivateState(current_hand_type=2, current_hand_strength=0.5225140712945591,
                     current_hand_rank=3563, num_hands_better=42, num_hands_tied=11,
                     num_hands_worse=1122, win_prob_vs_random=0.871),
        PrivateState(current_hand_type=2, current_hand_strength=0.5225140712945591,
                     current_hand_rank=3563, num_hands_better=42, num_hands_tied=11,
                     num_hands_worse=1122, win_prob_vs_random=0.871),
        PrivateState(current_hand_type=2, current_hand_strength=0.5230501206110962,
                     current_hand_rank=3559, num_hands_better=72, num_hands_tied=11,
                     num_hands_worse=1044, win_prob_vs_random=0.872),
        PrivateState(current_hand_type=2, current_hand_strength=0.5230501206110962,
                     current_hand_rank=3559, num_hands_better=72, num_hands_tied=11,
                     num_hands_worse=1044, win_prob_vs_random=0.872),
        PrivateState(current_hand_type=2, current_hand_strength=0.5230501206110962,
                     current_hand_rank=3559, num_hands_better=170, num_hands_tied=10,
                     num_hands_worse=900, win_prob_vs_random=0.842),
        PrivateState(current_hand_type=2, current_hand_strength=0.5230501206110962,
                     current_hand_rank=3559, num_hands_better=170, num_hands_tied=10,
                     num_hands_worse=900, win_prob_vs_random=0.842)]


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
    private_states = make_private_states(
        game.game_view(), deal.hole_cards[player_index], deal.board
    )

    assert private_states == [
        PrivateState(current_hand_type=None, current_hand_strength=None, current_hand_rank=None,
                     num_hands_better=None, num_hands_tied=None, num_hands_worse=None,
                     win_prob_vs_random=None),
        PrivateState(current_hand_type=None, current_hand_strength=None, current_hand_rank=None,
                     num_hands_better=None, num_hands_tied=None, num_hands_worse=None,
                     win_prob_vs_random=None),
        PrivateState(current_hand_type=4, current_hand_strength=0.752881265076387,
                     current_hand_rank=1844, num_hands_better=0, num_hands_tied=2,
                     num_hands_worse=1173, win_prob_vs_random=0.928),
        PrivateState(current_hand_type=4, current_hand_strength=0.752881265076387,
                     current_hand_rank=1844, num_hands_better=0, num_hands_tied=2,
                     num_hands_worse=1173, win_prob_vs_random=0.928),
        PrivateState(current_hand_type=8, current_hand_strength=0.993299383543286,
                     current_hand_rank=50, num_hands_better=0, num_hands_tied=0,
                     num_hands_worse=1127, win_prob_vs_random=0.999),
        PrivateState(current_hand_type=8, current_hand_strength=0.993299383543286,
                     current_hand_rank=50, num_hands_better=0, num_hands_tied=0,
                     num_hands_worse=1127, win_prob_vs_random=0.999),
        PrivateState(current_hand_type=8, current_hand_strength=0.9937014205306888,
                     current_hand_rank=47, num_hands_better=1, num_hands_tied=0,
                     num_hands_worse=1079, win_prob_vs_random=1.0),
        PrivateState(current_hand_type=8, current_hand_strength=0.9937014205306888,
                     current_hand_rank=47, num_hands_better=1, num_hands_tied=0,
                     num_hands_worse=1079, win_prob_vs_random=1.0)]
