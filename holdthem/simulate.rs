extern crate rand;

use self::rand::rngs::ThreadRng;
use self::rand::seq::SliceRandom;
use rand::thread_rng;
use rs_poker::core::{Card, Rankable, Suit, Value};
use std::slice::Iter;

use crate::cardset::CardSet;
use crate::globals::ALL_CARDS;
use crate::hand::{Board, Hand, HoleCards};

#[derive(Debug, Clone)]
pub struct SimulationResult {
    pub num_wins: i64,
    pub num_losses: i64,
    pub num_ties: i64,
}

impl SimulationResult {
    pub fn num_simulations(&self) -> i64 {
        self.num_wins + self.num_ties + self.num_losses
    }
    pub fn win_frac(&self) -> Option<f32> {
        match self.num_simulations() {
            0 => None,
            n => Some(self.num_wins as f32 / n as f32),
        }
    }
}

enum DrawnCards {
    Zero,
    One(Card),
    Two(Card, Card),
    Five(Card, Card, Card, Card, Card),
}

impl DrawnCards {
    fn combine(&self, board: &Board) -> Result<Board, String> {
        match (board, self) {
            (Board::River([a, b, c, d, e]), DrawnCards::Zero) => Ok((*board).clone()),
            (Board::Turn([a, b, c, d]), DrawnCards::One(e)) => {
                Ok(Board::River([*a, *b, *c, *d, *e]))
            }
            (Board::Flop([a, b, c]), DrawnCards::Two(d, e)) => {
                Ok(Board::River([*a, *b, *c, *d, *e]))
            }
            (Board::Empty, DrawnCards::Five(a, b, c, d, e)) => {
                Ok(Board::River([*a, *b, *c, *d, *e]))
            }
            _ => Err("Foo".parse().unwrap()),
        }
    }
}

struct FastDrawDeck {
    cards: Vec<Card>,
    /// Current index into the deck
    /// cards[current_index] is the first card eligibe to be drawn, and all cards
    /// afer are also eligible to be drawn
    current_index: usize,
}

impl FastDrawDeck {
    pub fn new<I>(ineligible_cards_iter: I) -> Self
    where
        I: Iterator<Item = Card>,
    {
        let ineligible_cards = CardSet::from_iter(ineligible_cards_iter);

        //   let mut ineligible_cards = CardSet::new();
        //   for card in hand.iter() {
        //       ineligible_cards.insert(card);
        //   }

        //   let ineligible_cards = ineligible_cards.

        // Note that we don't remove all cards in the range
        //for card in board.iter() {
        //    ineligible_cards.insert(card);
        //}

        FastDrawDeck {
            cards: ALL_CARDS
                .iter()
                .filter(|c| !ineligible_cards.contains(c))
                .copied()
                .collect(),
            current_index: 0,
        }
    }

    pub fn draw(
        &mut self,
        rng: &mut ThreadRng,
        num_to_draw: usize,
        skippable: &[Card],
    ) -> Result<DrawnCards, String> {
        let mut skip_set: CardSet = CardSet::from_iter(skippable.iter().map(|c| *c));
        //let mut cards: Vec<Card> = vec![];
        //cards.reserve_exact(num_to_draw);

        assert!(num_to_draw == 0 || num_to_draw == 1 || num_to_draw == 2 || num_to_draw == 5);
        // Create an array of dummy cards of at most length 5, since thats the most
        // number of cards we'll draw.  We use an array and not a vector to keep
        // everything on the stack.
        let mut cards: [Card; 5] = [Card {
            value: Value::Ace,
            suit: Suit::Spade,
        }; 5];

        let mut num_drawn = 0;

        while num_drawn < num_to_draw {
            if self.current_index >= self.cards.len() {
                self.cards.shuffle(rng);
                self.current_index = 0;
            }
            let test_card = &self.cards[self.current_index];
            if skip_set.contains(test_card) {
                self.current_index += 1;
                continue;
            }
            cards[num_drawn] = *test_card;
            skip_set.insert(test_card);
            num_drawn += 1;
        }

        match num_drawn {
            0 => Ok(DrawnCards::Zero),
            1 => Ok(DrawnCards::One(cards[0])),
            2 => Ok(DrawnCards::Two(cards[0], cards[1])),
            5 => Ok(DrawnCards::Five(
                cards[0], cards[1], cards[2], cards[3], cards[4],
            )),
            _ => Err("Invaid number of cards".parse().unwrap()),
        }
    }
}

pub fn simulate(
    hero_hole_cards: &HoleCards,
    range: &Vec<HoleCards>,
    board: &Board,
    num_to_simulate: i64,
) -> Result<SimulationResult, String> {
    if range.is_empty() {
        return Err("Must have non-empty range".to_string());
    }

    // First, create the deck
    let mut deck = FastDrawDeck::new(
        hero_hole_cards
            .slice()
            .iter()
            .chain(board.cards().iter())
            .map(|c| *c),
    );

    // Cards to draw
    let num_cards_to_draw = 5 - board.len();

    let mut rng = thread_rng();

    let mut simulation_result = SimulationResult {
        num_wins: 0,
        num_losses: 0,
        num_ties: 0,
    };

    for _ in 0..num_to_simulate {
        // Randomy pick the opponent's card
        let villian_hole_cards = range.choose(&mut rng).unwrap();

        let drawn_board = deck.draw(&mut rng, num_cards_to_draw, villian_hole_cards.slice())?;
        let full_board: Board = drawn_board.combine(&board)?;

        let hero_hand: Hand = Hand::from_hole_cards_and_board(hero_hole_cards, &full_board);
        let hero_rank = hero_hand.rank();

        let villian_hand: Hand = Hand::from_hole_cards_and_board(villian_hole_cards, &full_board);
        let villian_rank = villian_hand.rank();

        if villian_rank == hero_rank {
            simulation_result.num_ties += 1
        } else if hero_rank <= villian_rank {
            simulation_result.num_losses += 1
        } else {
            simulation_result.num_wins += 1
        }
    }
    Ok(simulation_result)
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test_simulate_pocket_pair() {
        let hole_cards = HoleCards::new_from_string("KdKh").unwrap();
        let range = vec![
            HoleCards::new_from_string("AdAh").unwrap(),
            HoleCards::new_from_string("2c2s").unwrap(),
        ];
        let result = simulate(&hole_cards, &range, &Board::Empty, 1).unwrap();
        println!("{:?}", result);
    }
}
