# AVALON AI

TODO:

(DONE) disallow putting in duplicates of a person on a quest
- check for the win condition of the game (three successful, three failed)
    - probably in the while loop
- add a way to check when good win, to input a Merlin guess for evils
- add the command "ACCUSE"
- add the command "KNOWN"
- add heuristics for Minions of Mordred
- add heuristics for Servants of Arthur

- WRITE A TON OF TESTS

- after making the basic voting heurisitics, we need to test out the AI on a real game!
    - we'll be able to find bugs and see how well our most basic heuristic works

Basis of the AI:

The information that we have is very sparse. We try to apply heuristics to our possible teams to evaluate how likely each combination is. In order to get to an effective answer, we must filter step-by-step; otherwise we will have to analyze all 10!/4! possible combinations to see if each is viable. While this is doable (specifically, we would use SQL to handle the data), it is not efficient.

We will have several main stages (not in any particular order right now) to narrow our search to a manageable dataset (it is extremely nice to work with SQL here because of how it can manage filters):

- Analyze the data with no special roles, just Minions and Servants.
- Analyze pairs of players. Oftentimes (will have to do more research) players on the same team who know who each other are, will vote similarly (but not necessarily ACT similarly). These pairs can be both good and both bad pairs, but are more often bad because they know who each other are.
- Use KNOWN_PLAYERS. Factor the player type of one of the players into account, reducing computation by a factor.

