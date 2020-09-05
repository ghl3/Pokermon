from pokermon.poker.game import Action, Move, Street
from pokermon.poker.game_runner import GameRunner


def test_call():
    game = GameRunner(starting_stacks=[100, 100, 100])

    game.start_game()

    assert game.game_view().events() == [
        Street.PREFLOP,
        Action(player_index=0, move=Move.SMALL_BLIND, amount_added=1, total_bet=1),
        Action(player_index=1, move=Move.BIG_BLIND, amount_added=2, total_bet=2),
    ]

    assert game.street() == Street.PREFLOP
    assert game.current_player() == 2

    # Preflop Action
    assert game.bet_raise(to=25) == GameRunner.Result(
        street=Street.PREFLOP, current_player=0, total_bet=25, amount_to_call=24
    )
    assert game.call() == GameRunner.Result(
        street=Street.PREFLOP, current_player=1, total_bet=25, amount_to_call=23
    )
    assert game.fold() == GameRunner.Result(
        street=Street.FLOP, current_player=0, total_bet=0, amount_to_call=0
    )

    # Flop Action
    assert game.bet_raise(to=50) == GameRunner.Result(
        street=Street.FLOP, current_player=2, total_bet=50, amount_to_call=50
    )
    assert game.call() == GameRunner.Result(
        street=Street.TURN, current_player=0, total_bet=0, amount_to_call=0
    )

    # Turn Action
    assert game.check() == GameRunner.Result(
        street=Street.TURN, current_player=2, total_bet=0, amount_to_call=0
    )
    assert game.check() == GameRunner.Result(
        street=Street.RIVER, current_player=0, total_bet=0, amount_to_call=0
    )

    # River
    assert game.check() == GameRunner.Result(
        street=Street.RIVER, current_player=2, total_bet=0, amount_to_call=0
    )
    assert game.bet_raise(raise_amount=10) == GameRunner.Result(
        street=Street.RIVER, current_player=0, total_bet=10, amount_to_call=10
    )
    assert game.call() == GameRunner.Result(street=Street.OVER)


#    call = game.game_view().call()
#    assert call == Action(
#        player_index=0, move=Move.CHECK_CALL, amount_added=9, total_bet=10
#    )
#    game.add_action(call)

#    call = game.view().call()
#    assert call == Action(
#        player_index=1, move=Move.CHECK_CALL, amount_added=8, total_bet=10
#    )


# def test_call_all_in():
#    game = Game(starting_stacks=[10, 20, 100])

#    game.add_action(Action(0, Move.SMALL_BLIND, total_bet=1, amount_added=1))
#    game.add_action(Action(1, Move.BIG_BLIND, total_bet=2, amount_added=2))
#    game.add_action(Action(2, Move.BET_RAISE, total_bet=100, amount_added=100))

#    call = game.view().call()
#    assert game.view().call() == Action(
#        player_index=0, move=Move.CHECK_CALL, amount_added=9, total_bet=100
#    )
#    game.add_action(call)

#    call = game.view().call()
#    assert call == Action(
#        player_index=1, move=Move.CHECK_CALL, amount_added=18, total_bet=100
#    )