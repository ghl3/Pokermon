import logging
from random import randint
from typing import List, Tuple

import pokermon.poker.rules as rules
from pokermon.model.heads_up import HeadsUpModel
from pokermon.poker import dealer
from pokermon.poker.cards import FullDeal
from pokermon.simulate import simulate

logger = logging.getLogger(__name__)


def choose_starting_stacks():
    return [randint(10, 300), randint(10, 300)]


def train_heads_up(players: List[HeadsUpModel], num_hands_to_play: int):
    logger.debug("Beginning training with %s players", len(players))

    for hand_index in range(num_hands_to_play):
        starting_stacks = choose_starting_stacks()

        deal: FullDeal = dealer.deal_cards(len(players))

        game, results = simulate.simulate(players, starting_stacks, deal)

        results = rules.get_result(deal, game.view())

        for player_idx, model in enumerate(players):
            model.train_step(
                player_idx,
                game.view(),
                deal.hole_cards[player_idx],
                deal.board,
                results,
            )
