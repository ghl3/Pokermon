use crate::globals;
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

pub fn card_from_index(i: usize) -> Card {
    globals::ALL_CARDS[i]
}

/// This must match the index of the card in globals::ALL_CARDS
pub fn card_index(card: &Card) -> usize {
    card.value as usize * 4 + card.suit as usize
}

#[derive(Debug, PartialEq, Clone)]
pub struct HoleCards {
    pub cards: [Card; 2],
}

impl HoleCards {
    pub fn new_from_cards(c1: Card, c2: Card) -> HoleCards {
        if c1 > c2 {
            HoleCards { cards: [c1, c2] }
        } else {
            HoleCards { cards: [c2, c1] }
        }
    }

    pub fn new_from_string(hand_string: &str) -> Result<HoleCards, String> {
        match card_vec_from_string(hand_string)?[..] {
            [a, b] => Ok(HoleCards::new_from_cards(a, b)),
            _ => Err("Cannot parse hole cards".parse().unwrap()),
        }
    }

    pub fn new_from_index(i: usize) -> HoleCards {
        globals::ALL_HANDS[i].clone()
    }

    pub fn slice(&self) -> &[Card] {
        &self.cards[..]
    }

    pub fn preflop_index(&self) -> usize {
        let paired = self.cards[0].value == self.cards[1].value;
        let suited = self.cards[0].suit == self.cards[1].suit;

        if paired {
            self.cards[0].value as usize
        } else {
            let r1 = self.cards[0].value as usize;
            let r2 = self.cards[1].value as usize;

            let n = r1 - 1;
            let offset = n * (n + 1) / 2;

            13 + 2 * (offset + r2) + if suited { 0 } else { 1 }
        }
    }

    /// This must match the index of the hand in globals::ALL_HANDS
    pub fn index(&self) -> usize {
        // c1 is the smaller card.  That is the 'first' one since we iterate
        // from smaller cards to larger cards.  These indices start at 0.
        let c1 = card_index(&self.cards[1]);
        let c2 = card_index(&self.cards[0]);

        // Sum(i=1 to c1) (52 - c1) if c1>0 else 0
        let offset = 52 * c1 - c1 * (c1 + 1) / 2;
        offset + (c2 - c1 - 1)
    }
}

#[derive(Debug, PartialEq, Clone)]
pub enum Board {
    Flop([Card; 3]),
    Turn([Card; 4]),
    River([Card; 5]),
}

impl Board {
    pub fn cards(&self) -> &[Card] {
        match self {
            Board::Flop(x) => x,
            Board::Turn(x) => x,
            Board::River(x) => x,
        }
    }

    pub fn len(&self) -> usize {
        match self {
            Board::Flop(_) => 3,
            Board::Turn(_) => 4,
            Board::River(_) => 5,
        }
    }

    pub fn new_from_string(hand_string: &str) -> Result<Option<Board>, String> {
        match card_vec_from_string(hand_string)?[..] {
            [] => Ok(None),
            [a, b, c] => Ok(Some(Board::Flop([a, b, c]))),
            [a, b, c, d] => Ok(Some(Board::Turn([a, b, c, d]))),
            [a, b, c, d, e] => Ok(Some(Board::River([a, b, c, d, e]))),
            _ => Err("Cannot parse board".parse().unwrap()),
        }
    }

    pub fn new_from_string_vec(hand_strings: &[String]) -> Result<Option<Board>, String> {
        match hand_strings {
            [a, b, c] => Ok(Some(Board::Flop([
                card_from_str(a)?,
                card_from_str(b)?,
                card_from_str(c)?,
            ]))),
            [a, b, c, d] => Ok(Some(Board::Turn([
                card_from_str(a)?,
                card_from_str(b)?,
                card_from_str(c)?,
                card_from_str(d)?,
            ]))),
            [a, b, c, d, e] => Ok(Some(Board::River([
                card_from_str(a)?,
                card_from_str(b)?,
                card_from_str(c)?,
                card_from_str(d)?,
                card_from_str(e)?,
            ]))),
            [] => Ok(None),
            _ => Err("Cannot parse board".parse().unwrap()),
        }
    }

    pub fn new_from_indices(hand_strings: &[i32]) -> Result<Option<Board>, String> {
        match hand_strings {
            [a, b, c] => Ok(Some(Board::Flop([
                card_from_index(*a as usize),
                card_from_index(*b as usize),
                card_from_index(*c as usize),
            ]))),
            [a, b, c, d] => Ok(Some(Board::Turn([
                card_from_index(*a as usize),
                card_from_index(*b as usize),
                card_from_index(*c as usize),
                card_from_index(*d as usize),
            ]))),
            [a, b, c, d, e] => Ok(Some(Board::River([
                card_from_index(*a as usize),
                card_from_index(*b as usize),
                card_from_index(*c as usize),
                card_from_index(*d as usize),
                card_from_index(*e as usize),
            ]))),
            [] => Ok(None),
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
    pub fn from_hole_cards_and_board(hole_cards: &HoleCards, board: &Board) -> Hand {
        match board {
            Board::Flop([a, b, c]) => {
                Hand::Five([hole_cards.cards[0], hole_cards.cards[1], *a, *b, *c])
            }
            Board::Turn([a, b, c, d]) => {
                Hand::Six([hole_cards.cards[0], hole_cards.cards[1], *a, *b, *c, *d])
            }
            Board::River([a, b, c, d, e]) => {
                Hand::Seven([hole_cards.cards[0], hole_cards.cards[1], *a, *b, *c, *d, *e])
            }
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
    use crate::globals::ALL_CARDS;
    use crate::globals::ALL_HANDS;
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
            Some(Board::River([
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
            ]))
        );
        assert_eq!(
            Board::new_from_string("AcAh3s").unwrap(),
            Some(Board::Flop([
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
            ]))
        );
        assert_eq!(
            Board::new_from_string("AcAh3s7d").unwrap(),
            Some(Board::Turn([
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
            ]))
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
                        suit: Suit::Heart,
                    },
                    Card {
                        value: Value::Ace,
                        suit: Suit::Club,
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
                &Board::new_from_string("3s7d8c").unwrap().unwrap()
            ),
            Hand::Five([
                Card {
                    value: Value::Ace,
                    suit: Suit::Heart,
                },
                Card {
                    value: Value::Ace,
                    suit: Suit::Club,
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

    #[test]
    fn test_card_index() {
        for c in ALL_CARDS.iter() {
            assert_eq!(*c, ALL_CARDS[card_index(c)]);
        }
    }

    #[test]
    fn test_hand_index() {
        for h in ALL_HANDS.iter() {
            assert_eq!(*h, ALL_HANDS[h.index()]);
        }
    }
}
