# This is the main file for Avalon AI inputs.

""" General global unchanging variables """
game_state = 3
# Game states:
# 0 : Minions of Mordred win
# 1 : Servants of Arthur win
# 2 : Servants of Arthur won, but Minions of Mordred still choose to assassinate
# 3 : Game in progress
num_players = 0
# the number of players playing
role_types = [0, 0, 0, 0, 0, 0, 0]
# number of each role, in this order per index:
# 0: normal bad (assassin counts as normal bad)
# 1: normal good
# 2: Merlin
# 3: Percival
# 4: Morgana
# 5: Mordred
# 6: Oberon

""" Varying variables that change throughout the game """
current_leader = 0
# the player ID of the current leader.
quest_state = [-1, -1, -1, -1, -1, 0]
# the first five represent fails or successes.
# 0 is fail, 1 is success
# the last entry represents how many rejected quests in a row there are.
people_per_quest = [0, 0, 0, 0, 0]
# the number of people on each quest
propose_history = []
# list of proposals. Each proposal is a list of people in the proposal. Some proposals may not even
# make it to the voting stage; all this means is that VOTE_HISTORY is empty at that index.
vote_history = []
# history of votes. Each entry is a list of votes, 0 or 1, based on the person's (index in the list) vote.
# This should be the same length as propose history.
quest_history = []
# history of quests. Each entry is a list, with these values at each index:
# 0: the position in PROPOSE_HISTORY that this quest was proposed (same as the position in VOTE_HISTORY)
# 1: fail or success? (0 and 1 respectively)
# 2: number of fails
# 3: number of successes

""" Initializes the game. """
def initialize():
    global num_players
    global role_types
    global people_per_quest
    num_players = int(input("Number of players: "))
    # TODO

""" One player accuses another of being evil, or being a specific role. """
def accuse():
    # TODO
    pass

""" The current leader proposes a team. """
def propose_team():
    # TODO
    pass

""" The players vote on the most recently proposed team. If rejected, adds to the rejected tally. """
def vote():
    # TODO
    pass

""" Gets the results of a quest. Passes possesion of the leader to the next person. """
def quest():
    # TODO
    global current_leader
    current_leader = (current_leader + 1) % num_players

def print_help():
    # TODO
    pass



""" Heuristics for Minions of Mordred 

Please write out the strategies that you think are valid for Minions, i.e. what would a minion do?

"""

# Vote through an to-fail quest
def mm_vote_to_fail():
    pass

""" Heuristics for Servants of Arthur 

Please write out the strategies that you think are valid for Servants, i.e. what would a servant do?

"""

# Vote against a to-fail quest
def sa_vote_against_fail():
    pass


initialize()
user_input = ""

while (game_state > 1):
    user_input = input("Command (type help for commands): ")
    if (user_input == "help"):
        print_help()
    if (user_input == "proposeteam" or user_input == "pt"):
        propose_team()
    if (user_input == "accuse" or user_input == "ac"):
        accuse()
    if (user_input == "vote" or user_input == "v"):
        vote()