from dataclasses import dataclass
from typing import Dict, List, Set

from pokermon.poker.cards import FullDeal
from pokermon.poker.evaluation import EvaluationResult, evaluate_hand
from pokermon.poker.game import GameView
from pokermon.poker.rules import get_pot_payouts, get_ranked_hand_groups


@dataclass(frozen=True)
class Result:
    # Whether each player won the hand.  Usually there is only one, but there may
    # be multiple in the event of ties or side-pots.  A player who was given any part
    # of the pot is considered a winning player.
    won_hand: List[bool]

    # A map of the player indices to their final hand (is this for all players
    # or just players who went to showdown?)
    hand_results: List[EvaluationResult]

    # Whether each player went to showdown (or, if they were the last player
    # after everyone else folded, which we consider to be a 1-player showdown).
    # In other words, showdown == !folded
    went_to_showdown: List[bool]

    # The amount of money won by each player at the end of the hand (not profit)
    earned_at_showdown: List[int]

    # The actual profits, in small blinds, won or list by each player during this game
    profits: List[int]


def get_result(cards: FullDeal, game: GameView) -> Result:
    hand_results: List[EvaluationResult] = []

    went_to_showdown: List[bool] = []

    for player_index in range(game.num_players()):
        hole_cards = cards.hole_cards[player_index]
        board = cards.board

        eval_result: EvaluationResult = evaluate_hand(hole_cards, board)

        hand_results.append(eval_result)

        went_to_showdown.append(not game.is_folded()[player_index])

    showdown_hands: Dict[int, EvaluationResult] = {
        idx: hand for idx, hand in enumerate(hand_results) if went_to_showdown[idx]
    }

    winning_players: Set[int] = get_winning_players(showdown_hands)

    won_hand: List[bool] = [
        player_index in winning_players for player_index in range(game.num_players())
    ]

    pot_per_winning_player: Dict[int, int] = get_pot_payouts(
        get_ranked_hand_groups(showdown_hands), game.amount_added_total()
    )

    earned_at_showdown: List[int] = [
        pot_per_winning_player.get(i, 0) for i in range(game.num_players())
    ]
    profit_per_player: List[int] = [
        earned_at_showdown[i] - amount_added
        for i, amount_added in enumerate(game.amount_added_total())
    ]

    return Result(
        won_hand=won_hand,
        hand_results=hand_results,
        went_to_showdown=went_to_showdown,
        earned_at_showdown=earned_at_showdown,
        profits=profit_per_player,
    )


def get_winning_players(hands: Dict[int, EvaluationResult]) -> Set[int]:
    """
    Returns the order of winning players (among all players who went to showdown) in order (the
    first player index returned as the best hand, the second the next best, etc)
    :param hands:
    :return:
    """
    # Lower ranks are better
    winning_rank = min([res.rank for _, res in hands.items()])
    return {player_idx for player_idx, h in hands.items() if h.rank == winning_rank}
