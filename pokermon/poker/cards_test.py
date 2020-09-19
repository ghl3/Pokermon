from pokermon.poker.cards import Board, mkflop, mkcard, Card, Rank, Suit
from pokermon.poker.game import Street


def test_board_at_street() -> None:

    board = Board(flop=mkflop("AdKs3h"), turn=mkcard("5h"), river=mkcard("7s"))

    assert board.at_street(Street.TURN) == Board(
        flop=(
            Card(rank=Rank.ACE, suit=Suit.DIAMONDS),
            Card(rank=Rank.KING, suit=Suit.SPADES),
            Card(rank=Rank.THREE, suit=Suit.HEARTS),
        ),
        turn=Card(rank=Rank.FIVE, suit=Suit.HEARTS),
        river=None,
    )

    assert board.at_street(Street.FLOP) == Board(
        flop=(
            Card(rank=Rank.ACE, suit=Suit.DIAMONDS),
            Card(rank=Rank.KING, suit=Suit.SPADES),
            Card(rank=Rank.THREE, suit=Suit.HEARTS),
        ),
        turn=None,
        river=None,
    )
