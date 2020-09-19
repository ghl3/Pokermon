import argparse
import logging
import sys
from random import randint, shuffle
from typing import List

import numpy as np
from tqdm import tqdm

import pokermon.poker.rules as rules
from pokermon.model import heads_up
from pokermon.model.heads_up import HeadsUpModel
from pokermon.poker import dealer
from pokermon.poker.cards import FullDeal
from pokermon.simulate import simulate
from pokermon.simulate.simulate import choose_starting_stacks

logger = logging.getLogger(__name__)


def train_heads_up(
    players: List[HeadsUpModel],
    num_hands_to_play: int,
    num_hands_between_checkpoins: int,
):
    logger.debug("Beginning training with %s players", len(players))

    losses = []

    for i in tqdm(range(num_hands_to_play)):
        starting_stacks = choose_starting_stacks()

        shuffle(players)

        deal: FullDeal = dealer.deal_cards(len(players))

        game, results = simulate.simulate(players, starting_stacks, deal)

        results = rules.get_result(deal, game.view())

        for player_idx, model in enumerate(players):
            if isinstance(model, HeadsUpModel):
                example, loss = model.train_step(
                    player_idx,
                    game.view(),
                    deal.hole_cards[player_idx],
                    deal.board,
                    results,
                )

                ckpt_path = f"./models/{model.name}"
                if i == 0:
                    print(f"Restoring from {ckpt_path}")
                    model.checkpoint().restore(
                        model.checkpoint_manager(ckpt_path).latest_checkpoint
                    )
                elif i % num_hands_between_checkpoins == 0:
                    print(f"Saving to {ckpt_path}")
                    model.checkpoint_manager(ckpt_path).save()


#   print(np.cumsum(losses))


def main():
    parser = argparse.ArgumentParser(description="Play a hand of poker.")

    parser.add_argument(
        "--num_hands",
        help="Number of hands to play",
        type=int,
        default=500,
    )

    parser.add_argument(
        "--checkpoint_every",
        help="Number between checkpoints",
        type=int,
        default=100,
    )

    parser.add_argument(
        "-log",
        "--log",
        help="Provide logging level. Example --log debug'",
        type=str,
        default="INFO",
    )

    args = parser.parse_args()

    # Configure the logger
    format = "[%(asctime)s] %(pathname)s:%(lineno)d %(levelname)s - %(message)s"
    log_level = getattr(logging, args.log)
    logging.basicConfig(level=log_level, format=format)

    models = [heads_up.HeadsUpModel("Foo"), heads_up.HeadsUpModel("Bar")]

    train_heads_up(models, args.num_hands, args.checkpoint_every)

    sys.exit(0)


if __name__ == "__main__":
    main()
