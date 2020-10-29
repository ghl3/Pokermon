use crate::globals::ALL_HANDS;
use crate::hand::{Board, Hand, HoleCards};
use rs_poker::core::{Card, Rankable};

#[derive(Debug, Clone)]
pub struct NutResult {
    pub better_hands: Vec<HoleCards>,
    pub tied_hands: Vec<HoleCards>,
    pub worse_hands: Vec<HoleCards>,
}

pub fn make_nut_result(hand: &HoleCards, board: &Board) -> NutResult {
    let full_hand: Hand = Hand::from_hole_cards_and_board(hand, board);
    let rank = full_hand.rank();
    let mut nut_result = NutResult {
        better_hands: vec![],
        tied_hands: vec![],
        worse_hands: vec![],
    };

    for other_hand in ALL_HANDS.iter() {
        let full_other_hand = Hand::from_hole_cards_and_board(other_hand, board);
        let other_rank = full_other_hand.rank();

        if other_rank < rank {
            nut_result.worse_hands.push(other_hand.clone());
        } else if rank != other_rank {
            nut_result.better_hands.push(other_hand.clone());
        } else {
            nut_result.tied_hands.push(other_hand.clone());
        }
    }

    nut_result
}
