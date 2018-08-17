# This is the main file for Avalon AI inputs.
import sqlite3
from sqlite3 import OperationalError
from utils import *
from analysis import Analysis

# INSTALL PYTEST IN ORDER TO RUN TESTER FUNCTIONS

class Avalon:
    def __init__(self, value):
        """ Game States:
            # 0 : Minions of Mordred win
            # 1 : Servants of Arthur win
            # 2 : Servants of Arthur won, but Minions of Mordred still choose to assassinate
            # 3 : Game in progress  """
        self.game_state = 3
        """ Number of Players:
            # The number of players playing """
        self.num_players = 0
        """ Role Types:
            Number of each role, in this order per index:
            # 0: normal bad (assassin counts as normal bad)
            # 1: normal good
            # 2: Merlin
            # 3: Percival
            # 4: Morgana
            # 5: Mordred
            # 6: Oberon """
        self.role_types = {'Normal Bad': 0, 'Normal Good': 0, 'Merlin': 0, 'Percival': 0, 'Morgana': 0, 'Mordred': 0, 'Oberon': 0}

        """ Varying variables that change throughout the game """

        """ Current Leader: 
            # The player ID of the current leader. """
        self.current_leader = 0
        """ Quest State: 
            The first five represent fails or successes.
            # 0 is fail, 1 is success
            # the last entry represents how many rejected quests in a row there are. """
        self.quest_state = [-1, -1, -1, -1, -1, 0]
        """ People per Quest: 
            # The number of people on each quest """
        self.people_per_quest = [0, 0, 0, 0, 0]
        self.required_fails_per_quest = [0, 0, 0, 0, 0]
        """ Propose History:
            # List of proposals. Each proposal is a list of people in the proposal. Some proposals may not even
            # Make it to the voting stage; all this means is that VOTE_HISTORY is empty at that index. """
        self.propose_history = []
        """ Voting History: 
            # history of votes. Each entry is a list of votes, 0 or 1, based on the person's (index in the list) vote.
            # This should be the same length as propose history. """
        self.vote_history = []
        """ Quest History:
            # History of quests. Each entry is a list, with these values at each index:
            # 0: the position in PROPOSE_HISTORY that this quest was proposed (same as the position in VOTE_HISTORY)
            # 1: fail or success? (0 and 1 respectively)
            # 2: number of fails
            # 3: number of successes 
            # 4: number of rejects when this quest went through (only important if 4 of them) """
        self.quest_history = []
        """ Known Players:  
            # list of size NUM_PLAYERS, where each index correlates to the player number
            # the values are the role types, as above. """
        self.known_players = []
        """ Feelings :
            # important data for higher level heuristics; who trusts or mistrusts who?
            # we need some way to understand dupes
            # Each player (index in list) gets a list of feelings. The first is a
            # list of (trusted people, time trusted) pairs and the second is a list of 
            # (mistrusted people, time mistrusted).
            # aka: map {player_number > [ [(trusts, time)], [(mistrusts, time)] ]} """
        self.feelings = {}

        if value == 0: #if you want to preset-initialize
            useIn = input("Welcome to Avalon AI! Press enter to continue. ")
            if useIn == "skip":
                self.initialize(5, {'Normal Bad': 2, 'Normal Good': 3, 'Merlin': 0, 'Percival': 0, 'Morgana': 0, 'Mordred': 0, 'Oberon': 0})
            else:
                self.initialize()

    """ Initializes the game. """
    def initialize(self, numplayers = 0, roletypes = {}, currentleader = 0):
        if roletypes == {}:
            self.num_players = sanitised_input("Number of Players: ", int, 5, 10)
            self.role_types['Normal Bad'] = sanitised_input("Normal Bad: ", int)
            self.role_types['Normal Good'] = sanitised_input("Normal Good: ", int)
            self.role_types['Merlin'] = sanitised_input("Merlin: ", int)
            self.role_types['Percival'] = sanitised_input("Percival: ", int)
            self.role_types['Morgana'] = sanitised_input("Morgana: ", int)
            self.role_types['Mordred'] = sanitised_input("Mordred: ", int)
            self.role_types['Oberon'] = sanitised_input("Oberon: ", int)
            self.current_leader = sanitised_input("Starting leader: ", int, max_= self.num_players - 1)
        else:
            self.num_players = numplayers
            self.role_types = roletypes
            self.current_leader = currentleader
        
        self.accusations = [[] for i in range(self.num_players)]
        self.known_players = [-1 for i in range(self.num_players)]
        print("Initializing databases...")
        conn = sqlite3.connect("avalon.db")
        c = conn.cursor()
        executeScriptsFromFile("avalon.sql", c)
        self.check_parameters(c)
        self.load_info(c)
        print("Initialized databases.\n")

        print("Let the game begin!\n")

    """ SQL helper. Checks if initialization is valid. """
    def check_parameters(self, c):
        c.execute("SELECT * FROM player_alignment WHERE num_players = " + str(self.num_players))
        row = c.fetchall()[0]
        num_good = self.role_types['Normal Good'] + self.role_types['Merlin'] + self.role_types['Percival']
        num_bad = self.role_types['Normal Bad'] + self.role_types['Morgana'] + self.role_types['Mordred'] + self.role_types['Oberon']
        if not (row[1] == num_good and row[2] == num_bad):
            print("For", self.num_players, "players, you must have", row[1], "good guys and", row[2], "bad guys.")

    """ SQL helper. Loads into instance variables. """
    def load_info(self, c):
        c.execute("SELECT * FROM people_per_quest WHERE num_players = " + str(self.num_players))
        row = c.fetchall()[0]
        self.people_per_quest = [i for i in row[1:]]
        c.execute("SELECT * FROM required_fails_per_quest WHERE num_players = " + str(self.num_players))
        row = c.fetchall()[0]
        self.required_fails_per_quest = [i for i in row[1:]]

    """ For diagnostics """
    def print_all(self):
        print("Game state:", self.game_state)
        print("Number of players:", self.num_players)
        print("Roles:", self.role_types)
        print("Propose history:", self.propose_history)
        print("Vote history:", self.vote_history)
        print("Quest state:", self.quest_state)
        print("Quest history:", self.quest_history)
        print("Known Players:", self.known_players)

    """ One player accuses another of being evil, or being a specific role. """
    def accuse(self):
        player_accusing = sanitised_input("Who accused? ", int, 0, self.num_players - 1)
        player_accused = sanitised_input("Accusing whom? ", int, 0, self.num_players)
        if (not (player_accusing in self.feelings)):
            self.feelings[player_accusing] = [[], [(self.current_time, player_accused)]]
        else:
            self.feelings[player_accusing][1].append((self.current_time, player_accused))
        
    def trust(self):
        player_trusting = sanitised_input("Who trusts? ", int, 0, self.num_players - 1)
        player_trusted = sanitised_input("Trusts whom? ", int, 0, self.num_players)
        if (not (player_trusting in self.feelings)):
            self.feelings[player_trusting] = [[(self.current_time, player_trusted)], []]
        else:
            self.feelings[player_trusting][0].append((self.current_time, player_trusted))

    """ Returns the index of the last item in proposal array. """
    def current_time(self):
        return len(self.propose_history) - 1

    """ The person using the AI knows the alignment of a player. """
    def known(self):
        self.known_players[input("Which person? ")] = input("Which role? ")

    """ Command-Line Known command"""
    def cl_known(self, player, role_num):
        self.known_players[player] = role_num

    """ The current leader proposes a team. """
    def propose_team(self):
        print("Propose your team!")
        proposed_team, current_quest = [], self.cur_quest()
        max_people, num_people = self.people_per_quest[current_quest], 1
        while num_people <= max_people:
            added_player = sanitised_input("Choose team member " + str(num_people) + " for Quest " + str(current_quest) + ": ", int, max_=self.num_players - 1)
            if added_player in proposed_team:
                print("Player", added_player, "is already chosen to be on the quest.")
            else:
                proposed_team.append(added_player)
                num_people += 1
        self.propose_history.append(proposed_team)
        answer = input("Proceed to vote? Yes (y) or No (n)? ")
        if answer.lower() == "y":
            self.vote()
        else:
            self.vote_history.append([]) #Empty entry
            return

    """ The players vote on the most recently proposed team. If rejected, adds to the rejected tally. """
    def vote(self):
        approved_counts, rejected_counts, vote_list = 0, 0, []
        for i in range(self.num_players):
            choice = sanitised_input("Player " + str(i) + ", approve (1) or reject (0) mission? ", int, 0, 1)
            if choice == 1:
                approved_counts += 1
            else: 
                rejected_counts += 1
            vote_list.append(choice)
        self.vote_history.append(vote_list)
        if approved_counts > rejected_counts:
            self.quest_state[5] = 0 # Reset rejected tally
            self.quest()
        else:
            self.quest_state[5] += 1 # Increment rejected tally
            self.change_current_leader()
            return

    """ We said we didn't want to vote after the proposal... but we did want to """
    def force_vote(self):
        self.quest_state[5] -= 1
        del self.vote_history[-1]
        self.vote()

    """ Gets the results of a quest. Passes possesion of the leader to the next person. """
    def quest(self):
        print("Quest Initiated!")
        previous_rejects = self.quest_state[5]
        votes = []
        cur_quest = self.cur_quest()
        for i in range(self.people_per_quest[self.cur_quest()]):
            votes.append(sanitised_input("Result " + str(i) + " is success (1) or fail (0): ", int, 0, 1))
        fail = 0
        success = 0
        for vote in votes:
            if vote == 0:
                fail += 1
            else:
                success += 1
        quest_result = int(fail < self.required_fails_per_quest[cur_quest])
        self.go_quest(len(self.propose_history) - 1, quest_result, fail, success, previous_rejects)
        self.quest_state[cur_quest] = quest_result
        self.quest_state[5] = 0
        self.change_current_leader()
        print("Quest result: " + ("good" if quest_result else "bad"))
        if self.quest_state[:-1].count(0) >= 3:
            self.game_state = 0 # Bad guys win
        if self.quest_state[:-1].count(1) >= 3:
            self.game_state = 2 # Bad guys have a chance to guess merlin

    def guess_merlin(self):
        guess = sanitised_input("Who do you think is Merlin? ", int, 0, self.num_players - 1)
        if (self.known_players[guess] == 2 or sanitised_input("Who is actually Merlin? ", int, 0, self.num_players - 1) == guess):
            self.game_state = 0
        else:
            self.game_state = 1

    def cur_quest(self):
        return len(self.quest_history)

    def go_quest(self, propose_index, result, fails, successes, previous_rejects):
        self.quest_history.append([propose_index, result, fails, successes, previous_rejects])

    def change_current_leader(self):
        self.current_leader = (self.current_leader + 1) % self.num_players

