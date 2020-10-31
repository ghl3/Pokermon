use crate::globals::ALL_HANDS;
use crate::hand::{Board, Hand, HoleCards};
use rs_poker::core::Rankable;

#[derive(Debug, Clone)]
pub struct NutResult {
    pub better_hands: Vec<HoleCards>,
    pub tied_hands: Vec<HoleCards>,
    pub worse_hands: Vec<HoleCards>,
}

impl NutResult {
    pub fn num_hands(&self) -> usize {
        self.better_hands.len() + self.tied_hands.len() + self.worse_hands.len()
    }
    pub fn frac_better(&self) -> f32 {
        self.better_hands.len() as f32 / self.num_hands() as f32
    }
    pub fn frac_tied(&self) -> f32 {
        self.tied_hands.len() as f32 / self.num_hands() as f32
    }
    pub fn frac_worse(&self) -> f32 {
        self.worse_hands.len() as f32 / self.num_hands() as f32
    }
}

pub fn make_nut_result(hole_cards: &HoleCards, board: &Board) -> NutResult {
    let hand = Hand::from_hole_cards_and_board(hole_cards, board);

    let rank = hand.rank();
    let mut nut_result = NutResult {
        better_hands: vec![],
        tied_hands: vec![],
        worse_hands: vec![],
    };

    for other_hand in ALL_HANDS.iter() {
        // TODO: We should be able to eliminate this unwrap since we aready know the board
        // is not empty at this point.
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
