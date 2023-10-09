import tkinter as tk
from tkinter import messagebox, PhotoImage
from DataCollection import DatabaseManager
from BlackJack import suits, ranks,create_deck, shuffle_deck, deal_cards, hand_value, determine_winner, basic_strategy_advice, dealer_action
from Analysis import Analysis

class BlackjackGUI:
    def __init__(self, master,df_no_ace,df_ace):
        self.master = master
        master.title("Blackjack")
        self.font = ("Arial", 14)
        self.bg_color='#F0F0F0'

        self.main_frame = tk.Frame(master,bg=self.bg_color)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.db_manager = DatabaseManager()
        self.current_game_id = self.db_manager.insert_game()
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.df_no_ace = df_no_ace
        self.df_ace = df_ace

        # Game initialization
        self.deck = create_deck()
        shuffle_deck(self.deck)
        self.player_hand = []
        self.dealer_hand = []
        self.dealer_card_hidden = True

        self.card_images = {}
        for suit in suits:
            for rank in ranks:
                image_name = f"{rank}_of_{suit}.png".lower().replace(" ", "_")
                self.card_images[(rank, suit)] = tk.PhotoImage(file=f"cards/{image_name}")

        self.hidden_card_image = self.load_card_image_back()

        # Balance and Betting UI
        self.player_balance = 1000
        self.bet_amount = 0

        # Update UI elements with the consistent font and color
        self.prompt_label = tk.Label(self.main_frame, text="Place your bet to start the game!", font=("Arial", 16), bg=self.bg_color, fg="Black")
        self.bet_label = tk.Label(self.main_frame, text=f"Balance: ${self.player_balance}", font=self.font, bg=self.bg_color, fg="Black")
        
        # Adjust the width of the bet_entry widget
        self.bet_entry = tk.Entry(self.main_frame, font=self.font, width=10)
        self.bet_button = tk.Button(self.main_frame, text="Place Bet", command=self.place_bet)

        # Dealer's frame
        self.dealer_frame = tk.Frame(self.main_frame, bg=self.bg_color)

        # Player's frame
        self.player_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.buttons_frame = tk.Frame(self.main_frame)
        self.hit_button = tk.Button(self.buttons_frame, text="Hit", command=self.hit, state=tk.DISABLED)
        self.stand_button = tk.Button(self.buttons_frame, text="Stand", command=self.stand, state=tk.DISABLED)
        self.advice_label = tk.Label(self.main_frame)

        # Placeholder for the card image labels
        self.player_card_labels = []
        self.dealer_card_labels = []

        self.analysis_button = tk.Button(self.main_frame, text="Analyze Play", command=self.perform_analysis)

        self.analysis = Analysis('game_data.db')

        self.deck_table_frame = tk.Frame(self.main_frame)
        self.deck_table_frame.grid(row=0, column=2, rowspan=8, sticky=tk.N+tk.W+tk.E)

        self.deck_labels = {}
        for rank in ranks:
            self.deck_labels[rank] = tk.Label(self.deck_table_frame, text=f"{rank}: {sum(1 for card in self.deck if card[0] == rank)}")
            self.deck_labels[rank].pack(anchor=tk.W)

        self.total_cards_label = tk.Label(self.deck_table_frame, text=f"Total Cards: {len(self.deck)}")
        self.total_cards_label.pack(pady=10)
        
        # Update UI elements with the consistent font and color
        self.prompt_label.grid(row=0, column=0, pady=50, columnspan=2, sticky=tk.W+tk.E)
        self.bet_label.grid(row=1, column=0, pady=20, sticky=tk.W+tk.E)
        self.bet_entry.grid(row=1, column=1, pady=20, padx=(0, 20), sticky=tk.E)
        self.bet_button.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)
        self.dealer_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)
        self.player_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)
        self.buttons_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)
        self.hit_button.pack(side=tk.LEFT, padx=5)
        self.stand_button.pack(side=tk.LEFT, padx=5)
        self.advice_label.grid(row=6, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)
        self.analysis_button.grid(row=7, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)

        # Adjusting weights for rows and columns in main_frame
        self.main_frame.grid_rowconfigure(5, weight=1)
        self.main_frame.grid_rowconfigure(6, weight=1)
        self.main_frame.grid_rowconfigure(7, weight=1)

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)  # for the deck table frame

    # Modify the hit and stand functions to update the deck details table after each action
    
    def update_deck_table(self):
        # Create a temporary deck without adding back any of the dealer's or player's cards
        temp_deck = list(self.deck)
        
        # If the dealer's card is hidden, add back only the dealer's hidden card to the temporary deck
        if self.dealer_card_hidden:
            temp_deck.append(self.dealer_hand[1])  # This adds only the dealer's hidden card

        for rank in ranks:
            self.deck_labels[rank].config(text=f"{rank}: {sum(1 for card in temp_deck if card[0] == rank)}")
        
        self.total_cards_label.config(text=f"Total Cards: {len(temp_deck)}")


    def on_closing(self):
        self.db_manager.close()
        self.master.destroy()

    def perform_analysis(self):
        self.analysis.analyze()
            
    def load_card_image(self, card):
        rank, suit = card[0], card[1]
        image = self.card_images[(rank, suit)]

        base_width = max(self.master.winfo_width() // 10, 50)  # Consistent resizing logic
        width_percent = (base_width / float(image.width()))
        new_height = int((float(image.height()) * float(width_percent)))
        zoom_factor = max(int(width_percent*10), 1)
        image = image.zoom(zoom_factor, zoom_factor)
        image = image.subsample(10, 10)

        return image

    def load_card_image_back(self):
        image = tk.PhotoImage(file="cards/back.png")
        base_width = max(self.master.winfo_width() // 10, 50)
        width_percent = (base_width / float(image.width()))
        new_height = int((float(image.height()) * float(width_percent)))
        zoom_factor = max(int(width_percent*10), 1)
        image = image.zoom(zoom_factor, zoom_factor)
        image = image.subsample(10, 10)
        return image
    
    def ensure_deck(self, threshold=78):
        """Reshuffle the deck if it has fewer than the threshold number of cards."""
        if len(self.deck) < threshold:
            self.deck = create_deck()
            shuffle_deck(self.deck)

    def new_game(self):
        # Ensure there are enough cards in the deck
        self.ensure_deck()
        # Reset hands
        self.player_hand, self.dealer_hand = deal_cards(self.deck)
        
        # Set dealer card as hidden before updating the total counter and deck table
        self.dealer_card_hidden = True
        
        # Update the cumulative counter for the new cards, only accounting for the dealer's visible card and player's cards
        self.update_deck_table()

        # Check for natural blackjacks
        if hand_value(self.player_hand) == 21:
            self.dealer_card_hidden = False  # Reveal dealer's card
            self.update_display()  # Update display to show the dealer's cards
            self.update_deck_table()  # Reflect the revealed card in the deck table
            if hand_value(self.dealer_hand) == 21:  # Both player and dealer have blackjack
                winner = "Tie"
                self.player_balance += self.bet_amount  # Return the bet amount
            else:  # Only player has blackjack
                winner = "Player"
                self.player_balance += int(self.bet_amount * 2.5)  # 3:2 payout + original bet
            self.bet_label.config(text=f"Balance: ${self.player_balance}")
            messagebox.showinfo("Result", f"{winner} wins due to natural blackjack!")
            
            # Prepare for the next round
            self.bet_entry.config(state=tk.NORMAL)
            self.bet_button.config(state=tk.NORMAL)
            self.hit_button.config(state=tk.DISABLED)
            self.stand_button.config(state=tk.DISABLED)
            return  # Exit the new_game method
        
        # Clear frames
        for widget in self.player_frame.winfo_children():
            widget.destroy()
        for widget in self.dealer_frame.winfo_children():
            widget.destroy()

        # Re-add headers
        tk.Label(self.player_frame, text="Player's Cards:", bg=self.bg_color, fg="black").pack(side=tk.BOTTOM)
        tk.Label(self.dealer_frame, text="Dealer's Cards:", bg=self.bg_color, fg="black").pack(side=tk.BOTTOM)
        
        # Recreate dealer_cards_frame
        self.dealer_cards_frame = tk.Frame(self.dealer_frame)
        self.dealer_cards_frame.pack(pady=10)
    
        # Enable game buttons for the new round
        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)
        
        # Disable betting entry and button during gameplay
        self.bet_entry.config(state=tk.DISABLED)
        self.bet_button.config(state=tk.DISABLED)

        # Display advice at the start of the game
        advice = basic_strategy_advice(self.player_hand, self.dealer_hand, self.df_no_ace, self.df_ace)
        self.advice_label.config(text=f"Strategy Advice: {advice}")
        self.update_display()

    
    def hit(self):
        # Ensure there are enough cards in the deck
        self.ensure_deck()
        
        self.player_hand.append(self.deck.pop())
        
        # Update the display before checking for bust
        self.update_display()
        self.update_deck_table()
        if hand_value(self.player_hand) > 21:
            self.dealer_card_hidden = False
            self.update_display()
            self.update_deck_table()
            # Player busts, so the dealer wins.
            winner = "Dealer"
            # Save hand data to the database
            player_cards_str = ", ".join([f"{card[0]} of {card[1]}" for card in self.player_hand])
            dealer_cards_str = ", ".join([f"{card[0]} of {card[1]}" for card in self.dealer_hand])
            advice = basic_strategy_advice(self.player_hand, self.dealer_hand, self.df_no_ace, self.df_ace)

            action = "Hit"
            self.db_manager.insert_hand(self.current_game_id, player_cards_str, dealer_cards_str, advice, action, winner)
            ### Next Round Loading
            self.bet_label.config(text=f"Balance: ${self.player_balance} - Player busts! Dealer wins.")
            self.bet_entry.config(state=tk.NORMAL)
            self.bet_button.config(state=tk.NORMAL)
            self.hit_button.config(state=tk.DISABLED)
            self.stand_button.config(state=tk.DISABLED)
        elif hand_value(self.player_hand) == 21:
            self.stand()  # Automatically stand if player's hand totals 21
        else:
            advice = basic_strategy_advice(self.player_hand, self.dealer_hand, self.df_no_ace, self.df_ace)
            self.advice_label.config(text=f"Strategy Advice: {advice}")
    
    def place_bet(self):
            try:
                bet = int(self.bet_entry.get())
                if bet <= self.player_balance and bet > 0:
                    self.bet_amount = bet
                    self.player_balance -= bet
                    self.bet_label.config(text=f"Balance: ${self.player_balance}")
                    
                    # Enable game buttons
                    self.hit_button.config(state=tk.NORMAL)
                    self.stand_button.config(state=tk.NORMAL)
                    
                    # Disable betting entry and button
                    self.bet_entry.config(state=tk.DISABLED)
                    self.bet_button.config(state=tk.DISABLED)
                    self.prompt_label.destroy()
                    self.new_game()
                else:
                    messagebox.showwarning("Invalid Bet", "Please enter a valid bet amount. Type 1")
            except ValueError:
                messagebox.showwarning("Invalid Bet", "Please enter a valid bet amount.")

    def stand(self):
        self.ensure_deck()
        print("Player's Hand",self.player_hand)
        cards_dealt_in_round = self.player_hand.copy() + [self.dealer_hand[1]]  # Including player's cards and dealer's revealed card
        self.dealer_card_hidden = False
        
        self.update_deck_table()  # Update the deck table to reflect the revealed card
        self.update_display()  # Update display to show the revealed card
        print("Dealer's hand before action:", self.dealer_hand)
        action = dealer_action(self.dealer_hand)
        print("Dealer decided to:", action)
        while action == "Hit":
            new_card = self.deck.pop()
            print("Dealer drew:", new_card)
            self.dealer_hand.append(new_card)
            cards_dealt_in_round.append(new_card)  # Add the new card to the list
            self.update_deck_table()  # Update the deck table for the new dealer card
            self.update_display()  # Update display to show the new card
            print("Dealer's hand before action:", self.dealer_hand)
            action = dealer_action(self.dealer_hand)
            print("Dealer decided to:", action)

        winner = determine_winner(self.player_hand, self.dealer_hand)
        
        if winner == "Player":
            if hand_value(self.player_hand) == 21 and len(self.player_hand) == 2:
                self.player_balance += int(self.bet_amount * 2.5)  # 3:2 payout + original bet
            else:
                self.player_balance += self.bet_amount * 2  # Double the bet amount
        elif winner == "Dealer":
            pass  # Player already lost their bet
        else:
            self.player_balance += self.bet_amount  # Return the bet amount

        self.update_deck_table()  # Reflect the final total_counter in the deck table
        advice = basic_strategy_advice(self.player_hand, self.dealer_hand, self.df_no_ace, self.df_ace)
        self.advice_label.config(text=f"Strategy Advice: {advice}")
        self.bet_label.config(text=f"Balance: ${self.player_balance}")
        messagebox.showinfo("Result", f"{winner} wins!")
        # After determining the winner, prepare for the next round
        self.bet_entry.config(state=tk.NORMAL)
        self.bet_button.config(state=tk.NORMAL)
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)

        # Save hand data to the database
        player_cards_str = ", ".join([f"{card[0]} of {card[1]}" for card in self.player_hand])
        dealer_cards_str = ", ".join([f"{card[0]} of {card[1]}" for card in self.dealer_hand])
        action = "Stand"  # Since this is the stand method
        self.db_manager.insert_hand(self.current_game_id, player_cards_str, dealer_cards_str, advice, action, winner)

    
    def update_display(self):
        # Clear the current displayed cards
        for label in self.player_card_labels + self.dealer_card_labels:
            label.destroy()
        self.player_card_labels = []
        self.dealer_card_labels = []

        # Player's cards
        for card in self.player_hand:
            image = self.load_card_image(card)
            label = tk.Label(self.player_frame, image=image, bg=self.bg_color)
            label.image = image  # Keep a reference
            label.pack(side=tk.LEFT, padx=5)
            self.player_card_labels.append(label)

        # Dealer's cards
        for idx, card in enumerate(self.dealer_hand):
            # If dealer_card_hidden is True, only show the back of the second card.
            # Otherwise, show both cards.
            if self.dealer_card_hidden and idx == 1:  
                image = self.load_card_image_back()
            else:
                image = self.load_card_image(card)
            label = tk.Label(self.dealer_frame, image=image, bg=self.bg_color)
            label.image = image  # Keep a reference
            label.pack(side=tk.LEFT, padx=5)
            self.dealer_card_labels.append(label)


