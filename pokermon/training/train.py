import argparse
import logging
import sys
from random import shuffle
from typing import Dict, Optional

from tqdm import tqdm

from pokermon.ai.policy import Policy
from pokermon.model import heads_up
from pokermon.model.heads_up import HeadsUpModel
from pokermon.poker import dealer
from pokermon.poker.cards import FullDeal
from pokermon.simulate import simulate
from pokermon.simulate.simulate import choose_starting_stacks
from pokermon.training.stats import Stats

logger = logging.getLogger(__name__)


def train_heads_up(
    policies: Dict[str, Policy],
    num_hands_to_play: int,
    num_hands_between_checkpoints: Optional[int] = None,
):

    # Initialize the stats per hand
    results: Dict[str, Stats] = {name: Stats() for name in policies}

    players = list(policies.keys())

    logger.debug("Beginning training with %s players", len(players))

    for player_name, model in policies.items():
        if num_hands_between_checkpoints and isinstance(model, HeadsUpModel):
            ckpt_path = f"/Users/George/Projects/pokermon/models/{model.name}"
            latest_checkpoint = model.checkpoint_manager(ckpt_path).latest_checkpoint
            print(f"Restoring from {ckpt_path} {latest_checkpoint}")
            model.checkpoint().restore(latest_checkpoint)

    for i in tqdm(range(num_hands_to_play)):

        hand_index = i + 1

        starting_stacks = choose_starting_stacks()

        shuffle(players)

        deal: FullDeal = dealer.deal_cards(len(players))

        game, result = simulate.simulate(
            [policies[player] for player in players], starting_stacks, deal
        )

        for player_idx, player_name in enumerate(players):

            model = policies[player_name]

            results[player_name].update_stats(game.view(), result, player_idx)

            if isinstance(model, HeadsUpModel):
                model.train_step(
                    player_idx,
                    game.view(),
                    deal.hole_cards[player_idx],
                    deal.board,
                    result,
                )

            if (
                num_hands_between_checkpoints
                and hand_index % num_hands_between_checkpoints == 0
            ):
                print()
                print(f"Stats for {player_name}")
                results[player_name].print_summary()
                print()
                # Reset the stats
                results[player_name] = Stats()

                if isinstance(model, HeadsUpModel):
                    ckpt_path = f"./models/{model.name}"
                    print(f"Saving to {ckpt_path}")
                    model.checkpoint_manager(ckpt_path).save()


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

    models = {"foo": heads_up.HeadsUpModel("Foo"), "bar": heads_up.HeadsUpModel("Bar")}

    train_heads_up(models, args.num_hands, args.checkpoint_every)

    sys.exit(0)


if __name__ == "__main__":
    main()
