mod simulate;

//extern crate rs_poker;
use crate::simulate::{simulate, Game};
use rs_poker::core::{Card, Deck, Flattenable, Hand, Suit, Value};
use rs_poker::holdem::MonteCarloGame;

// This is a comment, and is ignored by the compiler
// You can test this code by clicking the "Run" button over there ->
// or if you prefer to use your keyboard, you can use the "Ctrl + Enter" shortcut

// This code is editable, feel free to hack it!
// You can always return to the original code by clicking the "Reset" button ->

// This is the main function

pub fn card_from_char(card_str: &str) -> Result<Card, String> {
    let value = Value::from_char(card_str.chars().nth(0).unwrap()).unwrap();
    let suit = Suit::from_char(card_str.chars().nth(1).unwrap()).unwrap();
    Ok(Card { value, suit })
}
//
// pub fn new_with_hands_and_board(
//     hands: Vec<Hand>,
//     board: Vec<Card>,
// ) -> Result<MonteCarloGame, String> {
//     let mut d = Deck::default();
//     for h in &hands {
//         if h.len() != 2 {
//             return Err(String::from("Hand passed in doesn't have 2 cards."));
//         }
//         for c in h.iter() {
//             if !d.remove(*c) {
//                 return Err(format!("Card {} was already removed from the deck.", c));
//             }
//         }
//     }
//     for c in &board {
//         if !d.remove(*c) {
//             return Err(format!("Card {} was already removed from the deck.", c));
//         }
//     }
//     Ok(MonteCarloGame {
//         deck: d.flatten(),
//         board: board,
//         hands: hands,
//         current_offset: 52,
//     })
// }

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

    // let mut g = new_with_hands_and_board(hands, board).expect("Should be able to create a game.");
    let win_counts = simulate(
        Game {
            hole_cards: hands,
            board: board,
        },
        1_000_000,
    )
    .unwrap();

    // [0, 0];
    // for _ in 0..10_000 {
    //     match g.simulate() {
    //         Ok((winner_index, rank)) => {
    //             wins[winner_index] += 1;
    //             print!("{:?}\n", rank)
    //         }
    //         _ => {}
    //     }
    //     g.reset();
    // }

    println!("Wins = {:?}", win_counts);
}
