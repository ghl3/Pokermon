mod globals;
mod simulate;

use crate::simulate::simulate;

use clap::Clap;
use rs_poker::core::{Card, Hand, Suit, Value};

pub fn card_from_char(card_str: &str) -> Result<Card, String> {
    let value = Value::from_char(card_str.chars().next().unwrap()).unwrap();
    let suit = Suit::from_char(card_str.chars().nth(1).unwrap()).unwrap();
    Ok(Card { value, suit })
}

#[derive(Clap, Debug)]
#[clap(name = "basic")]
struct Opts {
    #[clap(long)]
    hand: String,

    #[clap(long)]
    range: String,

    #[clap(long)]
    board: Option<String>,

    #[clap(long, default_value = "1000000")]
    num_to_simulate: i64,
}

fn main() {
    let opts: Opts = Opts::parse();

    let hand = Hand::new_from_str(&*opts.hand).unwrap();
    let oppo_range: Vec<Hand> = opts
        .range
        .split(',')
        .map(|s| Hand::new_from_str(s).unwrap())
        .collect();

    let board: Vec<Card> = match opts.board {
        Some(s) => {
            let board_chars: Vec<char> = s.chars().collect();
            board_chars
                .chunks(2)
                .map(|chunk| chunk.iter().collect::<String>())
                .map(|s| card_from_char(&*s).unwrap())
                .collect::<Vec<Card>>()
        }

        None => vec![],
    };

    let win_counts = simulate(&hand, &oppo_range, &board, opts.num_to_simulate).unwrap();

    println!("Wins = {:?}", win_counts);
}
