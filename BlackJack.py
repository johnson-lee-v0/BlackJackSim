import random
import pandas as pd

suits = ('Hearts', 'Diamonds', 'Clubs', 'Spades')
ranks = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace')
rank_values = {'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 
                       'Nine': 9, 'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}

def create_deck(num_decks=6):
    deck = [(rank, suit, deck_num) for deck_num in range(1, num_decks+1) for rank in ranks for suit in suits]
    return deck
def shuffle_deck(deck):
    random.shuffle(deck)

def deal_cards(deck):
    return [deck.pop(), deck.pop()], [deck.pop(), deck.pop()]

def hand_value(hand):
    rank_values = {'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 
                   'Nine': 9, 'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}
    value = sum(rank_values[card[0]] for card in hand)
    num_aces = sum(1 for card in hand if card[0] == 'Ace')
    while value > 21 and num_aces:
        value -= 10
        num_aces -= 1
    return value

def determine_winner(player_hand, dealer_hand):
    player_value, dealer_value = hand_value(player_hand), hand_value(dealer_hand)
    if player_value > 21:
        return "Dealer"
    elif dealer_value > 21:
        return "Player"
    elif player_value > dealer_value:
        return "Player"
    elif dealer_value > player_value:
        return "Dealer"
    else:
        return "Tie"

def basic_strategy_advice(player_hand, dealer_hand, df_no_ace, df_ace):
    # Determine if player has a usable ace
    has_usable_ace = any(card[0] == 'Ace' for card in player_hand) and (hand_value(player_hand) + 10 <= 21)

    # Get the player's hand value
    player_value = hand_value(player_hand)

    # If player's hand value is 21 or more, return no advice
    if player_value >= 21:
        return ""
    
    # Get the dealer's face-up card value. We'll assume the dealer's face-up card is the first card in dealer_hand.
    dealer_face_up_card = dealer_hand[0]
    dealer_upcard_value = rank_values.get(dealer_face_up_card[0], 0)

    # Use the appropriate table to get the advice
    if has_usable_ace:
        advice = df_ace[df_ace["Unnamed: 0"] == player_value][str(dealer_upcard_value)].values[0]
    else:
        advice = df_no_ace[df_no_ace["Unnamed: 0"] == player_value][str(dealer_upcard_value)].values[0]

    return advice

def dealer_action(dealer_hand):
    """Determine the dealer's action based on their hand."""
    while hand_value(dealer_hand) < 17:
        return "Hit"
    return "Stand"
