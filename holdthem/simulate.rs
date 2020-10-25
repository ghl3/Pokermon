use rs_poker::core::{Card, Deck, Hand, Rank, Rankable};

extern crate rand;
use rand::seq::*;
use rand::thread_rng;

/// The input of a simulation
#[derive(Debug)]
pub struct Game {
    pub hole_cards: Vec<Hand>,
    /// Flatten deck
    pub board: Vec<Card>,
}

#[derive(Debug, Clone)]
pub struct SimulationResult {
    pub num_wins: i64,
    pub num_losses: i64,
    pub num_ties: i64,
}

pub fn simulate(game: Game, num_to_simulate: i64) -> Result<Vec<SimulationResult>, String> {
    if game.hole_cards.len() < 2 {
        return Err(format!("Not enough players"));
    }

    // First, create the deck
    let mut deck = Deck::default();

    // Then, remove known cards
    for h in &game.hole_cards {
        if h.len() != 2 {
            return Err(String::from("Hand passed in doesn't have 2 cards."));
        }
        for c in h.iter() {
            if !deck.remove(*c) {
                return Err(format!("Card {} was already removed from the deck.", c));
            }
        }
    }

    for c in &game.board {
        if !deck.remove(*c) {
            return Err(format!("Card {} was already removed from the deck.", c));
        }
    }

    // Create a flattened deck that we can shuffle
    let mut deck: Vec<Card> = deck.into_iter().collect();
    let mut simulation_results = vec![
        SimulationResult {
            num_wins: 0,
            num_losses: 0,
            num_ties: 0
        };
        game.hole_cards.len()
    ];

    // Cards to draw
    let num_cards_to_draw = 5 - game.board.len();

    //let mut rng = SeedableRng::from_seed(12);
    let mut rng = thread_rng();

    let mut deck_idx: usize = 0;

    for _ in 0..num_to_simulate {
        // We only need to re-shuffle when we get to the end of the deck
        // This is because we "Run it N Times".  This ends up having the same
        // expectation value as re-shuffling between each run.
        if deck_idx + num_cards_to_draw >= deck.len() {
            // Shuffle the deck
            deck.shuffle(&mut rng);
            deck_idx = 0;
        }

        let next_cards = &deck[deck_idx..deck_idx + num_cards_to_draw];
        deck_idx += num_cards_to_draw;

        let mut ranks: Vec<Rank> = vec![];

        for hole_cards in game.hole_cards.iter() {
            let mut hand: Vec<Card> = hole_cards.iter().map(|c| c.clone()).collect();
            hand.reserve_exact(7);
            for c in &game.board {
                hand.push(*c);
            }
            for c in next_cards {
                hand.push(c.clone());
            }
            ranks.push(hand.rank());
        }

        let max_rank = ranks.iter().max().unwrap();
        let exists_tie = ranks.iter().map(|r| (r == max_rank) as i8).sum::<i8>() > 1;

        for (idx, rank) in ranks.iter().enumerate() {
            if rank == max_rank {
                if exists_tie {
                    simulation_results[idx].num_ties += 1
                } else {
                    simulation_results[idx].num_wins += 1
                }
            } else {
                simulation_results[idx].num_losses += 1
            }
        }
    }
    Ok(simulation_results)
}

#[cfg(test)]
mod test {
    use super::*;
    use crate::core::Hand;
    use crate::core::Rank;

    #[test]
    fn test_simulate_pocket_pair() {
        let hands = ["AdAh", "2c2s"]
            .iter()
            .map(|s| Hand::new_from_str(s).unwrap())
            .collect();
        let mut g = Game {
            hole_cards: hands,
            board: vec![],
        };
        let result = simulate(game, 1).unwrap();
        assert!(result.1 >= Rank::OnePair(0));
    }
}
