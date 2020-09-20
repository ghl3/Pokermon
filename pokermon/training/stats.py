import dataclasses

from pokermon.poker.game import GameView, Move
from pokermon.poker.result import Result


@dataclasses.dataclass
class Stats:

    # Per hand stats
    num_hands: int = 0
    reward: int = 0

    num_wins: int = 0
    num_losses: int = 0

    # Per action stats
    num_voluntary_actions: int = 0
    num_check: int = 0
    num_call: int = 0
    total_amount_called: int = 0
    num_bet: int = 0
    total_amount_bet: int = 0

    def summarize(self):
        return {
            "num_hands": self.num_hands,
            "win_rate": self.num_wins / self.num_hands,
            "reward_per_hand": self.reward / self.num_hands,
            "check_rate": self.num_check / self.num_voluntary_actions,
            "call_rate": self.num_call / self.num_voluntary_actions,
            "avg_call_amount": self.total_amount_called / self.num_call,
            "bet_rate": self.num_bet / self.num_voluntary_actions,
            "avg_bet_amount": self.total_amount_bet / self.num_bet,
        }

    def update_stats(self, game: GameView, result: Result, player_id: int):

        self.num_hands += 1

        self.reward += result.profits[player_id]

        payer_won = result.won_hand[player_id]

        if payer_won:
            self.num_wins += 1
        else:
            self.num_losses += 1

        for action in game.all_actions():
            if action.move in {Move.SMALL_BLIND, Move.BIG_BLIND}:
                continue
            self.num_voluntary_actions += 1

            if action.move == Move.CHECK_CALL and action.amount_added == 0:
                self.num_check += 1
            elif action.move == Move.CHECK_CALL and action.amount_added > 0:
                self.num_call += 1
                self.total_amount_called += action.amount_added
            elif action.move == Move.BET_RAISE:
                self.num_bet += 1
                self.total_amount_bet += action.amount_added
