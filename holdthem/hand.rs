use rs_poker::core::{Card, Rankable, Suit, Value};
use std::collections::HashSet;
use std::ops::Index;
use std::ops::{RangeFrom, RangeFull, RangeTo};

pub fn card_from_str(card_str: &str) -> Result<Card, String> {
    if card_str.len() != 2 {
        return Err(String::from("Error"));
    }

    let value = Value::from_char(card_str.chars().next().unwrap()).unwrap();
    let suit = Suit::from_char(card_str.chars().nth(1).unwrap()).unwrap();
    Ok(Card { value, suit })
}

#[derive(Debug, PartialEq, Clone)]
pub struct HoleCards {
    pub cards: [Card; 2],
}

impl HoleCards {
    pub fn new_from_cards(c1: Card, c2: Card) -> HoleCards {
        HoleCards { cards: [c1, c2] }
    }

    pub fn new_from_string(hand_string: &str) -> Result<HoleCards, String> {
        match card_vec_from_string(hand_string)?[..] {
            [a, b] => Ok(HoleCards { cards: [a, b] }),
            _ => Err("Cannot parse hole cards".parse().unwrap()),
        }
    }

    pub fn slice(&self) -> &[Card] {
        &self.cards[..]
    }
}

#[derive(Debug, PartialEq, Clone)]
pub enum Board {
    Empty,
    Flop([Card; 3]),
    Turn([Card; 4]),
    River([Card; 5]),
}

impl Board {
    pub fn cards(&self) -> &[Card] {
        match self {
            Board::Empty => &[] as &[Card; 0],
            Board::Flop(x) => x,
            Board::Turn(x) => x,
            Board::River(x) => x,
        }
    }

    pub fn len(&self) -> usize {
        match self {
            Board::Empty => 0,
            Board::Flop(x) => 3,
            Board::Turn(x) => 4,
            Board::River(x) => 5,
        }
    }

    pub fn new_from_string(hand_string: &str) -> Result<Board, String> {
        match card_vec_from_string(hand_string)?[..] {
            [a, b, c] => Ok(Board::Flop([a, b, c])),
            [a, b, c, d] => Ok(Board::Turn([a, b, c, d])),
            [a, b, c, d, e] => Ok(Board::River([a, b, c, d, e])),
            _ => Err("Cannot parse board".parse().unwrap()),
        }
    }

    pub fn new_from_string_vec(hand_strings: &[String]) -> Result<Board, String> {
        match hand_strings {
            [a, b, c] => Ok(Board::Flop([
                card_from_str(a)?,
                card_from_str(b)?,
                card_from_str(c)?,
            ])),
            [a, b, c, d] => Ok(Board::Turn([
                card_from_str(a)?,
                card_from_str(b)?,
                card_from_str(c)?,
                card_from_str(d)?,
            ])),
            [a, b, c, d, e] => Ok(Board::River([
                card_from_str(a)?,
                card_from_str(b)?,
                card_from_str(c)?,
                card_from_str(d)?,
                card_from_str(e)?,
            ])),
            [] => Ok(Board::Empty),
            _ => Err("Cannot parse board".parse().unwrap()),
        }
    }
}

#[derive(Debug, PartialEq)]
pub enum Hand {
    Five([Card; 5]),
    Six([Card; 6]),
    Seven([Card; 7]),
}

impl Hand {
    pub fn from_hole_cards_and_board(hole_cards: &HoleCards, board: &Board) -> Option<Hand> {
        match board {
            Board::Flop([a, b, c]) => Some(Hand::Five([
                hole_cards.cards[0],
                hole_cards.cards[1],
                *a,
                *b,
                *c,
            ])),
            Board::Turn([a, b, c, d]) => Some(Hand::Six([
                hole_cards.cards[0],
                hole_cards.cards[1],
                *a,
                *b,
                *c,
                *d,
            ])),
            Board::River([a, b, c, d, e]) => Some(Hand::Seven([
                hole_cards.cards[0],
                hole_cards.cards[1],
                *a,
                *b,
                *c,
                *d,
                *e,
            ])),
            Board::Empty => None,
        }
    }
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

fn card_vec_from_string(hand_string: &str) -> Result<Vec<Card>, String> {
    // Get the chars iterator.
    let mut chars = hand_string.chars();
    // Where we will put the cards
    //
    // We make the assumption that the hands will have 2 plus five cards.
    let mut cards: Vec<Card> = Vec::with_capacity(7);

    let mut cards_deduped: HashSet<Card> = HashSet::with_capacity(7);

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
            if !cards_deduped.insert(c) {
                // If this card is already in the set then error out.
                return Err(format!("This card has already been added {}", c));
            }
            cards.push(c);
        }
    }

    if chars.next() != None {
        return Err(String::from("Extra un-used chars found."));
    }

    Ok(cards)
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

    #[test]
    fn test_board_from_string() {
        assert_eq!(
            Board::new_from_string("AcAh3s4s5s").unwrap(),
            Board::River([
                Card {
                    value: Value::Ace,
                    suit: Suit::Club,
                },
                Card {
                    value: Value::Ace,
                    suit: Suit::Heart,
                },
                Card {
                    value: Value::Three,
                    suit: Suit::Spade,
                },
                Card {
                    value: Value::Four,
                    suit: Suit::Spade,
                },
                Card {
                    value: Value::Five,
                    suit: Suit::Spade,
                },
            ])
        );
        assert_eq!(
            Board::new_from_string("AcAh3s").unwrap(),
            Board::Flop([
                Card {
                    value: Value::Ace,
                    suit: Suit::Club,
                },
                Card {
                    value: Value::Ace,
                    suit: Suit::Heart,
                },
                Card {
                    value: Value::Three,
                    suit: Suit::Spade,
                },
            ])
        );
        assert_eq!(
            Board::new_from_string("AcAh3s7d").unwrap(),
            Board::Turn([
                Card {
                    value: Value::Ace,
                    suit: Suit::Club,
                },
                Card {
                    value: Value::Ace,
                    suit: Suit::Heart,
                },
                Card {
                    value: Value::Three,
                    suit: Suit::Spade,
                },
                Card {
                    value: Value::Seven,
                    suit: Suit::Diamond,
                },
            ])
        );
        assert!(Board::new_from_string("AcAh").is_err());
    }

    #[test]
    fn test_hole_cards_from_string() {
        assert_eq!(
            HoleCards::new_from_string("AcAh").unwrap(),
            HoleCards {
                cards: [
                    Card {
                        value: Value::Ace,
                        suit: Suit::Club,
                    },
                    Card {
                        value: Value::Ace,
                        suit: Suit::Heart,
                    },
                ]
            }
        );

        assert!(HoleCards::new_from_string("AcAh7s").is_err());
    }

    #[test]
    fn test_hand_from_hole_cards_and_board() {
        assert_eq!(
            Hand::from_hole_cards_and_board(
                &HoleCards::new_from_string("AcAh").unwrap(),
                &Board::new_from_string("3s7d8c").unwrap()
            )
            .unwrap(),
            Hand::Five([
                Card {
                    value: Value::Ace,
                    suit: Suit::Club,
                },
                Card {
                    value: Value::Ace,
                    suit: Suit::Heart,
                },
                Card {
                    value: Value::Three,
                    suit: Suit::Spade,
                },
                Card {
                    value: Value::Seven,
                    suit: Suit::Diamond,
                },
                Card {
                    value: Value::Eight,
                    suit: Suit::Club,
                },
            ])
        );
    }
}
