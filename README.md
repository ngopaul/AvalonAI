# AVALON AI

FILE STRUCTURE:
- main.py holds the Avalon object and the main loop to play the game
- analysis.py holds the heuristics and analyzes who is who in the game
- test.py uses pyautogui to test the game
- utils.py holds utility functions

TODO:

- see the Avalon AI project in github, in the projects tab.

Basis of the AI:

The information that we have is very sparse. We try to apply heuristics to our possible teams to evaluate how likely each combination is. In order to get to an effective answer, we must filter step-by-step; otherwise we will have to analyze all 10!/4! possible combinations to see if each is viable. While this is doable (specifically, we would use SQL to handle the data), it is not efficient.

We will have several main stages (not in any particular order right now) to narrow our search to a manageable dataset (it is extremely nice to work with SQL here because of how it can manage filters):

- Analyze the data with no special roles, just Minions and Servants. This scores players positively for good actions, and negatively for bad ones. A 0 score for a player means the AI thinks he/she are neither good nor evil.
    - COMPLETED
- Analyze each possible combination of players, and rank which is the most likely by their score; score using the heuristics that we create (including the first analysis above). A command in the main game should output the top highest likely possibilities.
    - Working on heuristics

