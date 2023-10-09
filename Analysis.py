import sqlite3
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class Analysis:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def retrieve_data(self):
        query = "SELECT player_cards, dealer_cards, action FROM hands"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        return data

    def preprocess_data(self, data):
        rank_values = {'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 
                   'Nine': 9, 'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}
        action_map = {"Hit": 0, "Stand": 1}
        
        numeric_data = []
        for record in data:
            player_cards_str = record[0].split(", ")
            dealer_cards_str = record[1].split(", ")
            
            # Extract only the rank for each card
            player_cards = [card.split(" ")[0] for card in player_cards_str]
            dealer_cards = [card.split(" ")[0] for card in dealer_cards_str]
            
            player_total = sum(rank_values[rank] for rank in player_cards[:2])  # Consider only the first 2 cards
            dealer_card = rank_values[dealer_cards[0]]
            action = action_map[record[2]]
            
            numeric_data.append([player_total, dealer_card, action])
        
        return np.array(numeric_data)

    def perform_clustering(self, data, n_clusters=4):
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(data)
        return kmeans.labels_

    def visualize_clusters(self, data, labels):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        scatter = ax.scatter(data[:, 0], data[:, 1], data[:, 2], c=labels, s=50, cmap='viridis')
        ax.set_xlabel("Player Total (First 2 cards)")
        ax.set_ylabel("Dealer Card")
        ax.set_zlabel("Action (0: Hit, 1: Stand)")
        ax.set_title("Player Behavior Clusters")

        # Setting ticks for each axis
        ax.set_xticks(np.arange(2, 22))  # Player's two-card total can range from 2 to 21
        ax.set_yticks(np.arange(2, 12))  # Dealer's card value can range from 2 to 11 (considering Ace as 11)
        ax.set_zticks([0, 1])  # Action can be 0 or 1

        # Create a legend
        legend_labels = [f"Cluster {i}" for i in set(labels)]
        ax.legend(handles=scatter.legend_elements()[0], labels=legend_labels)

        plt.show()


    def analyze(self):
        raw_data = self.retrieve_data()
        processed_data = self.preprocess_data(raw_data)
        
        cluster_labels = self.perform_clustering(processed_data)
        self.visualize_clusters(processed_data, cluster_labels)

if __name__ == "__main__":
    analysis = Analysis('game_data.db')
    analysis.analyze()
