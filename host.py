import socket
import pickle
import threading
import tkinter as tk
from hangmanstuff import HangmanDisplay, KeyboardSelection, WordGuesser, check_win
import time


# handles connection from a client
def networking():
    global data
    host = ""
    port = 43535

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        data["connected"] = True
        playAgain = True
        while playAgain:
            # get the opponent's word, then send them ours once we have decided
            data["client word"] = pickle.loads(conn.recv(2048))
            while True:
                if data["host word"] and data["win"] == "none":
                    conn.send(pickle.dumps(data["host word"]))
                    break
                time.sleep(0.2)

            while True:
                # get the opponent's guess, then send ours when decided
                guessdata = conn.recv(2048)
                while len(data["host guesses"]) != len(data["client guesses"]) + 1:
                    time.sleep(0.2)
                conn.send(pickle.dumps(data["host guesses"][-1]))
                data["client guesses"].append(pickle.loads(guessdata))
                if not guessdata:
                    break
                win = check_win(data)
                if win != "none" or not conn:
                    if not conn:
                        playAgain = False
                    data["win"] = win
                    break


# displays the game stats including word completion, enemy guesses, and lives in the form of a hangman graphic
class StatsDisplay(tk.Label):
    def __init__(self, master):
        tk.Label.__init__(self, master, bg="#e8cb75")
        self.guessesDisplay = tk.Label(self, width=20, height=4, bg="#e8cb75", fg="#000000", font=("Arial", 30))
        self.guessesDisplay.grid(row=0, column=1, rowspan=2)

        self.ownHangmanText = tk.Label(self, height=2, bg="#e8cb75", fg="#000000", font=("Arial", 10),
                                       text="Own lives")
        self.enemyHangmanText = tk.Label(self, height=2, bg="#e8cb75", fg="#000000", font=("Arial", 10),
                                         text="Opponent's lives")

        self.enemyHangman = HangmanDisplay(self)
        self.enemyHangman.grid(row=1, column=2, padx=20, pady=(0, 20))
        self.enemyHangmanText.grid(row=0, column=2)

        self.ownHangman = HangmanDisplay(self)
        self.ownHangman.grid(row=1, column=0, padx=20, pady=(0, 20))
        self.ownHangmanText.grid(row=0, column=0)

        self.enemyGuessedDisplay = tk.Label(self, bg="#e8cb75", fg="#000000", font=("Arial", 15), anchor="w",
                                            width=80)
        self.enemyGuessedDisplay.grid(row=2, column=0, columnspan=3, pady=5)

        self.turnWaitText = tk.Label(self, bg="#e8cb75", fg="#000000", font=("Arial", 15), text="", height=1, width=80)
        self.turnWaitText.grid(row=3, column=0, columnspan=3, pady=5)

    # gets the new values of everything to display
    def refresh(self):
        ownStage = 0
        enemyStage = 0
        if data["win"] != "none":  # displays the opponent's word when the game is over
            text = data["client word"] + "\n"
        else:
            text = "\n"

        # logic for displaying correct guesses
        for letter in data["client word"]:
            if letter in data["host guesses"]:
                text = text + " " + letter + " "
            else:
                text = text + " _ "
        for letter in data["host guesses"]:
            if letter not in data["client word"]:
                ownStage += 1
            if letter == data["client word"]:
                text = letter
        for letter in data["client guesses"]:
            if letter not in data["host word"]:
                enemyStage += 1

        self.guessesDisplay.config(text=text)
        self.enemyGuessedDisplay.config(text="Opponent has guessed: " + ", ".join(data["client guesses"]))
        self.ownHangman.refresh(ownStage)
        self.enemyHangman.refresh(enemyStage)
        if len(data["client guesses"]) < len(data["host guesses"]):
            self.turnWaitText.config(text="Waiting on opponent...")
        else:  # turnWaitText also doubles up as a game end display
            self.turnWaitText.config(text={"none": "", "host": "You Win", "client": "You Lose",
                                           "draw": "Draw", "lose": "You Both Lose"}[data["win"]])


# attempt to guess a letter
def add(letter, keyboard):
    if data["win"] == "none" and len(data["client guesses"]) == len(data["host guesses"]):
        data["host guesses"].append(letter)
        keyboard.disable(letter)


# attempt to guess a word (clears word entry if successful)
def addw(word, entry):
    if data["win"] == "none" and (len(data["client guesses"]) == len(data["host guesses"])
                                  and word not in data["host guesses"]) and word.isalpha():
        data["host guesses"].append(word.upper())
        entry.entry.delete(0, tk.END)


# the main screen display when the game is in progress
# contains all aspects of the ongoing game
class MainScreen(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, bg="#e8cb75", *args, **kwargs)
        self.statsDisplay = StatsDisplay(self)
        self.statsDisplay.grid(row=0)
        self.alphabet = KeyboardSelection(self, add, bg="#e8cb75")
        self.alphabet.grid(row=1, sticky="nesw")
        self.entry = WordGuesser(self, addw)
        self.entry.grid(row=2, sticky="nesw")
        self.playAgain = tk.Button(self, bg="#fcad03", fg="#ffffff", width=20, font=("Arial", 20), text="Play Again",
                                   command=self.play_again)
        self.ended = False
        self.master = master

    # reverts the game to the word selection stage
    def play_again(self):
        sa = WordSelect(self.master)
        sa.pack()
        sa.refresh()
        self.destroy()

    def refresh(self, *args, **kwargs):
        self.statsDisplay.refresh()
        self.after(500, self.refresh)
        w = data["win"]
        if w != "none" and not self.ended:
            self.ended = True
            self.entry.destroy()
            self.playAgain.grid(row=2, pady=(5, 10))


# contains all aspects of the word selection screen at the start of a game
class WordSelect(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, bg="#e8cb75", *args, **kwargs)
        data["client guesses"] = []
        data["host guesses"] = []
        data["client word"] = ""
        data["host word"] = ""
        self.master = master
        self.entry = WordGuesser(self, self.play, text="Play with this word")
        self.entry.pack(pady=5)
        self.ended = False

    # all this does is update the word record to a given word
    # the game does not actually progress until both players choose a word
    def play(self, text, *args):
        if text.isalpha():
            if not self.ended:
                data["win"] = "none"
                data["host word"] = text.upper()

    def refresh(self):
        # this if statement resolves only when both players have chosen a word
        if data["host word"] and data["client word"] and not self.ended:
            self.ended = True
            sa = MainScreen(self.master)
            sa.pack()
            sa.refresh()
            self.destroy()
        elif data["win"] == "none" and not self.ended:
            self.entry.button.config(text="waiting on opponent")
        self.after(200, self.refresh)


if __name__ == "__main__":
    # holds all data for the game, a global so it can be accessed by the networking thread easily
    global data
    data = {"client guesses": [],
            "host guesses": [],
            "client word": "",
            "host word": "",
            "connected": False,
            "win": "first"}

    thread = threading.Thread(target=networking)
    thread.daemon = True
    thread.start()
    root = tk.Tk()
    root.resizable(False, False)
    s = WordSelect(root)
    s.pack()
    s.refresh()
    root.mainloop()
