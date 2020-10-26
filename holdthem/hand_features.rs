use crate::hand_comparison::make_nut_result;
use crate::simulate::simulate;
use rs_poker::core::{Card, Hand};

/// The input of a simulation
#[derive(Debug)]
pub struct HandFeatures {
    pub num_better_hands: i64,
    pub num_tied_hands: i64,
    pub num_worse_hands: i64,

    pub odds_vs_better: Option<f32>,
    pub odds_vs_tied: Option<f32>,
    pub odds_vs_worse: Option<f32>,
}

pub fn make_hand_features(
    hand: Hand,
    board: Vec<Card>,
    num_to_simulate: i64,
) -> Result<HandFeatures, String> {
    let nut_result = make_nut_result(&hand, &board);

    let odds_vs_better = simulate(&hand, &nut_result.better_hands, &board, num_to_simulate)?;

    let odds_vs_tied = simulate(&hand, &nut_result.tied_hands, &board, num_to_simulate)?;

    let odds_vs_worse = simulate(&hand, &nut_result.worse_hands, &board, num_to_simulate)?;

    Ok(HandFeatures {
        num_better_hands: nut_result.better_hands.len() as i64,
        num_tied_hands: nut_result.tied_hands.len() as i64,
        num_worse_hands: nut_result.worse_hands.len() as i64,
        odds_vs_better: odds_vs_better.win_frac(),
        odds_vs_tied: odds_vs_tied.win_frac(),
        odds_vs_worse: odds_vs_worse.win_frac(),
    })
}
