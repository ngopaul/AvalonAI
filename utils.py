# Utilities File
import sqlite3
from sqlite3 import OperationalError

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

""" Allows us to read in SQL files. """
def executeScriptsFromFile(filename, c, option = "print"):
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
            if option == "print":
                print("Command skipped: ", msg)

def get_known_players(a):
    to_return = []
    for i in range(len(a.known_players)): # loop to add to our WHERE statement
        if a.known_players[i] != -1:
            to_return.append([i, a.known_players[i]])
    return to_return

role_numbers = {'Normal Bad': 0, 'Normal Good': 1, 'Merlin': 2, 'Percival': 3, 'Morgana': 4, 'Mordred': 5, 'Oberon': 6}
num_to_names = {0: 'Normal Bad', 1: 'Normal Good', 2: 'Merlin', 3: 'Percival', 4: 'Morgana', 5: 'Mordred', 6: 'Oberon'}

def get_all_players(a):
    to_return = []
    temp_dict = dict(a.role_types)
    i = 0
    for key in temp_dict.keys():
        while temp_dict[key] != 0:
            to_return.append([i, role_numbers[key]])
            i += 1
            temp_dict[key] -= 1
    return to_return

def known_to_where_statement(a):
    to_return = ""
    for pair in get_known_players(a): # loop to add to our WHERE statement
        to_return += "a" + str(pair[0] + 1) + ".role" + " = " + str(pair[1]) + " AND "
    if to_return == "":
        return ""
    else:
        to_return = to_return[:-4] + " " # delete the last AND, but not the space
        return to_return

""" Template from StackOverflow:
# creates all permutations of ABCD (e.g. CBAD, DCBA)
with llb as (
  select 'A' as col,1 as cnt union 
  select 'B' as col,3 as cnt union 
  select 'C' as col,9 as cnt union 
  select 'D' as col,27 as cnt
) 
select a1.col,a2.col,a3.col,a4.col, 0 as score
from llb a1
cross join llb a2
cross join llb a3
cross join llb a4
where a1.cnt + a2.cnt + a3.cnt + a4.cnt = 40 """
def create_possibilities(a):
    rtn = "CREATE TABLE possibilities AS SELECT DISTINCT * FROM (WITH llb as ( "
    i = 1
    players_to_roles = get_all_players(a)

    # first part (select 'A' as col, 1 as cnt); I used a binary instead of ternary sum.
    for pair in players_to_roles:
        rtn += "SELECT " + str(pair[1]) + " AS role, " + str(i) + " AS count UNION "
        i *= 2
    rtn = rtn[:-6] + ") " # remove the last union, close parens

    # second (select a1.col as a1...)
    rtn += "SELECT "
    for i in range(1, len(players_to_roles) + 1):
        rtn += ("a" + str(i) + ".role" + " as " + "a" + str(i) + ",")
    rtn = rtn + " 0 as score "

    # from llb a1 cross join ...
    rtn += " FROM llb a1 "
    for i in range(2, len(players_to_roles) + 1):
        rtn += ("CROSS JOIN llb a" + str(i) + " ")

    # where case
    rtn += "WHERE "
    for i in range(1, len(players_to_roles) + 1):
        rtn += "a" + str(i) + ".count + "
    rtn = rtn[:-2] + "= " + str(2**len(players_to_roles) - 1)
    
    # if you know something about roles already, account for that
    known_factor = known_to_where_statement(a)

    if known_factor == "":
        return rtn + ");"
    else:
        return rtn + " AND " + known_factor + ");"

def passed_votes_history(a):
    return [vote for vote in a.vote_history if vote.count(1) > vote.count(0)]

def row_to_roles(row):
    rtn = []
    for num in row:
        if type(num) == int and num in num_to_names:
            rtn.append(num_to_names[num])
        else:
            rtn.append(num)
    return rtn

def check_list(lst, MIN, MAX, length, duplicates = True):
    if len(lst) != length:
        return False
    copy = []
    for item in lst:
        if item < MIN or item > MAX:
            return False
        if not duplicates and item in copy:
            return False
        copy.append(item)
    return True

""" Checks if a person's number is valid """
def check_person(a, person_num):
    return 0 <= person_num < a.num_players and type(person_num) == int

""" Checks if a role num is valid """
def check_role(role):
    return 0 <= role < 7 and type(role) == int