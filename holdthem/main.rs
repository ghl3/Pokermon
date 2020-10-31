mod cardset;
mod features;
mod globals;
mod hand;
mod nut_result;
mod simulate;
mod stack_array;

use crate::simulate::simulate;

use crate::hand::{Board, HoleCards};
use clap::Clap;
use rs_poker::core::{Card, Suit, Value};

pub fn card_from_char(card_str: &str) -> Result<Card, String> {
    let value = Value::from_char(card_str.chars().next().unwrap()).unwrap();
    let suit = Suit::from_char(card_str.chars().nth(1).unwrap()).unwrap();
    Ok(Card { value, suit })
}

#[derive(Clap, Debug)]
#[clap(name = "basic")]
struct Opts {
    #[clap(long, default_value = "AdAh")]
    hand: String,

    #[clap(long, default_value = "8s7s")]
    range: String,

    #[clap(long)]
    board: Option<String>,

    #[clap(long, default_value = "100000000")]
    num_to_simulate: i64,
}

fn main() {
    let opts: Opts = Opts::parse();

    let hand = HoleCards::new_from_string(&*opts.hand).unwrap();
    let oppo_range: Vec<HoleCards> = opts
        .range
        .split(',')
        .map(|s| HoleCards::new_from_string(s).unwrap())
        .collect();

    let board: Option<Board> = match opts.board {
        Some(s) => Some(Board::new_from_string(&*s).unwrap()),
        None => None,
    };

    let win_counts = simulate(&hand, &oppo_range, &board, opts.num_to_simulate).unwrap();

    println!("Wins = {:?}", win_counts);
}
