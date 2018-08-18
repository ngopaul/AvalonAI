# Main file for analyzing an Avalon Object.
import sqlite3
from utils import *

class Analysis:
    def __init__(self, avalonObject):
        self.conn = sqlite3.connect("avalon.db")
        self.c = self.conn.cursor()
        self.a = avalonObject
        self.player_values = []
        self.minion_set = set([0, 4, 5, 6])
        self.servant_set = set([1, 2, 3])

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
        order_string = ""
        i = 1
        for player in range(self.a.num_players):
            self.player_values.append(self.vote(player))
            order_string += " a" + str(i) + ","
        order_string = order_string[:-1] + ";"
        self.c.execute("select * from possibilities order by 1")
        rows = self.c.fetchall()
        for row in rows:
            role_set = row[0:5]
            score = self.apply_heuristics(role_set)
            where_string = ""
            for i in range(len(role_set)):
                where_string += " a" + str(i+1) + " = " + str(role_set[i]) + " and "
            where_string = where_string[:-4]
            self.c.execute("update possibilities set score = " + str(score) + " where " + where_string + ";")
        self.c.execute("select * from possibilities order by score")
        rows = self.c.fetchall()
        for row in rows:
            print(row)

    def apply_heuristics(self, role_set, weights=[1]):
        return self.mm_coordinate(role_set)

    def importance_factor(self):
        quest_history = [quest[1] * 2 - 1 for quest in self.a.quest_history] # +1 for success, -1 for fail
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
        return quest_importance


    """ General Heuristics """

    # Check how a player has voted. The farther the vote is in the game, or closer it is 
    # to a victory for one side, the more it matters.
    def vote(self, player):
        passed_votes = passed_votes_history(self.a)
        quest_history = [quest[1] * 2 - 1 for quest in self.a.quest_history] # +1 for success, -1 for fail
        player_vote_history = [votes[player] * 2 - 1 for votes in passed_votes] # +1 for yes, -1 for no
        quest_importance = self.importance_factor()
        player_value = 0
        for i in range(len(quest_history)):
            player_value += quest_history[i] * player_vote_history[i] * quest_importance[i]
        return player_value


    """ Heuristics for Minions of Mordred 

    Please write out the strategies that you think are valid for Minions, i.e. what would a minion do?

    """

    # Minions seem to coordinate. 
    # Take the largest similar vote between all minions divided by total number of minions, 
    # multiplied by the importance factor of the quest vote. 
    # For example, on quest 1 (importance = 1), 2 minions vote yes and 1 minion votes no. 
    # This is a factor of 2/3 * 1, which is added to the score that is returned.
    def mm_coordinate(self, role_set):
        simplified_minions = [1 if (i in self.minion_set) else 0 for i in role_set] # [0, 0, 1, 1, 0]
        minion_nums = []
        quest_importance = self.importance_factor()
        for i in range(len(simplified_minions)):
            if simplified_minions[i] == 1:
                minion_nums.append(i)
        num_minions = self.a.num_bad
        passed_votes = passed_votes_history(self.a)
        value = 0
        for i in range(len(passed_votes)):
            amount = 0
            for num in minion_nums:
                amount += passed_votes[i][num]
            amount /= num_minions
            value += quest_importance[i] * max(amount, 1-amount)
        return value
            

    """ Heuristics for Servants of Arthur 

    Please write out the strategies that you think are valid for Servants, i.e. what would a servant do?

    """

    # Merlin is the first to vote against a bad person on a quest
    def sa_merlin_predicts(self, role_set):
        pass

    # Merlin starts trusting someone who is good,
    # when previously they were pretending to not trust the person
    def sa_merlin_change_of_heart(self, role_set):
        pass