# LAN-hangman
A 2-player symmetric hangman game. One player hosts (needs host.py), the other connects to them (needs client.py). This serves no gamemplay difference.
The player with client.py needs addr.txt, and in it should have the address of the player with host.py.
host.py must already be running when client.py is started

__How the game works__

Both players choose a word. The game then progresses in turns, each turn consisting of a single guess by both players. Once both players have made a guess, players are notified of each others guesses, and the next turn begins. The game is thus symmetric.

A guess is either a single letter, or a word. If a single letter is guessed then all positions that letter occurs in the opponents word are immediately displayed. If a full, incorrect word is guessed, then the player loses a life and no information is displayed.

A player loses once they have made 11 incorrect guesses. If both players reach 11 incorrect guesses on the same turn, it is a draw (both lose).

A player wins once they have guessed the opponent's word (either by a correct full word guess or by getting all letters). If both players get the opponent's word on the same turn, it is a draw (both win).
