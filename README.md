# Pokermon
Poker using AI


## Desired Strategy:

- Train using Actor-Critic Policy Gradient to get the EV of the current
position and a range of moves to make
- Model is a multi-layer, multi-head LSTM that takes in the full history of actions
- Train a model to predict unknown hands (based on visible state and player's actions)
- At each street, for each player, predict a range of hands
- For the most probably hand ranges, use MonteCarloTreeSearch to determine
how the game will play out (using the AI's policy to generate the tree)
- Pick the move with the highest EV using MCTS