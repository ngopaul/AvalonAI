# AVALON AI

ABOUT:
- Avalon AI simulates a game of The Resistance: Avalon. The goal of Avalon AI is to predict the roles of players as they play the game in real life, as an aid. It uses filtering and heuristics in order to sort combinations of possible roles.

FILE STRUCTURE:
- main.py holds the Avalon object and the main loop to play the game
- analysis.py holds the heuristics and analyzes who is who in the game
- test.py uses pyautogui to test the game
- utils.py holds utility functions
- resources/ contains images used in the GUI version of the game

TODO:

- see the Avalon AI project in github, in the projects tab.
- currently, adding heuristics and testing the game in real life.

Basis of the AI:

We try to apply heuristics to our possible teams to evaluate how likely each combination is. In order to get to an effective answer, we must filter step-by-step; otherwise we will have to analyze all 10!/4! possible combinations to see if each is viable. While this is doable it is not efficient. We use SQL to handle the data

We will have several main stages to narrow our search to a manageable dataset:

- Analyze impossibles: Quests with fails cannot possible have all good roles.
- Analyze the data with no special roles, just Minions and Servants. This scores players positively for good actions, and negatively for bad ones. A 0 score for a player means the AI thinks he/she are neither good nor evil.
- Analyze each possible combination of players, and rank which is the most likely by their score; score using the heuristics that we create (including the first analysis above). A command in the main game should output the top highest likely possibilities.

GUI:

- The GUI uses pygame to simulate the game and provides visual feedback, offering buttons that can be clicked to play the game
- The GUI uses pygame's built-in event queue to handle events throughout the game, and relies on an action-submit structure of events:
    - An action is done (i.e. clicked on the accuse button). This is stored in the current_event variable.
    - Some modifications are made (such as choosing who accused who), and the submit button is clicked. The current_event becomes 'submit', and the previous_event variable becomes the original action/event (i.e. 'accuse')
        - There is also a cancel button.
    - Now, the game can parse the submission of the event using all of the variables, and then clear after handling this game action.

