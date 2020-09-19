from pokermon.ai.random_policy import RandomPolicy
from pokermon.poker import dealer, rules
from pokermon.poker.cards import FullDeal
from pokermon.simulate.simulate import choose_starting_stacks, simulate


def test_simulate_random():
    for _ in range(20):
        players = [RandomPolicy(), RandomPolicy(), RandomPolicy()]
        starting_stacks = choose_starting_stacks()
        deal: FullDeal = dealer.deal_cards(len(players))
        game, results = simulate(players, starting_stacks, deal)
        results = rules.get_result(deal, game.view())
