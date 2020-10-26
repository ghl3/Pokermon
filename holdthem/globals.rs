use lazy_static::lazy_static;
use rs_poker::core::{Card, Hand, Suit, Value};

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
    pub static ref ALL_HANDS: Vec<Hand> = {
        let mut hands: Vec<Hand> = vec![];
        for i in 0..ALL_CARDS.len() {
            for j in i + 1..ALL_CARDS.len() {
                hands.push(Hand::new_with_cards(vec![ALL_CARDS[i], ALL_CARDS[j]]))
            }
        }
        hands
    };
}
