from deuces import Card, Deck, Evaluator

board = [Card.new("Ah"), Card.new("Kd"), Card.new("Jc")]
hand = [Card.new("Qs"), Card.new("Th")]

Card.print_pretty_cards(board + hand)

evaluator = Evaluator()

print(evaluator.evaluate(board, hand))

deck = Deck()
board = deck.draw(5)
player1_hand = deck.draw(2)
player2_hand = deck.draw(2)
Card.print_pretty_cards(board)
Card.print_pretty_cards(player1_hand)
Card.print_pretty_cards(player2_hand)

hands = [player1_hand, player2_hand]

evaluator.hand_summary(board, hands)
