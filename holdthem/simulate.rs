extern crate rand;

use self::rand::rngs::ThreadRng;
use self::rand::seq::SliceRandom;
use rand::thread_rng;
use rs_poker::core::{Card, Rankable, Suit, Value};

use crate::cardset::CardSet;
use crate::globals::ALL_CARDS;
use crate::hand::{Board, Hand, HoleCards};
use crate::stack_array::StackArray;

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

        let mut cards: StackArray<Card> = StackArray::Zero;

        while cards.len() < num_to_draw {
            if self.current_index >= self.cards.len() {
                self.cards.shuffle(rng);
                self.current_index = 0;
            }
            let test_card = &self.cards[self.current_index];
            if skip_set.contains(test_card) {
                self.current_index += 1;
                continue;
            }
            cards = cards.push(*test_card);
            skip_set.insert(test_card);
        }

        match cards {
            StackArray::Zero => Ok(DrawnCards::Zero),
            StackArray::One(a) => Ok(DrawnCards::One(a)),
            StackArray::Two(a, b) => Ok(DrawnCards::Two(a, b)),
            StackArray::Five(a, b, c, d, e) => Ok(DrawnCards::Five(a, b, c, d, e)),
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
            .copied(),
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

        let hero_hand: Hand =
            Hand::from_hole_cards_and_board(hero_hole_cards, &full_board).ok_or("Foo")?;
        let hero_rank = hero_hand.rank();

        let villian_hand: Hand =
            Hand::from_hole_cards_and_board(villian_hole_cards, &full_board).ok_or("Foo")?;
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
