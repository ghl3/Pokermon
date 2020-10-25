use lazy_static::lazy_static;
use rs_poker::core::{Card, Hand, Rankable, Suit, Value};

#[derive(Debug, Clone)]
pub struct NutResult {
    pub better_hands: Vec<Hand>,
    pub tied_hands: Vec<Hand>,
    pub worse_hands: Vec<Hand>,
}

lazy_static! {
    static ref ALL_CARDS: Vec<Card> = {
        let mut cards: Vec<Card> = vec![];
        for value in Value::values().iter() {
            for suit in Suit::suits().iter() {
                cards.push(Card {
                    value: *value,
                    suit: *suit,
                })
            }
        }
        cards
    };
}

lazy_static! {
    static ref ALL_HANDS: Vec<Hand> = {
        let mut hands: Vec<Hand> = vec![];
        for i in 0..ALL_CARDS.len() {
            for j in i + 1..ALL_CARDS.len() {
                hands.push(Hand::new_with_cards(vec![ALL_CARDS[i], ALL_CARDS[j]]))
            }
        }
        hands
    };
}

pub fn make_nut_result(hand: Hand, board: Vec<Card>) -> NutResult {
    let full_hand = Hand::new_with_cards(hand.iter().chain(board.iter()).collect());
    let rank = full_hand.rank();
    let mut nut_result = NutResult {
        better_hands: vec![],
        tied_hands: vec![],
        worse_hands: vec![],
    };

    for other_hand in ALL_HANDS {
        let full_other_hand = Hand::new_with_cards(other_hand.iter().chain(board.iter()).collect());
        let other_rank = full_other_hand.rank();

        if rank > other_rank {
            nut_result.worse_hands.push(other_hand);
        } else if rank == other_rank {
            nut_result.tied_hands.push(other_hand);
        } else {
            nut_result.better_hands.push(other_hand);
        }
    }

    nut_result
}
