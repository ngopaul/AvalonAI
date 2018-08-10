# Main file for analyzing an Avalon Object.

""" DROPS the analysis table if it exists. Creates a new table with all possible combinations."""
def start_analysis(a):
    pass

""" Runs heurisitics on the Avalon object. """
def analyze(a):
    pass

""" Heuristics for Minions of Mordred 

Please write out the strategies that you think are valid for Minions, i.e. what would a minion do?

"""

# Vote through a to-fail quest, or against a to-win quest
# This is weighted more heavily when the quest turns the tide (i.e. GOOD/bad is about to win)
def mm_vote(a, player, quest_num):
    pass

""" Heuristics for Servants of Arthur 

Please write out the strategies that you think are valid for Servants, i.e. what would a servant do?

"""

# Vote against a to-fail quest, or for a to-win quest
# This is weighted more heavily when the quest turns the tide (i.e. good/BAD is about to win)
def sa_vote(a, player, quest_num):
    pass

# Merlin is the first to vote against a bad person on a quest
def sa_merlin_predicts(a, player, other):
    pass

# Merlin starts trusting someone who is good,
# when previously they were pretending to not trust the person
def sa_merlin_change_of_heart(a, player, other):
    pass