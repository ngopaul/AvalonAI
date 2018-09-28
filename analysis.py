# Main file for analyzing an Avalon Object.
import sqlite3
from utils import *
import sys

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
    def analyze(self, limit = sys.maxsize, include_player_vals = False):
        # This first part is a pass through of the first heuristic, 
        # which is voting good or bad for good or bad quests.
        self.player_values = []
        order_string = ""
        i = 1
        for player in range(self.a.num_players):
            self.player_values.append(self.vote(player))
            order_string += " a" + str(i) + ","
        # Filter impossibles
        order_string = order_string[:-1] + ";"
        self.c.execute("select * from possibilities")
        rows = self.c.fetchall()
        for row in rows:
            role_set = row[0:len(row)-1]
            score = self.filter_impossibles(role_set)
            where_string = ""
            for i in range(len(role_set)):
                where_string += " a" + str(i+1) + " = " + str(role_set[i]) + " and "
            where_string = where_string[:-4]
            if score == -99:
                self.c.execute("DELETE FROM possibilities" + " where " + where_string + ";")
        # This second part we can hone with machine learning or 
        # just by hand. The idea is to apply heurisitics to every possible 
        # set of roles, and based on scoring each of the possible sets, one 
        # should eventually stand out as the correct role set.
        order_string = order_string[:-1] + ";"
        self.c.execute("select * from possibilities")
        rows = self.c.fetchall()
        for row in rows:
            role_set = row[0:len(row)-1]
            # This is where the magic happens for each row. Score is calulated here.
            score = self.apply_heuristics(role_set)
            # updating the score for the column
            where_string = ""
            for i in range(len(role_set)):
                where_string += " a" + str(i+1) + " = " + str(role_set[i]) + " and "
            where_string = where_string[:-4]
            self.c.execute("update possibilities set score = " + str(score) + " where " + where_string + ";")
        # Printing the scores just for testing purposes
        self.c.execute("select * from possibilities order by score")
        rows = self.c.fetchall()
        iterator = reversed(rows)
        for i in range(min(limit, len(rows))):
            print(row_to_roles(next(iterator)))

    """ Applies any heuristics for a role_set guess. This is the front end for managing all our
    weights for all of our heurisitics. """
    def apply_heuristics(self, role_set, weights=[1, 1, 1, 1, 1, 1]):
        heurisitics_set = [self.mm_coordinate, self.sa_merlin_trusts_good_mistrusts_bad, 
        self.sa_merlin_quests_good, self.general_vote]
        score = 0.0
        for i in range(len(heurisitics_set)):
            score += weights[i] * heurisitics_set[i](role_set)
        return score

    """ Returns a list of importance weights based on how 
    important a quest is to the game's state."""
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

    """ Returns two lists of the player's current feelings about other players in the game. 
    Returns two blank lists if no feeligs. 
    i.e. return [2,/ 4], [0, 1] 
    In order of trust and mistrust. """
    def current_feelings(self, player_num):
        trusts, mistrusts = [], []
        if not player_num in self.a.feelings:
            return [], []
        else:
            trust_dict = self.a.feelings[player_num][0]
            mistrust_dict = self.a.feelings[player_num][1]
            for i in range(self.a.num_players):
                if i in trust_dict and i in mistrust_dict and max(trust_dict[i]) > max(mistrust_dict[i]):
                    trusts.append(i)
                elif i in trust_dict and i in mistrust_dict and max(trust_dict[i]) <= max(mistrust_dict[i]):
                    mistrusts.append(i)
                elif i in trust_dict:
                    trusts.append(i)
                elif i in mistrust_dict:
                    mistrusts.append(i)
        return trusts, mistrusts

    """ Returns all of the quests a certain player has proposed. 
    Returns a list of proposals. """
    def players_proposed(self, player_num):
        toReturn = []
        current_player = self.a.starting_leader
        for proposal in self.a.propose_history:
            if current_player == player_num:
                toReturn.append(proposal)
            current_player = (current_player + 1) % self.a.num_players
        return toReturn

    """ General Heuristics """

    # Check how a player has voted. The farther the vote is in the game, or closer it is 
    # to a victory for one side, the more it matters.
    # DO NOT USE FOR HEURISTIC
    def vote(self, player):
        passed_votes = passed_votes_history(self.a)
        quest_history = [quest[1] * 2 - 1 for quest in self.a.quest_history] # +1 for success, -1 for fail
        player_vote_history = [votes[player] * 2 - 1 for votes in passed_votes] # +1 for yes, -1 for no
        quest_importance = self.importance_factor()
        player_value = 0
        for i in range(len(quest_history)):
            player_value += quest_history[i] * player_vote_history[i] * quest_importance[i]
        return player_value

    # use self.player vals to score.
    # currently this score will be a work in progress.
    # +1 point for each 'good' which is in the top #ofGood 'good'.
    # +(#good which Merlin is greater than)/(total number of good - 1)
    # +(#good which Percival is greater than - #ofMerlin)/(total number of good - 1 - #pfMerlin)
    # +1 point for each 'bad' which is in the top #ofBad 'bad'.

    # handles each player type and assigns scores to how they vote on quests of people.
    def general_vote(self, role_set):
        points = 0
        scores = [0 for i in range(len(role_set))]
        importance = self.importance_factor()
        # list of 1's and -1's which represent there being all good, or not all good people on the team.
        propose_goodness = []
        # list of importance numbers based on the quest that is currently being proposed
        propose_importance = [importance[max(self.a.quest_of_time(i) - 1, 0)] for i in range(len(self.a.propose_history))]
        # filling up propose_goodness
        for proposal in self.a.propose_history:
            state = 1
            proposal_roles = [role_set[person] for person in proposal]
            for bad_role in self.minion_set:
                if bad_role in proposal_roles:
                    state = -1
            propose_goodness.append(state)
        # print("PROPOSE GOODNESS:",propose_goodness)
        # print("PROPOSE IMPORTANCE:",propose_importance)
        # iterating through people to look at their votes. We can then score them and put into scores.
        for i in range(len(role_set)): # i is the person number
            # votes turn into +1 or -1, or 0 if there was no vote
            votes = [vote[i] * 2 - 1 if len(vote) > 0 else 0 for vote in self.a.vote_history]
            scores[i] = sum([votes[i]*propose_goodness[i]*propose_importance[i] for i in range(len(votes))])

        scores = [1/2 * scores[i] + self.player_values[i] for i in range(len(scores))]

        # Tailored ideas to differentiate and add points properly
        # Merlin/Percival is the most good
        if 2 in role_set:
            if scores[role_set.index(2)] == max(scores):
                points += 1
        if 3 in role_set:
            if scores[role_set.index(3)] == max(scores):
                points += 1
        # The most bad is a bad person
        if role_set[scores.index(min(scores))] in self.minion_set:
            points += 1

        # the final scoring
        final_scores = []
        for i in range(len(scores)):
            if role_set[i] in self.minion_set:
                final_scores.append(scores[i] * -1)
            else:
                final_scores.append(scores[i])
        points += sigmoid(sum(final_scores))
        # print("FINAL SCORES:", final_scores)
        # print("Points", points)
        return round(points, 2)

    # heuristics to handle obvious cases
    def filter_impossibles(self, role_set):
        role_impossible = False
        quests_failed_index = []
        for quest in self.a.quest_history:
            if quest[1] == 0:
                quests_failed_index.append((quest[0], quest[2]))
        
        for failed_quest_index, num_fails in quests_failed_index:
            # guy put on a team is good--- 1. is bad--- 0
            good_or_bad = []
            for person_index in self.a.propose_history[failed_quest_index]:
                if role_set[person_index] in self.minion_set:
                    good_or_bad.append(0)
                else:
                    good_or_bad.append(1)
            if good_or_bad.count(0) < num_fails:
                role_impossible = True

        if role_impossible:
            return -99
        return 0

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

    # when other people think a minion is bad, then another minion joins in and 
    # agrees with the group.        
    def mm_throw_under_the_bus(self, role_set):
        pass

    """ Heuristics for Servants of Arthur 

    Please write out the strategies that you think are valid for Servants, i.e. what would a servant do?

    """

    # The Merlin trusts good people and mistrusts bad people.
    # Give a point max for trusting good people, Give a point max for mistrusting bad
    def sa_merlin_trusts_good_mistrusts_bad(self, role_set):
        if not 2 in role_set:
            return 0
        trusts, mistrusts = self.current_feelings(role_set.index(2))
        total = len(trusts) + len(mistrusts)
        points = 0
        for person_num in trusts:
            if role_set[person_num] in self.servant_set:
                points += 1
        for person_num in mistrusts:
            if role_set[person_num] in self.minion_set:
                points += 1
        return 0 if total == 0 else round(2 * points/total, 2)

    # Merlin puts good people on a quest. Also allows Merlin to put one 
    # bad person on a quest... This is for advanced players
    def sa_merlin_quests_good(self, role_set):
        if not 2 in role_set:
            return 0
        merlins_proposed = self.players_proposed(role_set.index(2))
        total = sum([len(proposal) for proposal in merlins_proposed])
        score = 0
        for proposal in merlins_proposed:
            bad_count = 0
            for person in proposal:
                if role_set[person] in self.servant_set:
                    score += 1
                if bad_count == 0 and role_set[person] in self.minion_set:
                    score += 1
                    bad_count += 1
        return 0 if total == 0 else round(score/total, 2)

    # Merlin starts trusting someone who is good,
    # when previously they were pretending to not trust the person
    def sa_merlin_change_of_heart(self, role_set):
        if not 2 in role_set:
            return 0
        heuristics = []
        merlin = -1000
        servants = []
        # Find index of merlin
        # Find index of Loyal Servants
        # Using merlin in self.feelings, access his trusted and mistrust dictionaries and compare the most recent between those two values
        for r in range(len(role_set)):
            if role_set[r] == 1:
                servants.append(r)
            if role_set[r] == 2:
                merlin = r
        if merlin in self.a.feelings: # Check if Merlin has feelings!
            merlin_feelings = self.a.feelings[merlin]
            for servant in servants:
                trust_weight, mistrust_weight = 0, 0
                if servant in merlin_feelings[0]:
                    trust_weight = merlin_feelings[0][servant][-1]
                if servant in merlin_feelings[1]:
                    mistrust_weight = merlin_feelings[1][servant][-1]
                heuristics.append(trust_weight > mistrust_weight)
            return sum(heuristics)
        else: # If Merlin has no feelings
            return 0
