use crate::globals::ALL_HANDS;
use rs_poker::core::{Card, Hand, Rankable};

#[derive(Debug, Clone)]
pub struct NutResult {
    pub better_hands: Vec<Hand>,
    pub tied_hands: Vec<Hand>,
    pub worse_hands: Vec<Hand>,
}

pub fn make_nut_result(hand: &Hand, board: &Vec<Card>) -> NutResult {
    let full_hand = Hand::new_with_cards(hand.iter().chain(board.iter()).copied().collect());
    let rank = full_hand.rank();
    let mut nut_result = NutResult {
        better_hands: vec![],
        tied_hands: vec![],
        worse_hands: vec![],
    };

    for other_hand in ALL_HANDS.iter() {
        let full_other_hand =
            Hand::new_with_cards(other_hand.iter().chain(board.iter()).copied().collect());
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
