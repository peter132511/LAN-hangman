import tkinter as tk
from functools import partial


# takes a dictionary containing guesses that the client and host have made, along with their words,
# and returns the win state as a string
def check_win(data):
    client, host = False, False
    clientLoss, hostLoss = False, False
    if (len([x for x in data["client guesses"] if x in set(data["host word"]) and len(x) == 1])
        == len(set(data["host word"]))) or (len([x for x in data["client guesses"] if x == data["host word"]])
                                            > 0):
        client = True
    if (len([x for x in data["host guesses"] if x in set(data["client word"]) and len(x) == 1])
        == len(set(data["client word"]))) or (len([x for x in data["host guesses"] if x == data["client word"]])
                                              > 0):
        host = True
    if len([x for x in data["host guesses"] if x not in data["client word"]]) >= 11:
        hostLoss = True
    if len([x for x in data["client guesses"] if x not in data["host word"]]) >= 11:
        clientLoss = True

    if client and host:
        return "draw"  # both guess word simultaneously and win
    elif clientLoss and hostLoss:
        return "lose"  # both players reach the last hangman stage simultaneously and lose
    elif client or hostLoss:
        return "client"
    elif host or clientLoss:
        return "host"
    else:
        return "none"  # no one has one or lost


# a tkinter canvas that displays levels of completion of a hangman graphic
class HangmanDisplay(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master, width=150, height=200, bg="white")

    # draws the hangman graphic at the appropriate level of completion
    def refresh(self, stage):
        if stage >= 1:
            self.create_line(20, 180, 90, 180, width=4)
        if stage >= 2:
            self.create_line(55, 40, 55, 180, width=4)
        if stage >= 3:
            self.create_line(53, 40, 107, 40, width=4)
        if stage >= 4:
            self.create_line(55, 60, 75, 40, width=4)
        if stage >= 5:
            self.create_line(105, 40, 105, 55, width=4)
        if stage >= 6:
            self.create_oval(90, 55, 120, 85, width=4)
        if stage >= 7:
            self.create_line(105, 85, 105, 125, width=4)
        if stage >= 8:
            self.create_line(105, 85, 85, 115, width=4)
        if stage >= 9:
            self.create_line(105, 85, 125, 115, width=4)
        if stage >= 10:
            self.create_line(105, 122, 85, 155, width=4)
        if stage >= 11:
            self.create_line(105, 122, 125, 155, width=4)


class WordSelectionScreen(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, bg="#e8cb75", *args, **kwargs)


# a text entry and button that passes the text, and the object, to the function
class WordGuesser(tk.Frame):
    def __init__(self, master, function, text="Guess The Word", *args, **kwargs):
        tk.Frame.__init__(self, master, bg="#e8cb75", *args, **kwargs)
        self.entry = tk.Entry(self, width=20, font=("Arial", 20))
        self.button = tk.Button(self, font=("Arial", 20), text=text,
                                command=lambda: function(self.entry.get(), self), bg="#fcad03", fg="#ffffff")
        self.entry.grid(column=1, row=0, pady=(5, 10), padx=(0, 10))
        self.button.grid(column=2, row=0, pady=(5, 10), padx=(10, 0))
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)


# a set of QWERTY buttons that call a given function with their letter as
# the argument when pressed
class KeyboardSelection(tk.Frame):
    def __init__(self, master, function, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        alphabet = (("Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"),
                    ("A", "S", "D", "F", "G", "H", "J", "K", "L"),
                    ("Z", "X", "C", "V", "B", "N", "M"))

        self.buttons = {}

        rowNum = 0
        for row in alphabet:
            col = rowNum + 1
            for letter in row:
                # partial is required since letter is redefined multiple times, but a lambda is only evaluated at
                # runtime so would only return its latest value for all letters
                self.buttons[letter] = tk.Button(self, width=3, bg="#fcad03", fg="#ffffff", height=1, text=letter,
                                                 command=partial(function, letter, self), font=("Arial", 20))
                self.buttons[letter].grid(row=rowNum, column=col, padx=4, pady=4)
                col += 1
            rowNum += 1

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(11, weight=1)

    def disable(self, letter):
        self.buttons[letter].config(state="disabled", fg="#101010", bg="#505050")
