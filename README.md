# AVALON AI

FILE STRUCTURE:
- main.py holds the Avalon object and the main loop to play the game
- analysis.py holds the heuristics and analyzes who is who in the game
- test.py uses pyautogui to test the game

TODO:

- see the Avalon AI project in github, in the projects tab.

Basis of the AI:

The information that we have is very sparse. We try to apply heuristics to our possible teams to evaluate how likely each combination is. In order to get to an effective answer, we must filter step-by-step; otherwise we will have to analyze all 10!/4! possible combinations to see if each is viable. While this is doable (specifically, we would use SQL to handle the data), it is not efficient.

We will have several main stages (not in any particular order right now) to narrow our search to a manageable dataset (it is extremely nice to work with SQL here because of how it can manage filters):

- Analyze the data with no special roles, just Minions and Servants.
- Analyze pairs of players. Oftentimes (will have to do more research) players on the same team who know who each other are, will vote similarly (but not necessarily ACT similarly). These pairs can be both good and both bad pairs, but are more often bad because they know who each other are.
- Use KNOWN_PLAYERS. Factor the player type of one of the players into account, reducing computation by a factor.

