use crate::globals::PREFLOP_HAND_FEATURES;
use crate::hand::{Board, HoleCards};
use crate::nut_result::{make_nut_result, NutResult};
use crate::simulate::simulate;
use crate::simulate::SimulationResult;

/// The input of a simulation
#[derive(Debug)]
pub struct Features {
    pub frac_better_hands: f32,
    pub frac_tied_hands: f32,
    pub frac_worse_hands: f32,

    pub win_odds: f32,
    pub tie_odds: f32,
    pub lose_odds: f32,

    pub win_odds_vs_better: f32,
    pub tie_odds_vs_better: f32,
    pub lose_odds_vs_better: f32,

    pub win_odds_vs_tied: f32,
    pub tie_odds_vs_tied: f32,
    pub lose_odds_vs_tied: f32,

    pub win_odds_vs_worse: f32,
    pub tie_odds_vs_worse: f32,
    pub lose_odds_vs_worse: f32,
}

impl Features {
    fn new(
        nut_result: &NutResult,
        odds_vs_better: &Option<SimulationResult>,
        odds_vs_tied: &Option<SimulationResult>,
        odds_vs_worse: &Option<SimulationResult>,
    ) -> Features {
        let win_odds_vs_better = odds_vs_better.as_ref().map_or(0.0, |x| x.win_frac());
        let win_odds_vs_tied = odds_vs_tied.as_ref().map_or(0.0, |x| x.win_frac());
        let win_odds_vs_worse = odds_vs_worse.as_ref().map_or(0.0, |x| x.win_frac());

        let tie_odds_vs_better = odds_vs_better.as_ref().map_or(0.0, |x| x.tie_frac());
        let tie_odds_vs_tied = odds_vs_tied.as_ref().map_or(0.0, |x| x.tie_frac());
        let tie_odds_vs_worse = odds_vs_worse.as_ref().map_or(0.0, |x| x.tie_frac());

        let lose_odds_vs_better = odds_vs_better.as_ref().map_or(0.0, |x| x.lose_frac());
        let lose_odds_vs_tied = odds_vs_tied.as_ref().map_or(0.0, |x| x.lose_frac());
        let lose_odds_vs_worse = odds_vs_worse.as_ref().map_or(0.0, |x| x.lose_frac());

        let win_odds = nut_result.frac_better() * win_odds_vs_better
            + nut_result.frac_tied() * win_odds_vs_tied
            + nut_result.frac_worse() * win_odds_vs_worse;

        let tie_odds = nut_result.frac_better() * tie_odds_vs_better
            + nut_result.frac_tied() * tie_odds_vs_tied
            + nut_result.frac_worse() * tie_odds_vs_worse;

        let lose_odds = nut_result.frac_better() * lose_odds_vs_better
            + nut_result.frac_tied() * lose_odds_vs_tied
            + nut_result.frac_worse() * lose_odds_vs_worse;

        Features {
            frac_better_hands: nut_result.frac_better(),
            frac_tied_hands: nut_result.frac_tied(),
            frac_worse_hands: nut_result.frac_worse(),
            win_odds,
            tie_odds,
            lose_odds,

            win_odds_vs_better,
            tie_odds_vs_better,
            lose_odds_vs_better,

            win_odds_vs_tied,
            tie_odds_vs_tied,
            lose_odds_vs_tied,

            win_odds_vs_worse,
            tie_odds_vs_worse,
            lose_odds_vs_worse,
        }
    }
}

pub fn make_hand_features(
    hand: &HoleCards,
    board: &Option<Board>,
    num_to_simulate: i64,
) -> Result<Features, String> {
    match board {
        Some(b) => make_post_flop_hand_features(hand, b, num_to_simulate),
        None => Ok(make_pre_flop_hand_features(hand)),
    }
}

pub fn make_post_flop_hand_features(
    hand: &HoleCards,
    board: &Board,
    num_to_simulate: i64,
) -> Result<Features, String> {
    let nut_result = make_nut_result(hand, board);

    let odds_vs_better = match nut_result.better_hands.len() {
        0 => None,
        _ => Some(simulate(
            &hand,
            &nut_result.better_hands,
            &Some(board.clone()),
            num_to_simulate,
        )?),
    };

    let odds_vs_tied = match nut_result.tied_hands.len() {
        0 => None,
        _ => Some(simulate(
            &hand,
            &nut_result.tied_hands,
            &Some(board.clone()),
            num_to_simulate,
        )?),
    };

    let odds_vs_worse = match nut_result.worse_hands.len() {
        0 => None,
        _ => Some(simulate(
            &hand,
            &nut_result.worse_hands,
            &Some(board.clone()),
            num_to_simulate,
        )?),
    };

    Ok(Features::new(
        &nut_result,
        &odds_vs_better,
        &odds_vs_tied,
        &odds_vs_worse,
    ))
}

pub fn make_pre_flop_hand_features(hand: &HoleCards) -> Features {
    let (_, win_odds, tie_odds, lose_odds) = PREFLOP_HAND_FEATURES[hand.preflop_index()];

    Features {
        frac_better_hands: -1.0,
        frac_tied_hands: -1.0,
        frac_worse_hands: -1.0,
        win_odds,
        tie_odds,
        lose_odds,
        win_odds_vs_better: -1.0,
        tie_odds_vs_better: -1.0,
        lose_odds_vs_better: -1.0,
        win_odds_vs_tied: -1.0,
        tie_odds_vs_tied: -1.0,
        lose_odds_vs_tied: -1.0,
        win_odds_vs_worse: -1.0,
        tie_odds_vs_worse: -1.0,
        lose_odds_vs_worse: -1.0,
    }
}
