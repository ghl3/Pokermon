use crate::hand::HoleCards;
use lazy_static::lazy_static;
use rs_poker::core::{Card, Suit, Value};

lazy_static! {
    pub static ref ALL_CARDS: Vec<Card> = {
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
    pub static ref ALL_HANDS: Vec<HoleCards> = {
        let mut hands: Vec<HoleCards> = vec![];
        for i in 0..ALL_CARDS.len() {
            for j in i + 1..ALL_CARDS.len() {
                hands.push(HoleCards::new_from_cards(ALL_CARDS[i], ALL_CARDS[j]);
            }
        }
        hands
    };
}
