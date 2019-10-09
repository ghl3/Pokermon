import argparse
import logging
from typing import List

from pokermon.ai import policies
from pokermon.ai.policy import Policy
from pokermon.poker import dealer
from pokermon.poker.cards import FullDeal
from pokermon.simulate import simulate


def main():
  parser = argparse.ArgumentParser(description='Play a hand of poker.')
  
  parser.add_argument('--player', action='append', help='Type of player', type=str)
  
  parser.add_argument('--starting_stack', help='Starting stack size (in small blinds)', type=int,
                      default=100)
  
  parser.add_argument("-log", "--log", nargs='+',
                      help="Provide logging level. Example --log debug'")
  
  args = parser.parse_args()
  
  print(args)
  
  # Configure the logger
  log_level = getattr(logging, args.log[0])
  logging.basicConfig(level=log_level)
  
  players: List[Policy] = [policies.POLICIES[player] for player in args.player]
  
  stack_sizes = [args.starting_stack for _ in args.player]
  
  deal: FullDeal = dealer.deal_cards(len(players))
  
  game, result = simulate.simulate(players, stack_sizes, deal)
  
  print(game)
  print(result)


if __name__ == '__main__':
  main()
