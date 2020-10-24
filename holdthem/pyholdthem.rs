use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyModule, PyString, PyTuple};
use pyo3::wrap_pyfunction;
use rs_poker::core::{Card, Hand, Rank, Rankable, Suit, Value};
use std::error::Error;

pub fn card_from_str(card_str: &str) -> Result<Card, String> {
    if card_str.len() != 2 {
        return Err(String::from("Error"));
    }

    let value = Value::from_char(card_str.chars().nth(0).unwrap()).unwrap();
    let suit = Suit::from_char(card_str.chars().nth(1).unwrap()).unwrap();
    Ok(Card { value, suit })
}

#[pyclass]
struct HandRank {
    #[pyo3(get)]
    rank: i32,
    #[pyo3(get)]
    kicker: i32,
}

#[derive(Debug)]
struct CustomError {
    message: String,
}

impl std::convert::From<String> for CustomError {
    fn from(err: String) -> CustomError {
        CustomError { message: err }
    }
}

impl std::convert::From<CustomError> for PyErr {
    fn from(err: CustomError) -> PyErr {
        PyValueError::new_err(err.message)
    }
}

#[pyfunction]
fn evaluate_hand(hole_cards: String, board: Vec<String>) -> Result<HandRank, CustomError> {
    let mut hand = Hand::new_from_str(&hole_cards)?;
    for card in &board {
        hand.push(card_from_str(card)?)
    }

    let gil = Python::acquire_gil();
    let py = gil.python();

    Ok(match hand.rank() {
        Rank::HighCard(x) => HandRank {
            rank: 1,
            kicker: x as i32,
        },
        Rank::OnePair(x) => HandRank {
            rank: 2,
            kicker: x as i32,
        },
        Rank::TwoPair(x) => HandRank {
            rank: 3,
            kicker: x as i32,
        },
        Rank::ThreeOfAKind(x) => HandRank {
            rank: 4,
            kicker: x as i32,
        },
        Rank::Straight(x) => HandRank {
            rank: 5,
            kicker: x as i32,
        },
        Rank::Flush(x) => HandRank {
            rank: 6,
            kicker: x as i32,
        },
        Rank::FullHouse(x) => HandRank {
            rank: 7,
            kicker: x as i32,
        },
        Rank::FourOfAKind(x) => HandRank {
            rank: 8,
            kicker: x as i32,
        },
        Rank::StraightFlush(x) => HandRank {
            rank: 9,
            kicker: x as i32,
        },
    })
}

/// A Python module implemented in Rust.
#[pymodule]
fn pyholdthem(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(evaluate_hand, m)?)?;
    Ok(())
}
