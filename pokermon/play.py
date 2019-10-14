import argparse
import logging
import sys
from sys import stderr
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
  
  # Configure the logger
  format = '[%(asctime)s] %(pathname)s:%(lineno)d %(levelname)s - %(message)s'
  log_level = getattr(logging, args.log[0])
  logging.basicConfig(level=log_level, format=format)

#  ch = logging.StreamHandler()
#  ch.setLevel(logging.ERROR)
  
#  formatter = logging.Formatter(
#    '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
#    '%m-%d %H:%M:%S')
#  handler = logging.StreamHandler(stderr)
#  handler.setFormatter(formatter)
  
  players: List[Policy] = [policies.POLICIES[player] for player in args.player]
  
  stack_sizes = [args.starting_stack for _ in args.player]
  
  deal: FullDeal = dealer.deal_cards(len(players))
  
  game, result = simulate.simulate(players, stack_sizes, deal)
  
  print(game)
  print(result)
  
  sys.exit(0)


if __name__ == '__main__':
  main()