def print_help():
    print("printall or pa;", "proposeteam or pt;", "accuse or ac;", "forcevote or fv;", "break")

# comment copied from stackoverflow @Tamás
""" Some explanation here: __name__ is a special Python variable that holds the name
 of the module currently being executed, except when the module is started from the 
 command line, in which case it becomes "__main__". """
# I'm doing this so we can run tests in test.py, without triggering
#   the creation of an Avalon object unnecessarily

if __name__ == '__main__':
    a = Avalon(0)
    while (a.game_state > 1):
        user_input = input("Command (type help for commands): ")
        if (user_input == "help"):
            print_help()
        elif (user_input == "printall" or user_input == "pa"):
            a.print_all()
        elif (user_input == "break" or user_input == "quit"):
            break
        elif (user_input == "guessmerlin" or "gm"):
            a.guess_merlin()
        elif a.game_state != 2: # If not! bad guys guess Merlin
            if (user_input == "proposeteam" or user_input == "pt"):
                if not (a.quest_state[4] > -1):
                    a.propose_team()
                else:
                    print("Five quests have already been completed!")
            elif (user_input == "accuse" or user_input == "ac"):
                a.accuse()
            elif (user_input == "trust" or user_input == "tr"):
                a.trust()
            elif (user_input == "forcevote" or user_input == "fv"):
                print("I hope you know what you're doing! Voting the previous proposal...")
                a.force_vote()
            elif (user_input == "analyze" or user_input == "ana"):
                ana = Analysis(a)
                ana.start_analysis()
                ana.analyze()
                print(ana.player_values)
    if a.game_state == 0:
        print("Minions have won!")
    else:
        print("Servants have won!")