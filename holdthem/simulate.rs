use crate::globals::ALL_CARDS;
use rs_poker::core::{Card, Hand, Rankable};

extern crate rand;
use self::rand::rngs::ThreadRng;
use self::rand::seq::SliceRandom;
use rand::thread_rng;
use std::collections::HashSet;
use std::slice::Iter;

/// The input of a simulation
#[derive(Debug)]
pub struct Game {
    /// Current Player's Hole Cards
    pub hand: Hand,
    /// Opponent Player's Range
    pub range: Vec<Hand>,
    /// Flatten deck
    pub board: Vec<Card>,
}

#[derive(Debug, Clone)]
pub struct SimulationResult {
    pub num_wins: i64,
    pub num_losses: i64,
    pub num_ties: i64,
}

struct FastDrawDeck {
    cards: Vec<Card>,
    /// Current index into the deck
    /// cards[current_index] is the first card eligibe to be drawn, and all cards
    /// afer are also eligible to be drawn
    current_index: usize,
}

impl FastDrawDeck {
    pub fn new(game: &Game) -> Self {
        let mut ineligible_cards: HashSet<Card> = HashSet::new();
        for card in game.hand.iter() {
            ineligible_cards.insert(*card);
        }
        // Note that we don't remove all cards in the range
        for card in game.board.iter() {
            ineligible_cards.insert(*card);
        }

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
        skippable: Iter<Card>,
    ) -> Vec<Card> {
        let mut skippable: HashSet<Card> = skippable.copied().collect();
        let mut cards: Vec<Card> = vec![];
        cards.reserve_exact(num_to_draw);

        while cards.len() < num_to_draw {
            if self.current_index >= self.cards.len() {
                self.cards.shuffle(rng);
                self.current_index = 0;
            }
            let test_card = &self.cards[self.current_index];
            if skippable.contains(test_card) {
                self.current_index += 1;
                continue;
            }
            cards.push(*test_card);
            skippable.insert(*test_card);
        }
        cards
    }
}

pub fn simulate(game: Game, num_to_simulate: i64) -> Result<SimulationResult, String> {
    if game.range.is_empty() {
        return Err("Must have non-empty range".to_string());
    }

    // First, create the deck
    let mut deck = FastDrawDeck::new(&game);

    // Cards to draw
    let num_cards_to_draw = 5 - game.board.len();

    let mut rng = thread_rng();

    let mut simulation_result = SimulationResult {
        num_wins: 0,
        num_losses: 0,
        num_ties: 0,
    };

    for _ in 0..num_to_simulate {
        // Randomy pick the opponent's card
        let villian_hand = game.range.choose(&mut rng).unwrap();

        let next_cards = deck.draw(&mut rng, num_cards_to_draw, villian_hand.iter());

        let hero_full_hand: Hand = Hand::new_with_cards(
            game.hand
                .iter()
                .chain(game.board.iter())
                .chain(next_cards.iter())
                .copied()
                .collect(),
        );
        assert_eq!(hero_full_hand.len(), 7);
        let hero_rank = hero_full_hand.rank();

        let villian_full_hand: Hand = Hand::new_with_cards(
            villian_hand
                .iter()
                .chain(game.board.iter())
                .chain(next_cards.iter())
                .copied()
                .collect(),
        );
        assert_eq!(villian_full_hand.len(), 7);
        let villian_rank = villian_full_hand.rank();

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
    use crate::simulate::{simulate, Game};
    use rs_poker::core::Hand;

    #[test]
    fn test_simulate_pocket_pair() {
        let hand = Hand::new_from_str("KdKh").unwrap();
        let range = ["AdAh", "2c2s"]
            .iter()
            .map(|s| Hand::new_from_str(s).unwrap())
            .collect();
        let game = Game {
            hand,
            range,
            board: vec![],
        };
        let result = simulate(game, 1).unwrap();
        println!("{:?}", result);
    }
}
