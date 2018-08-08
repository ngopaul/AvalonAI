# This is the main file for Avalon AI inputs.
import sqlite3
from sqlite3 import OperationalError

class Avalon:
    def __init__(self):
        """ Game States:
            # 0 : Minions of Mordred win
            # 1 : Servants of Arthur win
            # 2 : Servants of Arthur won, but Minions of Mordred still choose to assassinate
            # 3 : Game in progress """
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
        self.num_players = int(input("Number of players: "))
        self.role_types['Normal Bad'] = int(input("Normal Bad: "))
        self.role_types['Normal Good'] = int(input("Normal Good: "))
        self.role_types['Merlin'] = int(input("Merlin: "))
        self.role_types['Percival'] = int(input("Percival: "))
        self.role_types['Morgana'] = int(input("Morgana: "))
        self.role_types['Mordred'] = int(input("Mordred: "))
        self.role_types['Oberon'] = int(input("Oberon: "))
        
        print("Initializing databases...")
        conn = sqlite3.connect("avalon.db")
        c = conn.cursor()
        self.executeScriptsFromFile("avalon.sql", c)
        self.check_parameters(c)

    def check_parameters(self, c):
        c.execute("SELECT * FROM player_alignment")
        rows = c.fetchall()
        if not (5 <= self.num_players <= 10):
            print("Avalon requires at least 5 players and at most 10 players!")
            self.initialize()
        else: 
            num_good = self.role_types['Normal Good'] + self.role_types['Merlin'] + self.role_types['Percival']
            num_bad = self.role_types['Normal Bad'] + self.role_types['Morgana'] + self.role_types['Mordred'] + self.role_types['Oberon']
            for row in rows:
                if row[0] == self.num_players:
                    if row[1] == num_good and row[2] == num_bad:
                        print("WOOHOO!")
                    else:
                        print("For", self.num_players, "players, you must have", row[1], "good guys and", row[2], "bad guys.")


    """ One player accuses another of being evil, or being a specific role. """
    def accuse(self):
        # TODO
        pass

    """ The person using the AI knows the alignment of a player. """
    def known(self):
        self.known_players[input("Which person? ")] = input("Which role? ")

    """ The current leader proposes a team. """
    def propose_team(self):
        # TODO
        pass

    """ The players vote on the most recently proposed team. If rejected, adds to the rejected tally. """
    def vote(self):
        # TODO
        pass

    """ Gets the results of a quest. Passes possesion of the leader to the next person. """
    def quest(self):
        # TODO
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
    # TODO
    pass

while (a.game_state > 1):
    user_input = input("Command (type help for commands): ")
    if (user_input == "help"):
        print_help()
    if (user_input == "proposeteam" or user_input == "pt"):
        a.propose_team()
    if (user_input == "accuse" or user_input == "ac"):
        a.accuse()
    if (user_input == "vote" or user_input == "v"):
        a.vote()

