
import deuces
from pokermon.ai.policy import Policy



def simulate(player_policies, num_games):


    for game_idx in range(num_games):
        deck = deuces.Deck()