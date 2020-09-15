import logging
from typing import List, Tuple

import pokermon.poker.rules as rules
from pokermon.ai.policy import Policy
from pokermon.poker.cards import FullDeal
from pokermon.poker.game import Game, Street
from pokermon.poker.game_runner import GameRunner
from pokermon.poker.rules import GameResults

logger = logging.getLogger(__name__)


def simulate(
    players: List[Policy], starting_stacks: List[int], deal: FullDeal
) -> Tuple[Game, GameResults]:
    """
    Players are ordered by Small Blind, Big Blind, ..., Button
    :param players:
    :param starting_stacks:
    :param deal:
    :return:
    """

    logger.debug("Simulating game with %s players", len(players))

    game_runner = GameRunner(starting_stacks=starting_stacks)

    logger.info("Hole Cards: %s", deal.hole_cards)

    game_runner.start_game()

    while True:

        player_index = game_runner.current_player()
        player = players[player_index]
        hand = deal.hole_cards[player_index]
        action = player.select_action(
            player_index, game_runner.game_view(), hand, deal.board
        )

        if action is None:
            raise Exception("Invalid Action")

        action_result = game_runner.advance(action)

        if action_result.street == Street.OVER:
            logger.debug("Hand Over")
            break

    result = rules.get_result(deal, game_runner.game_view())

    logger.info("Result: %s", result)

    return game_runner.game, result
