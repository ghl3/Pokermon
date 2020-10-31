mod cardset;
mod features;
mod globals;
mod hand;
mod nut_result;
mod simulate;
mod stack_array;

use crate::simulate::simulate;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyModule;
use pyo3::{wrap_pyfunction, PyObjectProtocol};

use crate::hand::{Board, Hand, HoleCards};

use rs_poker::core::{Rank, Rankable};

#[derive(Debug)]
struct HoldThemError {
    message: String,
}

impl std::convert::From<&str> for HoldThemError {
    fn from(err: &str) -> HoldThemError {
        HoldThemError {
            message: err.parse().unwrap(),
        }
    }
}

impl std::convert::From<String> for HoldThemError {
    fn from(err: String) -> HoldThemError {
        HoldThemError { message: err }
    }
}

impl std::convert::From<HoldThemError> for PyErr {
    fn from(err: HoldThemError) -> PyErr {
        PyValueError::new_err(err.message)
    }
}

#[pyfunction]
fn evaluate_hand(hole_cards: String, board: Vec<String>) -> Result<(i32, i32), HoldThemError> {
    let hole_cards = HoleCards::new_from_string(&hole_cards)?;
    let board = Board::new_from_string_vec(&board)?;
    let hand =
        Hand::from_hole_cards_and_board(&hole_cards, &board.ok_or("Board must not be empty")?);

    Ok(match hand.rank() {
        Rank::HighCard(x) => (1, x as i32),
        Rank::OnePair(x) => (2, x as i32),
        Rank::TwoPair(x) => (3, x as i32),
        Rank::ThreeOfAKind(x) => (4, x as i32),
        Rank::Straight(x) => (5, x as i32),
        Rank::Flush(x) => (6, x as i32),
        Rank::FullHouse(x) => (7, x as i32),
        Rank::FourOfAKind(x) => (8, x as i32),
        Rank::StraightFlush(x) => (9, x as i32),
    })
}

#[pyclass]
#[derive(Debug)]
struct SimulationResult {
    #[pyo3(get)]
    pub num_wins: i64,
    #[pyo3(get)]
    pub num_losses: i64,
    #[pyo3(get)]
    pub num_ties: i64,
}

#[pyproto]
impl PyObjectProtocol for SimulationResult {
    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }
}

impl std::convert::From<&simulate::SimulationResult> for SimulationResult {
    fn from(res: &simulate::SimulationResult) -> SimulationResult {
        SimulationResult {
            num_wins: res.num_wins,
            num_losses: res.num_losses,
            num_ties: res.num_ties,
        }
    }
}

#[pyfunction]
fn simulate_hand(
    hand: String,
    range: Vec<String>,
    board: Vec<String>,
    num_to_simulate: i64,
) -> Result<SimulationResult, HoldThemError> {
    print!("Simulating Hand");
    let range: Vec<HoleCards> = range
        .iter()
        .map(|s| HoleCards::new_from_string(s))
        .collect::<Result<Vec<HoleCards>, String>>()?;
    let board = Board::new_from_string_vec(&board[..])?;

    let result = simulate(
        &HoleCards::new_from_string(&*hand)?,
        &range,
        &board,
        num_to_simulate,
    )?;
    Ok(SimulationResult::from(&result))
}

#[pyclass]
#[derive(Debug)]
struct HandFeatures {
    #[pyo3(get)]
    pub frac_better_hands: f32,
    #[pyo3(get)]
    pub frac_tied_hands: f32,
    #[pyo3(get)]
    pub frac_worse_hands: f32,

    #[pyo3(get)]
    pub win_odds: f32,
    #[pyo3(get)]
    pub tie_odds: f32,
    #[pyo3(get)]
    pub lose_odds: f32,

    #[pyo3(get)]
    pub win_odds_vs_better: f32,
    #[pyo3(get)]
    pub tie_odds_vs_better: f32,
    #[pyo3(get)]
    pub lose_odds_vs_better: f32,

    #[pyo3(get)]
    pub win_odds_vs_tied: f32,
    #[pyo3(get)]
    pub tie_odds_vs_tied: f32,
    #[pyo3(get)]
    pub lose_odds_vs_tied: f32,

    #[pyo3(get)]
    pub win_odds_vs_worse: f32,
    #[pyo3(get)]
    pub tie_odds_vs_worse: f32,
    #[pyo3(get)]
    pub lose_odds_vs_worse: f32,
}

#[pyproto]
impl PyObjectProtocol for HandFeatures {
    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }
}

impl std::convert::From<&features::Features> for HandFeatures {
    fn from(res: &features::Features) -> HandFeatures {
        HandFeatures {
            frac_better_hands: res.frac_better_hands,
            frac_tied_hands: res.frac_tied_hands,
            frac_worse_hands: res.frac_worse_hands,
            win_odds: res.win_odds,
            tie_odds: res.tie_odds,
            lose_odds: res.lose_odds,

            win_odds_vs_better: res.win_odds_vs_better,
            tie_odds_vs_better: res.tie_odds_vs_better,
            lose_odds_vs_better: res.lose_odds_vs_better,

            win_odds_vs_tied: res.win_odds_vs_tied,
            tie_odds_vs_tied: res.tie_odds_vs_tied,
            lose_odds_vs_tied: res.lose_odds_vs_tied,

            win_odds_vs_worse: res.win_odds_vs_worse,
            tie_odds_vs_worse: res.tie_odds_vs_worse,
            lose_odds_vs_worse: res.lose_odds_vs_worse,
        }
    }
}

#[pyfunction]
fn make_hand_features(
    hand: String,
    board: Vec<String>,
    num_to_simulate: i64,
) -> Result<HandFeatures, HoldThemError> {
    let hand = HoleCards::new_from_string(&*hand)?;
    let board = Board::new_from_string_vec(&board[..])?;
    let result = features::make_hand_features(&hand, &board, num_to_simulate)?;

    Ok(HandFeatures::from(&result))
}

/// A Python module implemented in Rust.
#[pymodule]
fn pyholdthem(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(evaluate_hand, m)?)?;
    m.add_function(wrap_pyfunction!(simulate_hand, m)?)?;
    m.add_function(wrap_pyfunction!(make_hand_features, m)?)?;
    Ok(())
}
