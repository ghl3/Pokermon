import argparse

from pokermon.ai import policies
from pokermon.simulate import simulate


def main():
  parser = argparse.ArgumentParser(description='Play a hand of poker.')
  
  parser.add_argument('--player', nargs='+', help='Type of player', type=str)
  
  parser.add_argument('--starting_stack', help='Starting stack size (in small blinds)', type=int)
  
  args = parser.parse_args()
  
  players = [policies.POLICIES[player] for player in args.player]
  
  stack_sizes = [args.starting_stack for _ in args.player]
  
  # Deal the cards
  deal = None
  
  simulate.simulate(players, stack_sizes, deal)
