mod simulate;

use crate::simulate::{simulate, Game};
use rs_poker::core::{Card, Hand, Suit, Value};

pub fn card_from_char(card_str: &str) -> Result<Card, String> {
    let value = Value::from_char(card_str.chars().nth(0).unwrap()).unwrap();
    let suit = Suit::from_char(card_str.chars().nth(1).unwrap()).unwrap();
    Ok(Card { value, suit })
}

fn main() {
    let hands = vec![
        Hand::new_from_str("Adkh").unwrap(),
        Hand::new_from_str("8c8s").unwrap(),
    ];
    let board = vec![
        card_from_char("As").unwrap(),
        card_from_char("Kd").unwrap(),
        card_from_char("8h").unwrap(),
    ];

    let win_counts = simulate(
        Game {
            hole_cards: hands,
            board,
        },
        1_000_000,
    )
    .unwrap();

    println!("Wins = {:?}", win_counts);
}
