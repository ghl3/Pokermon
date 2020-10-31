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

    for villian_hole_cards in ALL_HANDS.iter() {
        if hole_cards == villian_hole_cards {
            continue;
        }

        let villian_hand = Hand::from_hole_cards_and_board(villian_hole_cards, board);
        let villian_rank = villian_hand.rank();

        if villian_rank < rank {
            nut_result.worse_hands.push(villian_hole_cards.clone());
        } else if rank != villian_rank {
            nut_result.better_hands.push(villian_hole_cards.clone());
        } else {
            nut_result.tied_hands.push(villian_hole_cards.clone());
        }
    }

    nut_result
}
