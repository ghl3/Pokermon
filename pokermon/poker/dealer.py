import random
from typing import Set

from pokermon.poker import cards, hands
from pokermon.poker.board import Board
from pokermon.poker.cards import Card
from pokermon.poker.deal import FullDeal


def deal_cards(num_players: int) -> FullDeal:

    # First, select the preflop hands
    preflop_hands = random.sample(hands.ALL_HANDS, num_players)

    # Then, select the board
    selected_cards: Set[Card] = set()
    for hand in preflop_hands:
        selected_cards.update(hand.cards)
    remaining_cards = [c for c in cards.ALL_CARDS if c not in selected_cards]
    board_cards = random.sample(remaining_cards, 5)

    return FullDeal(
        hole_cards=preflop_hands,
        board=Board(
            flop=(board_cards[0], board_cards[1], board_cards[2]),
            turn=board_cards[3],
            river=board_cards[4],
        ),
    )
