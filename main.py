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
        self.num_bad = 0
        self.num_good = 0
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
            # aka: map {player_number > [ [(trusts, time)], [(mistrusts, time)] ]}
            # alternative, faster approach: {player_number -> [
            #                                                  {trusted_player -> [times,]}, 
            #                                                  {untrusted_player -> [times,]}
            #                                                 ]
            #                               }
            #  """
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

    """ Throws an improper args error """
    def args_error(self):
        print("Improper arguments!")
        assert 1 == 0

    """ SQL helper. Checks if initialization is valid. """
    def check_parameters(self, c):
        c.execute("SELECT * FROM player_alignment WHERE num_players = " + str(self.num_players))
        row = c.fetchall()[0]
        self.num_good = self.role_types['Normal Good'] + self.role_types['Merlin'] + self.role_types['Percival']
        self.num_bad = self.role_types['Normal Bad'] + self.role_types['Morgana'] + self.role_types['Mordred'] + self.role_types['Oberon']
        if not (row[1] == self.num_good and row[2] == self.num_bad):
            print("For", self.num_players, "players, you must have", row[1], "good guys and", row[2], "bad guys.")

    """ SQL helper. Loads from tables into instance variables. """
    def load_info(self, c):
        c.execute("SELECT * FROM people_per_quest WHERE num_players = " + str(self.num_players))
        row = c.fetchall()[0]
        self.people_per_quest = [i for i in row[1:]]
        c.execute("SELECT * FROM required_fails_per_quest WHERE num_players = " + str(self.num_players))
        row = c.fetchall()[0]
        self.required_fails_per_quest = [i for i in row[1:]]

    """ For diagnostics and people playing the game """
    def print_all(self):
        print("Game state:", self.game_state)
        print("Number of players:", self.num_players)
        print("Roles:", self.role_types)
        print("Propose history:", self.propose_history)
        print("Vote history:", self.vote_history)
        print("Quest state:", self.quest_state)
        print("Quest history:", self.quest_history)
        print("Known Players:", self.known_players)
        print("Feelings:", self.feelings)

    """ One player accuses another of being evil, or being a specific role. """
    def accuse(self, player_accusing, player_accused):
        if not (check_person(self, player_accused) and check_person(self, player_accusing) and player_accusing != player_accused):
            self.args_error()
            return
        if (not (player_accusing in self.feelings)):
            self.feelings[player_accusing] = [{}, {player_accused : [self.current_time]}]
        else:
            self.feelings[player_accusing][1][player_accused].append(self.current_time)
        
    def trust(self, player_trusting, player_trusted):
        if not (check_person(self, player_trusting) and check_person(self, player_trusted) and player_trusting != player_trusted):
            self.args_error()
            return
        if (not (player_trusting in self.feelings)):
            self.feelings[player_trusting] = [{player_trusted : [self.current_time]}, {}]
        else:
            self.feelings[player_trusting][0][player_trusted].append(self.current_time)

    """ Returns the index of the last item in proposal array. """
    def current_time(self):
        return len(self.propose_history) - 1

    """ The person using the AI knows the alignment of a player. """
    def known(self, role, person):
        if not (check_person(self, person) and check_role(role)):
            self.args_error()
            return
        self.known_players[person] = role

    """ Command-Line Known command"""
    def cl_known(self, player, role_num):
        if not (check_person(self, player) and check_role(role_num)):
            self.args_error()
            return
        self.known_players[player] = role_num

    """ The current leader proposes a team. """
    def propose_team(self, proposed_team, current_quest, max_people, proceed):
        if (current_quest != self.cur_quest() or max_people != self.people_per_quest[self.cur_quest()] or not proceed.lower() in ['y', 'n']):
            self.args_error()
            return
        if (not check_list(proposed_team, 0, self.num_players-1, self.people_per_quest[self.cur_quest()], False)):
            self.args_error()
            return
        self.propose_history.append(proposed_team)
        if proceed.lower() == "y":
            approved_counts, rejected_counts, vote_list = 0, 0, []
            for i in range(self.num_players):
                choice = sanitised_input("Player " + str(i) + ", approve (1) or reject (0) mission? ", int, 0, 1)
                if choice == 1:
                    approved_counts += 1
                else: 
                    rejected_counts += 1
                vote_list.append(choice)
            self.vote(approved_counts, rejected_counts, vote_list)
        else:
            self.vote_history.append([]) #Empty entry
            return

    """ The players vote on the most recently proposed team. If rejected, adds to the rejected tally. """
    def vote(self, approved_counts, rejected_counts, vote_list):
        if (not check_list(vote_list, 0, 1, self.num_players) or approved_counts != vote_list.count(1)
        or rejected_counts != vote_list.count(0) or approved_counts + rejected_counts != self.num_players):
            self.args_error()
            return
        self.vote_history.append(vote_list)
        if approved_counts > rejected_counts:
            previous_rejects = self.quest_state[5]
            print("Quest Initiated!")
            votes = []
            cur_quest = self.cur_quest()
            for i in range(self.people_per_quest[self.cur_quest()]):
                votes.append(sanitised_input("Result " + str(i) + " is success (1) or fail (0): ", int, 0, 1))
            self.quest(previous_rejects, votes, cur_quest)
        else:
            self.quest_state[5] += 1 # Increment rejected tally
            self.change_current_leader()
            return

    """ We said we didn't want to vote after the proposal... but we did want to """
    def force_vote(self, approved_counts, rejected_counts, vote_list):
        del self.vote_history[-1]
        self.vote(approved_counts, rejected_counts, vote_list)

    """ Gets the results of a quest. Passes possesion of the leader to the next person. """
    def quest(self, previous_rejects, votes, cur_quest):
        if (previous_rejects != self.quest_state[5] or cur_quest != self.cur_quest() or not check_list(votes, 0, 1, self.people_per_quest[cur_quest])):
            self.args_error()
            return
        self.quest_state[5] = 0 # Reset rejected tally
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

    def guess_merlin(self, guess, actual):
        if (not check_person(self, guess) or not check_person(self, actual)):
            self.args_error()
            return
        if (guess == actual):
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
    print("\tprintall or pa; break")
    print("\tanalyze; anamore")
    print("\tproposeteam or pt")
    print("\tknown or kn")
    print("\taccuse or ac; trust or tr")
    print("\tforcevote or fv")

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
        elif (user_input == "known" or user_input == "kn"):
            role = sanitised_input("Which role? ", int, 0, 6)
            person = sanitised_input("Which person? ", int, 0, a.num_players - 1)
            a.known(role, person)
        elif (user_input == "guessmerlin" or user_input == "gm"):
            guess = sanitised_input("Who do you think is Merlin? ", int, 0, a.num_players - 1)
            actual = sanitised_input("Who is actually Merlin? ", int, 0, a.num_players - 1)
            a.guess_merlin(guess, actual)
        elif a.game_state != 2: # If not! bad guys guess Merlin
            if (user_input == "proposeteam" or user_input == "pt"):
                if not (a.quest_state[4] > -1):
                    print("Propose your team!")
                    proposed_team, current_quest = [], a.cur_quest()
                    max_people, num_people = a.people_per_quest[current_quest], 1
                    while num_people <= max_people:
                        added_player = sanitised_input("Choose team member " + str(num_people) + " for Quest " + str(current_quest) + ": ", int, max_=a.num_players - 1)
                        if added_player in proposed_team:
                            print("Player", added_player, "is already chosen to be on the quest.")
                        else:
                            proposed_team.append(added_player)
                            num_people += 1
                    proceed = input("Proceed to vote? Yes (y) or No (n)? ")
                    a.propose_team(proposed_team, current_quest, max_people, proceed)
                else:
                    print("Five quests have already been completed!")
            elif (user_input == "accuse" or user_input == "ac"):
                player_accusing = sanitised_input("Who accused? ", int, 0, a.num_players - 1)
                player_accused = sanitised_input("Accusing whom? ", int, 0, a.num_players)
                a.accuse(player_accusing, player_accused)
            elif (user_input == "trust" or user_input == "tr"):
                player_trusting = sanitised_input("Who trusts? ", int, 0, a.num_players - 1)
                player_trusted = sanitised_input("Trusts whom? ", int, 0, a.num_players)
                a.trust(player_trusting, player_trusted)
            elif (user_input == "forcevote" or user_input == "fv"):
                print("I hope you know what you're doing! Voting the previous proposal...")
                approved_counts, rejected_counts, vote_list = 0, 0, []
                for i in range(a.num_players):
                    choice = sanitised_input("Player " + str(i) + ", approve (1) or reject (0) mission? ", int, 0, 1)
                    if choice == 1:
                        approved_counts += 1
                    else: 
                        rejected_counts += 1
                    vote_list.append(choice)
                a.force_vote(approved_counts, rejected_counts, vote_list)
            elif (user_input == "analyze" or user_input == "ana"):
                ana = Analysis(a)
                ana.start_analysis()
                ana.analyze()
                print(ana.player_values)
            elif (user_input == "anamore"):
                ana = Analysis(a)
                ana.start_analysis()
                ana.analyze(15)
                print(ana.player_values)
            else:
                print("Invalid command.")
        else:
            print("Invalid command, must guess Merlin.")
    if a.game_state == 0:
        print("Minions have won!")
    else:
        print("Servants have won!")