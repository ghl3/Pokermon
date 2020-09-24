import dataclasses

from pokermon.poker.game import GameView, Move, Street
from pokermon.poker.result import Result


@dataclasses.dataclass
class Stats:

    # Per hand stats
    num_hands: int = 0
    reward: int = 0

    num_wins: int = 0
    num_losses: int = 0

    # Hand Depth
    num_flops: int = 0
    num_turns: int = 0
    num_rivers: int = 0
    num_showdowns: int = 0

    # Per action stats
    num_decisions: int = 0
    num_check: int = 0
    num_call: int = 0
    total_amount_called: int = 0
    num_bet: int = 0
    total_amount_bet: int = 0
    num_fold: int = 0

    def summarize(self):
        return {
            "num_hands": self.num_hands,
            "num_decisions_per_hand": self.num_decisions / self.num_hands,
            "flop_rate": self.num_flops / self.num_hands,
            "turn_rate": self.num_turns / self.num_hands,
            "river_rate": self.num_rivers / self.num_hands,
            "showdown_rate": self.num_showdowns / self.num_hands,
            "win_rate": self.num_wins / self.num_hands,
            "reward_per_hand": self.reward / self.num_hands,
            "check_rate": self.num_check / self.num_decisions,
            "call_rate": self.num_call / self.num_decisions,
            "avg_call_amount": self.total_amount_called / self.num_call,
            "bet_rate": self.num_bet / self.num_decisions,
            "avg_bet_amount": self.total_amount_bet / self.num_bet,
            "fold_rate": self.num_fold / self.num_decisions,
        }

    def print_summary(self):
        for k, v in self.summarize().items():
            print(f"{k}\t{v:.4f}")

    def update_stats(self, game: GameView, result: Result, player_id: int):

        self.num_hands += 1

        self.reward += result.profits[player_id]

        player_won = result.won_hand[player_id]

        if player_won:
            self.num_wins += 1
        else:
            self.num_losses += 1

        for i, event in enumerate(game.events()):

            view = game.view(i)

            if view.is_folded()[player_id]:
                break

            if event == Street.FLOP:
                self.num_flops += 1
            elif event == Street.TURN:
                self.num_turns += 1
            elif event == Street.RIVER:
                self.num_rivers += 1

        if result.went_to_showdown[player_id]:
            self.num_showdowns += 1

        for action in game.all_actions():

            if action.player_index != player_id:
                continue

            if action.move in {Move.SMALL_BLIND, Move.BIG_BLIND}:
                continue

            self.num_decisions += 1

            if action.move == Move.CHECK_CALL and action.amount_added == 0:
                self.num_check += 1

            elif action.move == Move.CHECK_CALL and action.amount_added > 0:
                self.num_call += 1
                self.total_amount_called += action.amount_added

            elif action.move == Move.BET_RAISE:
                self.num_bet += 1
                self.total_amount_bet += action.amount_added

            elif action.move == Move.FOLD:
                self.num_fold += 1
