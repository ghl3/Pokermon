import random

from pokermon.poker import cards, hands
from pokermon.poker.board import Board
from pokermon.poker.deal import FullDeal


def deal_cards(num_players: int) -> FullDeal:

    # First, select the preflop hands
    preflop_hands = random.sample(hands.ALL_HANDS, num_players)

    # Then, select the board
    selected_hands = set()
    for hand in preflop_hands:
        selected_hands.update(hand.cards)
    remaining_cards = [c for c in cards.ALL_CARDS if c not in selected_hands]
    board_cards = random.sample(remaining_cards, 5)

    return FullDeal(
        hole_cards=preflop_hands,
        board=Board(
            flop=(board_cards[0], board_cards[1], board_cards[2]),
            turn=board_cards[3],
            river=board_cards[4],
        ),
    )


# def deal_cards(num_players: int) -> FullDeal:
#     deck = deuces.deck.Deck()
#     board = deck.draw(5)
#
#     hole_cards = []
#
#     for _ in range(num_players):
#         hole_cards.append(deck.draw(2))
#
#     flop = (
#         wrapper.from_deuces_card(board[0]),
#         wrapper.from_deuces_card(board[1]),
#         wrapper.from_deuces_card(board[2]),
#     )
#     turn = wrapper.from_deuces_card(board[3])
#     river = wrapper.from_deuces_card(board[4])
#
#     return FullDeal(
#         hole_cards=[
#             (wrapper.from_deuces_card(x), wrapper.from_deuces_card(y))
#             for x, y in hole_cards
#         ],
#         board=Board(flop=flop, turn=turn, river=river),
#     )
