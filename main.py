# This is the main file for Avalon AI inputs.
import sqlite3
from sqlite3 import OperationalError

""" Utilities """
# @StackOverflow Community
def sanitised_input(prompt, type_=None, min_=None, max_=None, range_=None):
    if min_ is not None and max_ is not None and max_ < min_:
        raise ValueError("min_ must be less than or equal to max_.")
    while True:
        ui = input(prompt)
        if type_ is not None:
            try:
                ui = type_(ui)
            except ValueError:
                print("Input type must be {0}.".format(type_.__name__))
                continue
        if max_ is not None and ui > max_:
            print("Input must be less than or equal to {0}.".format(max_))
        elif min_ is not None and ui < min_:
            print("Input must be greater than or equal to {0}.".format(min_))
        elif range_ is not None and ui not in range_:
            if isinstance(range_, range):
                template = "Input must be between {0.start} and {0.stop}."
                print(template.format(range_))
            else:
                template = "Input must be {0}."
                if len(range_) == 1:
                    print(template.format(*range_))
                else:
                    print(template.format(" or ".join((", ".join(map(str,
                                                                     range_[:-1])),
                                                       str(range_[-1])))))
        else:
            return ui

class Avalon:
    def __init__(self):
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
            # 3: number of successes """
        self.quest_history = []
        """ Known Players:  
            # list of size NUM_PLAYERS, where each index correlates to the player number
            # the values are the role types, as above. """
        self.known_players = []

        self.initialize()
       

    """ Allows us to read in SQL files. """
    def executeScriptsFromFile(self, filename, c):
        # Open and read the file as a single buffer
        fd = open(filename, 'r')
        sqlFile = fd.read()
        fd.close()

        # all SQL commands (split on ';')
        sqlCommands = sqlFile.split(';')

        # Execute every command from the input file
        for command in sqlCommands:
            # This will skip and report errors
            # For example, if the tables do not yet exist, this will skip over
            # the DROP TABLE commands
            try:
                c.execute(command)
            except OperationalError as msg:
                print("Command skipped: ", msg)

    """ Initializes the game. """
    def initialize(self):
        useIn = input("Welcome to Avalon AI! Press enter to continue. ")
        if useIn != "skip":
            self.num_players = sanitised_input("Number of Players: ", int, 5, 10)
            self.role_types['Normal Bad'] = sanitised_input("Normal Bad: ", int)
            self.role_types['Normal Good'] = sanitised_input("Normal Good: ", int)
            self.role_types['Merlin'] = sanitised_input("Merlin: ", int)
            self.role_types['Percival'] = sanitised_input("Percival: ", int)
            self.role_types['Morgana'] = sanitised_input("Morgana: ", int)
            self.role_types['Mordred'] = sanitised_input("Mordred: ", int)
            self.role_types['Oberon'] = sanitised_input("Oberon: ", int)
            self.known_players = [-1 for i in range(self.num_players)]

            print("Initializing databases...")
            conn = sqlite3.connect("avalon.db")
            c = conn.cursor()
            self.executeScriptsFromFile("avalon.sql", c)
            self.check_parameters(c)
            self.load_info(c)
            print("Initialized databases.")
            
            self.current_leader = sanitised_input("Starting leader: ", int, max_= self.num_players - 1)
        elif useIn == "skip":
            self.num_players = 5
            self.role_types['Normal Bad'] = 2
            self.role_types['Normal Good'] = 3
            self.known_players = [-1 for i in range(self.num_players)]
            conn = sqlite3.connect("avalon.db")
            c = conn.cursor()
            self.load_info(c)
        print("Let the game begin!\n")

    def check_parameters(self, c):
        c.execute("SELECT * FROM player_alignment WHERE num_players = " + str(self.num_players))
        row = c.fetchall()[0]
        print(row)
        num_good = self.role_types['Normal Good'] + self.role_types['Merlin'] + self.role_types['Percival']
        num_bad = self.role_types['Normal Bad'] + self.role_types['Morgana'] + self.role_types['Mordred'] + self.role_types['Oberon']
        if not (row[1] == num_good and row[2] == num_bad):
            print("For", self.num_players, "players, you must have", row[1], "good guys and", row[2], "bad guys.")

    def load_info(self, c):
        c.execute("SELECT * FROM people_per_quest WHERE num_players = " + str(self.num_players))
        row = c.fetchall()[0]
        self.people_per_quest = [i for i in row[1:]]
        c.execute("SELECT * FROM required_fails_per_quest WHERE num_players = " + str(self.num_players))
        row = c.fetchall()[0]
        self.required_fails_per_quest = [i for i in row[1:]]

    def print_all(self):
        print("Game state:", self.game_state)
        print("Number of players:", self.num_players)
        print("Roles:", self.role_types)
        print("Propose history:", self.propose_history)
        print("Vote history:", self.vote_history)
        print("Quest state:", self.quest_state)
        print("Known Players:", self.known_players)

    """ One player accuses another of being evil, or being a specific role. """
    def accuse(self):
        # TODO
        pass

    """ The person using the AI knows the alignment of a player. """
    def known(self):
        self.known_players[input("Which person? ")] = input("Which role? ")

    """ The current leader proposes a team. """
    def propose_team(self):
        print("Propose your team!")
        proposed_team = []
        current_quest = len(self.quest_history)
        for i in range(self.people_per_quest[current_quest]):
            added_player = sanitised_input("Pick player " + str(i) + " for Quest " + str(current_quest) + ": ", int, max_=self.num_players - 1)
            proposed_team.append(added_player)
        self.propose_history.append(proposed_team)
        answer = input("Proceed to vote? Yes (y) or No (n)? ")
        if answer.lower() == "y":
            self.vote()
        else:
            self.vote_history.append([]) #Empty entry
            self.quest_state[5] += 1
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
            self.quest_state[5] = self.quest_state[5] + 1 # Increment rejected tally
            self.change_current_leader()
            return
    
    """ We said we didn't want to vote after the proposal... but we did want to """
    def force_vote(self):
        self.quest_state[5] -= 1
        self.vote()

    """ Gets the results of a quest. Passes possesion of the leader to the next person. """
    def quest(self):
        print("Quest Initiated!")
        votes = []
        cur_quest = self.cur_quest
        for i in range(self.people_per_quest[self.cur_quest()]):
            votes.append(sanitised_input("Result " + str(i) + " is success (1) or fail (0): ", int, 0, 1))
        fail = 0
        success = 0
        for vote in votes:
            if vote == 0:
                fail += 1
            else:
                success += 1
        quest_result = int(fail < self.required_fails_per_quest[cur_quest()])
        self.go_quest(len(self.propose_history) - 1, quest_result, fail, success)
        self.quest_state[cur_quest] = quest_result
        self.quest_state[5] = 0
        self.change_current_leader()
        
    def cur_quest(self):
        return len(self.quest_history)

    def go_quest(self, propose_index, result, fails, successes):
        self.quest_history.append([propose_index, result, fails, successes])

    def change_current_leader(self):
        self.current_leader = (self.current_leader + 1) % self.num_players

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

a = Avalon()
user_input = ""

def print_help():
    print("printall or pa;", "proposeteam or pt;", "accuse or ac;", "forcevote or fv;", "break")

while (a.game_state > 1):
    user_input = input("Command (type help for commands): ")
    if (user_input == "help"):
        print_help()
    elif (user_input == "printall" or user_input == "pa"):
        a.print_all()
    elif (user_input == "proposeteam" or user_input == "pt"):
        if a.quest_state[4] > -1:
            a.propose_team()
        else:
            print("Five quests have already been completed!")
    elif (user_input == "accuse" or user_input == "ac"):
        a.accuse()
    elif (user_input == "forcevote" or user_input == "fv"):
        print("I hope you know what you're doing! Voting the previous proposal...")
        a.force_vote()
    elif (user_input == "break"):
        break

