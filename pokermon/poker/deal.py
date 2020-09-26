from dataclasses import dataclass
from typing import List

from pokermon.poker.board import Board
from pokermon.poker.hands import HoleCards


@dataclass(frozen=True)
class FullDeal:
    hole_cards: List[HoleCards]
    board: Board
