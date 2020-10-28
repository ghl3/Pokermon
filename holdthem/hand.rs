use rs_poker::core::{Card, Rankable, Suit, Value};
use std::collections::HashSet;
use std::ops::Index;
use std::ops::{RangeFrom, RangeFull, RangeTo};
use std::slice::Iter;

#[derive(Debug)]
struct HoleCards {
    pub cards: [Card; 2],
}

enum Board {
    Flop([Card; 3]),
    Turn([Card; 4]),
    River([Card; 5]),
}

fn card_vec_from_string(hand_string: &str) -> Result<Vec<Card>, String> {
    // Get the chars iterator.
    let mut chars = hand_string.chars();
    // Where we will put the cards
    //
    // We make the assumption that the hands will have 2 plus five cards.
    let mut cards: HashSet<Card> = HashSet::with_capacity(7);

    // Keep looping until we explicitly break
    loop {
        // Now try and get a char.
        let vco = chars.next();
        // If there was no char then we are done.
        if vco == None {
            break;
        } else {
            // If we got a value char then we should get a
            // suit.
            let sco = chars.next();
            // Now try and parse the two chars that we have.
            let v = vco
                .and_then(Value::from_char)
                .ok_or_else(|| format!("Couldn't parse value {}", vco.unwrap_or('?')))?;
            let s = sco
                .and_then(Suit::from_char)
                .ok_or_else(|| format!("Couldn't parse suit {}", sco.unwrap_or('?')))?;

            let c = Card { value: v, suit: s };
            if !cards.insert(c) {
                // If this card is already in the set then error out.
                return Err(format!("This card has already been added {}", c));
            }
        }
    }

    if chars.next() != None {
        return Err(String::from("Extra un-used chars found."));
    }

    Ok(cards.into_iter().collect::<Vec<Card>>())
}

impl Board {
    fn cards(&self) -> &[Card] {
        match self {
            Board::Flop(x) => x,
            Board::Turn(x) => x,
            Board::River(x) => x,
        }
    }

    pub fn new_from_string(hand_string: &str) -> Result<Board, String> {
        match card_vec_from_string(hand_string)?[..] {
            [a, b, c] => Ok(Board::Flop([a, b, c])),
            [a, b, c, d] => Ok(Board::Turn([a, b, c, d])),
            [a, b, c, d, e] => Ok(Board::River([a, b, c, d, e])),
            _ => Err("Cannot parse hand".parse().unwrap()),
        }
    }
}

enum Hand {
    Five([Card; 5]),
    Six([Card; 6]),
    Seven([Card; 7]),
}

/// Implementation for `Hand`
impl Rankable for Hand {
    #[must_use]
    fn cards(&self) -> &[Card] {
        match self {
            Hand::Five(x) => x,
            Hand::Six(x) => x,
            Hand::Seven(x) => x,
        }
    }
}

impl Hand {
    pub fn from_hole_cards_and_board(hole_cards: HoleCards, board: Board) -> Hand {
        match board {
            Board::Flop([a, b, c]) => {
                Hand::Five([hole_cards.cards[0], hole_cards.cards[1], a, b, c])
            }
            Board::Turn([a, b, c, d]) => {
                Hand::Six([hole_cards.cards[0], hole_cards.cards[1], a, b, c, d])
            }
            Board::River([a, b, c, d, e]) => {
                Hand::Seven([hole_cards.cards[0], hole_cards.cards[1], a, b, c, d, e])
            }
        }
    }
}

/// Allow indexing into the hand.
impl Index<usize> for Hand {
    type Output = Card;
    #[must_use]
    fn index(&self, index: usize) -> &Card {
        &self.cards()[index]
    }
}

/// Allow the index to get refernce to every card.
impl Index<RangeFull> for Hand {
    type Output = [Card];
    #[must_use]
    fn index(&self, range: RangeFull) -> &[Card] {
        &self.cards()[range]
    }
}

impl Index<RangeTo<usize>> for Hand {
    type Output = [Card];
    #[must_use]
    fn index(&self, index: RangeTo<usize>) -> &[Card] {
        &self.cards()[index]
    }
}
impl Index<RangeFrom<usize>> for Hand {
    type Output = [Card];
    #[must_use]
    fn index(&self, index: RangeFrom<usize>) -> &[Card] {
        &self.cards()[index]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;
    use std::hash::Hash;

    fn eq_ignoring_order<T>(a: &[T], b: &[T]) -> bool
    where
        T: Eq + Hash,
    {
        fn value_count<T>(items: &[T]) -> HashMap<&T, usize>
        where
            T: Eq + Hash,
        {
            let mut cnt = HashMap::new();
            for i in items {
                *cnt.entry(i).or_insert(0) += 1
            }
            cnt
        }
        value_count(a) == value_count(b)
    }

    #[test]
    fn test_card_vec_from_string() {
        assert!(!eq_ignoring_order(
            &card_vec_from_string("AcAh3s4s5s").unwrap()[..],
            &[
                Card {
                    value: Value::Ace,
                    suit: Suit::Club
                },
                Card {
                    value: Value::Ace,
                    suit: Suit::Heart
                },
                Card {
                    value: Value::Two,
                    suit: Suit::Spade
                },
                Card {
                    value: Value::Three,
                    suit: Suit::Spade
                },
                Card {
                    value: Value::Four,
                    suit: Suit::Spade
                },
            ]
        ));

        assert!(eq_ignoring_order(
            &card_vec_from_string("AcAh3s4s5s").unwrap()[..],
            &[
                Card {
                    value: Value::Ace,
                    suit: Suit::Club
                },
                Card {
                    value: Value::Ace,
                    suit: Suit::Heart
                },
                Card {
                    value: Value::Three,
                    suit: Suit::Spade
                },
                Card {
                    value: Value::Four,
                    suit: Suit::Spade
                },
                Card {
                    value: Value::Five,
                    suit: Suit::Spade
                },
            ]
        ));
    }
}
