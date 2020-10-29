// A set holding cards
//

use rs_poker::core::Card;
use std::slice::Iter;

/// A set that holds cards
pub struct CardSet {
    bitmap: u64,
}

fn card_index(card: &Card) -> u32 {
    card.value as u32 * 4 + card.suit as u32
}

fn card_bit_mask(card: &Card) -> u64 {
    let one: u64 = 1;
    one.rotate_left(card_index(card))
}

impl CardSet {
    pub fn new() -> CardSet {
        CardSet { bitmap: 0 }
    }

    pub fn from_iter<I>(cards: I) -> CardSet
    where
        I: Iterator<Item = Card>,
    {
        let mut set = CardSet::new();
        for card in cards {
            set.insert(&card)
        }
        set
    }

    pub fn contains(&self, card: &Card) -> bool {
        self.bitmap & card_bit_mask(card) != 0
    }

    pub fn insert(&mut self, card: &Card) {
        self.bitmap |= card_bit_mask(card)
    }

    pub fn remove(&mut self, card: &Card) {
        self.bitmap &= !card_bit_mask(card)
    }
}

#[cfg(test)]
mod tests {
    // Note this useful idiom: importing names from outer (for mod tests) scope.
    use super::*;
    use rs_poker::core::{Suit, Value};

    #[test]
    fn test_set_contains() {
        let mut set = CardSet::new();

        set.insert(&Card {
            value: Value::Ace,
            suit: Suit::Spade,
        });

        assert!(set.contains(&Card {
            value: Value::Ace,
            suit: Suit::Spade,
        }));

        assert!(!set.contains(&Card {
            value: Value::Ace,
            suit: Suit::Club,
        }));
    }

    #[test]
    fn test_set_multiple_insert() {
        let mut set = CardSet::new();

        set.insert(&Card {
            value: Value::Ace,
            suit: Suit::Spade,
        });

        set.insert(&Card {
            value: Value::Two,
            suit: Suit::Diamond,
        });

        set.insert(&Card {
            value: Value::Ten,
            suit: Suit::Heart,
        });

        assert!(set.contains(&Card {
            value: Value::Ace,
            suit: Suit::Spade,
        }));
        assert!(set.contains(&Card {
            value: Value::Two,
            suit: Suit::Diamond,
        }));
        assert!(set.contains(&Card {
            value: Value::Ten,
            suit: Suit::Heart,
        }));

        assert!(!set.contains(&Card {
            value: Value::Ace,
            suit: Suit::Heart,
        }));
        assert!(!set.contains(&Card {
            value: Value::Two,
            suit: Suit::Club,
        }));
        assert!(!set.contains(&Card {
            value: Value::Ten,
            suit: Suit::Club,
        }));
    }

    #[test]
    fn test_set_removal() {
        let mut set = CardSet::new();

        set.insert(&Card {
            value: Value::Ace,
            suit: Suit::Spade,
        });

        assert!(set.contains(&Card {
            value: Value::Ace,
            suit: Suit::Spade,
        }));

        assert!(!set.contains(&Card {
            value: Value::Ace,
            suit: Suit::Club,
        }));

        set.remove(&Card {
            value: Value::Ace,
            suit: Suit::Spade,
        });

        assert!(!set.contains(&Card {
            value: Value::Ace,
            suit: Suit::Spade,
        }));

        assert!(!set.contains(&Card {
            value: Value::Ace,
            suit: Suit::Club,
        }));
    }
}
