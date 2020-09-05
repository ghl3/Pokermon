# /usr/bin/env python

import argparse
import logging
import sys
from typing import List

from pokermon.ai import policies
from pokermon.ai.policy import Policy
from pokermon.poker import dealer
from pokermon.poker.cards import FullDeal
from pokermon.simulate import simulate


def main():
    parser = argparse.ArgumentParser(description="Play a hand of poker.")

    parser.add_argument("--player", action="append", help="Type of player", type=str)

    parser.add_argument(
        "--starting_stack",
        help="Starting stack size (in small blinds)",
        type=int,
        default=100,
    )

    parser.add_argument(
        "-log",
        "--log",
        help="Provide logging level. Example --log debug'",
        type=str,
        default="DEBUG",
    )

    args = parser.parse_args()

    # Configure the logger
    format = "[%(asctime)s] %(pathname)s:%(lineno)d %(levelname)s - %(message)s"
    log_level = getattr(logging, args.log)
    logging.basicConfig(level=log_level, format=format)

    players: List[Policy] = [policies.POLICIES[player] for player in args.player]

    stack_sizes = [args.starting_stack for _ in args.player]

    deal: FullDeal = dealer.deal_cards(len(players))

    game, result = simulate.simulate(players, stack_sizes, deal)

    print(game)
    print(result)

    sys.exit(0)


if __name__ == "__main__":
    main()
