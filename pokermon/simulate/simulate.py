import logging
from random import randint
from typing import List, Tuple

import pokermon.poker.rules as rules
from pokermon.ai.policy import Policy
from pokermon.poker.cards import FullDeal
from pokermon.poker.game import Game, Street
from pokermon.poker.game_runner import GameRunner
from pokermon.poker.result import Result, get_result

logger = logging.getLogger(__name__)


def choose_starting_stacks():
    return [randint(10, 300), randint(10, 300)]


def simulate(
    players: List[Policy], starting_stacks: List[int], deal: FullDeal
) -> Tuple[Game, Result]:
    """
    Players are ordered by Small Blind, Big Blind, ..., Button
    :param players:
    :param starting_stacks:
    :param deal:
    :return:
    """

    logger.debug("Simulating game with %s players", len(players))

    game_runner = GameRunner(starting_stacks=starting_stacks)

    logger.debug("Hole Cards: %s", deal.hole_cards)

    game_runner.start_game()

    while True:

        board = deal.board.at_street(game_runner.street())

        player_index = game_runner.current_player()
        player = players[player_index]
        hand = deal.hole_cards[player_index]
        action = player.select_action(
            player_index, game_runner.game_view(), hand, board
        )

        if action is None:
            raise Exception("Invalid Action")

        action_result = game_runner.advance(action)

        if action_result.street == Street.HAND_OVER:
            logger.debug("Hand Over")
            break

    try:
        result = get_result(deal, game_runner.game_view())
    except Exception as e:
        for event in game_runner.game.events:
            print(event)
        raise e

    logger.debug("Result: %s", result)

    return game_runner.game, result
