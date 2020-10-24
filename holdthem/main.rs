//extern crate rs_poker;
use rs_poker::core::Hand;
use rs_poker::holdem::MonteCarloGame;


// This is a comment, and is ignored by the compiler
// You can test this code by clicking the "Run" button over there ->
// or if you prefer to use your keyboard, you can use the "Ctrl + Enter" shortcut

// This code is editable, feel free to hack it!
// You can always return to the original code by clicking the "Reset" button ->

// This is the main function
fn main() {
    let hands = ["Adkh", "8c8s"]
        .iter()
        .map(|s| Hand::new_from_str(s).expect("Should be able to create a hand."))
        .collect();
    let mut g = MonteCarloGame::new_with_hands(hands).expect("Should be able to create a game.");
    let mut wins: [u64; 2] = [0, 0];
    for _ in 0..10_000 {
        let r = g.simulate().expect("There should be one best rank.");
        g.reset();
        wins[r.0] += 1
    }
    println!("Wins = {:?}", wins);
}