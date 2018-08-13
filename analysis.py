# Main file for analyzing an Avalon Object.
import sqlite3
from utils import *

class Analysis:
    def __init__(self, avalonObject):
        self.conn = sqlite3.connect("avalon.db")
        self.c = self.conn.cursor()
        self.a = avalonObject
        self.player_values = []

    """ DROPS the analysis table if it exists. Creates a new table with all possible combinations."""
    def start_analysis(self, output = False):
        executeScriptsFromFile("avalon.sql", self.c, "don't print")
        self.c.execute("DROP TABLE IF EXISTS analysis")
        self.c.execute("DROP TABLE IF EXISTS possibilities")
        # creates sql table of all possibilities
        self.c.execute(create_possibilities(self.a))
        if output == True:
            self.c.execute("SELECT * FROM possibilities")
            row = self.c.fetchall()
            print(row)

    """ Runs heurisitics on the Avalon object. """
    def analyze(self):
        # currently, all it will be is a pass through all of the players 
        # and gauging how good/evil they are based on votes and quest results
        # The heuristic is simple: + if they are good, - if they are bad.
        self.player_values = []
        for player in range(self.a.num_players):
            self.player_values.append(self.vote(player))

    """ General Heuristics """

    # Check how a player has voted. The farther the vote is in the game, or closer it is 
    # to a victory for one side, the more it matters.
    def vote(self, player):
        passed_votes = passed_votes_history(self.a)
        quest_history = [quest[1] * 2 - 1 for quest in self.a.quest_history] # +1 for success, -1 for fail
        player_vote_history = [votes[player] * 2 - 1 for votes in passed_votes] # +1 for yes, -1 for no
        quest_importance = []
        g, b = 0, 0 # counting good and bad
        for quest in quest_history:
            if quest == -1:
                b += 1
            else:
                g += 1
            quest_importance.append(
                g+b +
                (1 if g > 1 else 0) +
                (1 if b > 1 else 0)
            )
        player_value = 0
        for i in range(len(quest_history)):
            player_value += quest_history[i] * player_vote_history[i] * quest_importance[i]
        return player_value


    """ Heuristics for Minions of Mordred 

    Please write out the strategies that you think are valid for Minions, i.e. what would a minion do?

    """

    # Vote through a to-fail quest, or against a to-win quest
    # This is weighted more heavily when the quest turns the tide (i.e. GOOD/bad is about to win)
    def mm_vote(self, player, quest_num):
        pass

    """ Heuristics for Servants of Arthur 

    Please write out the strategies that you think are valid for Servants, i.e. what would a servant do?

    """

    # Vote against a to-fail quest, or for a to-win quest
    # This is weighted more heavily when the quest turns the tide (i.e. good/BAD is about to win)
    def sa_vote(self, player, quest_num):
        pass

    # Merlin is the first to vote against a bad person on a quest
    def sa_merlin_predicts(self, player, other):
        pass

    # Merlin starts trusting someone who is good,
    # when previously they were pretending to not trust the person
    def sa_merlin_change_of_heart(self, player, other):
        pass