mod cardset;
mod globals;
mod hand_comparison;
mod hand_features;
mod simulate;

use crate::simulate::simulate;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyModule;
use pyo3::{wrap_pyfunction, PyObjectProtocol};

use rs_poker::core::{Card, Hand, Rank, Rankable, Suit, Value};

#[derive(Debug)]
struct HoldThemError {
    message: String,
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

pub fn card_from_str(card_str: &str) -> Result<Card, String> {
    if card_str.len() != 2 {
        return Err(String::from("Error"));
    }

    let value = Value::from_char(card_str.chars().next().unwrap()).unwrap();
    let suit = Suit::from_char(card_str.chars().nth(1).unwrap()).unwrap();
    Ok(Card { value, suit })
}

#[pyfunction]
fn evaluate_hand(hole_cards: String, board: Vec<String>) -> Result<(i32, i32), HoldThemError> {
    let mut hand = Hand::new_from_str(&hole_cards)?;
    for card in &board {
        hand.push(card_from_str(card)?)
    }

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
    let range: Vec<Hand> = range
        .iter()
        .map(|s| Hand::new_from_str(s))
        .collect::<Result<Vec<Hand>, String>>()?;
    let board: Vec<Card> = board
        .iter()
        .map(|s| card_from_str(s))
        .collect::<Result<Vec<Card>, String>>()?;

    let result = simulate(
        &Hand::new_from_str(&*hand)?,
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
    pub num_better_hands: i64,
    #[pyo3(get)]
    pub num_tied_hands: i64,
    #[pyo3(get)]
    pub num_worse_hands: i64,

    #[pyo3(get)]
    pub odds_vs_better: f32,
    #[pyo3(get)]
    pub odds_vs_tied: f32,
    #[pyo3(get)]
    pub odds_vs_worse: f32,
}

#[pyproto]
impl PyObjectProtocol for HandFeatures {
    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }
}

impl std::convert::From<&hand_features::HandFeatures> for HandFeatures {
    fn from(res: &hand_features::HandFeatures) -> HandFeatures {
        HandFeatures {
            num_better_hands: res.num_better_hands,
            num_tied_hands: res.num_tied_hands,
            num_worse_hands: res.num_worse_hands,
            odds_vs_better: res.odds_vs_better.unwrap_or(-1.0),
            odds_vs_tied: res.odds_vs_tied.unwrap_or(-1.0),
            odds_vs_worse: res.odds_vs_worse.unwrap_or(-1.0),
        }
    }
}

#[pyfunction]
fn make_hand_features(
    hand: String,
    board: Vec<String>,
    num_to_simulate: i64,
) -> Result<HandFeatures, HoldThemError> {
    let hand = Hand::new_from_str(&*hand)?;

    let board: Vec<Card> = board
        .iter()
        .map(|s| card_from_str(s))
        .collect::<Result<Vec<Card>, String>>()?;

    let result = hand_features::make_hand_features(hand, board, num_to_simulate)?;

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
