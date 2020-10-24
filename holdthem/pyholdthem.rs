use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyModule;
use pyo3::wrap_pyfunction;
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

    let value = Value::from_char(card_str.chars().nth(0).unwrap()).unwrap();
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

/// A Python module implemented in Rust.
#[pymodule]
fn pyholdthem(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(evaluate_hand, m)?)?;
    Ok(())
}
