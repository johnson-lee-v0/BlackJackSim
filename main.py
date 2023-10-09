import tkinter as tk
from GUI import BlackjackGUI
import pandas as pd

df_no_ace = pd.read_csv('df_no_usable_ace.csv')
df_ace = pd.read_csv('df_usable_ace.csv')

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")  # Setting an initial window size
    gui = BlackjackGUI(root, df_no_ace, df_ace)
    root.mainloop()