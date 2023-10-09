import random
import numpy as np
from BlackJack import suits,ranks,create_deck,shuffle_deck,deal_cards,hand_value,determine_winner 

# Essential functions and classes from BlackJack.py

class EnhancedBlackjackEnv:
    def __init__(self, num_decks=6):
        self.deck = create_deck(num_decks)
        shuffle_deck(self.deck)
        self.player_hand, self.dealer_hand = deal_cards(self.deck)
    
    def reset(self):
        self.player_hand, self.dealer_hand = deal_cards(self.deck)
        if len(self.deck) < 20:
            self.deck = create_deck()
            shuffle_deck(self.deck)
        return self._get_state()
    
    def _get_state(self):
        rank_values = {'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 
                       'Nine': 9, 'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}
        dealer_visible_card_value = rank_values[self.dealer_hand[0][0]]
        player_value = hand_value(self.player_hand)
        usable_ace = 1 if (player_value <= 21 and any(card[0] == 'Ace' for card in self.player_hand)) else 0
        return (player_value, dealer_visible_card_value, usable_ace)
    
    def step(self, action):
        if action == "Hit":
            self.player_hand.append(self.deck.pop())
            if hand_value(self.player_hand) > 21:
                return self._get_state(), -1, True
        
        if action == "Stand":
            while hand_value(self.dealer_hand) < 17:
                self.dealer_hand.append(self.deck.pop())
            winner = determine_winner(self.player_hand, self.dealer_hand)
            if winner == "Player":
                return self._get_state(), 1, True
            elif winner == "Dealer":
                return self._get_state(), -1, True
            else:
                return self._get_state(), 0, True
        
        return self._get_state(), 0, False

# Q-learning parameters
alpha = 0.2
gamma_mc = 0.9
action_to_index = {"Hit": 0, "Stand": 1}
index_to_action = {0: "Hit", 1: "Stand"}

def choose_action_enhanced(state, q_table):
    return index_to_action[np.argmax(q_table[min(state[0], 21), min(state[1]-1, 11), state[2], :])]

# Monte Carlo training loop with corrected choose_action function
q_table_corrected = np.zeros((22, 12, 2, 2))  # (player hand value, dealer's visible card value, usable ace, actions)
num_episodes_mc_corrected = 1000000
env_mc_corrected = EnhancedBlackjackEnv()

for _ in range(num_episodes_mc_corrected):
    state = env_mc_corrected.reset()
    done = False
    episode = []
    
    # Generate an episode
    while not done:
        action = choose_action_enhanced(state, q_table_corrected)
        next_state, reward, done = env_mc_corrected.step(action)
        episode.append((state, action, reward))
        state = next_state

    G = 0  # Expected return
    for t in reversed(range(len(episode))):
        state_t, action_t, reward_t = episode[t]
        G = gamma_mc * G + reward_t
        if (state_t, action_t) not in [(x[0], x[1]) for x in episode[:t]]:
            # Encourage standing for totals 18 or greater (excluding soft hands)
            q_table_corrected[17:, :, 0, action_to_index["Stand"]] = 1e5

            # Encourage hitting for soft 17
            q_table_corrected[18:, :, 1, action_to_index["Stand"]] = 1e5

            # Existing Q-value update logic
            old_value = q_table_corrected[state_t[0], state_t[1]-1, state_t[2], action_to_index[action_t]]
            q_table_corrected[state_t[0], state_t[1]-1, state_t[2], action_to_index[action_t]] = old_value + alpha * (G - old_value)

# Re-evaluate the agent's performance after defining the evaluate_enhanced_agent function

def evaluate_enhanced_agent(env, q_table, num_games=10000):
    wins = 0
    ties = 0
    losses = 0
    
    for _ in range(num_games):
        state = env.reset()
        done = False
        
        while not done:
            action = index_to_action[np.argmax(q_table[state[0], state[1]-1, state[2]])]  # Updated for enhanced state
            next_state, reward, done = env.step(action)
            state = next_state
        
        if reward == 1:
            wins += 1
        elif reward == 0:
            ties += 1
        else:
            losses += 1
            
    win_rate = wins / num_games
    tie_rate = ties / num_games
    loss_rate = losses / num_games
    
    return win_rate, tie_rate, loss_rate

# Re-running the evaluation after including the evaluate_enhanced_agent function

win_rate_corrected, tie_rate_corrected, loss_rate_corrected = evaluate_enhanced_agent(EnhancedBlackjackEnv(), q_table_corrected)
win_rate_corrected, tie_rate_corrected, loss_rate_corrected

print("Training completed!")
print(win_rate_corrected, tie_rate_corrected, loss_rate_corrected)

# Re-defining the necessary variables and constants from the initial code snippet

import pandas as pd

def best_action_for_state(q_table, player_value, dealer_card, usable_ace):
    return index_to_action[np.argmax(q_table[player_value, dealer_card, usable_ace, :])]

# Create the table
table_usable_ace = np.empty((20, 10), dtype=object)
table_no_usable_ace = np.empty((20, 10), dtype=object)

for player_value in range(2, 22):
    for dealer_card in range(1, 11):
        table_usable_ace[player_value-2, dealer_card-2] = best_action_for_state(q_table_corrected, player_value, dealer_card, 1)
        table_no_usable_ace[player_value-2, dealer_card-2] = best_action_for_state(q_table_corrected, player_value, dealer_card, 0)

# Convert the tables to DataFrames for visualization
df_usable_ace = pd.DataFrame(table_usable_ace, index=range(2, 22), columns=range(2, 12))
df_no_usable_ace = pd.DataFrame(table_no_usable_ace, index=range(2, 22), columns=range(2, 12))

df_usable_ace.to_csv('df_usable_ace.csv')
df_no_usable_ace.to_csv('df_no_usable_ace.csv')