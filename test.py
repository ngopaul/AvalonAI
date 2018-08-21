from main import Avalon
from utils import *
from analysis import *
import os
import subprocess as sub
from pyautogui import press, typewrite, hotkey
import sys

# pip install pyautogui

a = Avalon(1)

""" Test 1:
3 normal good, 2 normal evil
"""
def test1():
    global a

    a = Avalon(1) # don't preset-initialize
    # 5 people, with Merlin and Mordred
    # this games simulates Merlin as player 2, Mordred as 3, and Normal Evil as 4
    a.initialize(5, {'Normal Bad': 1, 'Normal Good': 2, 'Merlin': 1, 'Percival': 0, 'Morgana': 0, 'Mordred': 1, 'Oberon': 0}, 0)
    
    # propose a team with players 0, 1
    # don't actually propose the team
    a.propose_team([1, 0], a.cur_quest(), a.people_per_quest[a.cur_quest()], 'n')

    # assert our tally for rejected missions is same
    assert a.quest_state[5] == 0

    # propose a team with players 0, 1
    # move on to vote
    # 3 accept the team, pretty random because there is no knowledge rn
    typewrite("1\n1\n0\n0\n1\n")
    # the quest succeeds
    typewrite("1\n1\n")
    a.propose_team([0, 1], a.cur_quest(), a.people_per_quest[a.cur_quest()], 'y')

    # assert our tally for rejected missions has gone back to 0
    assert a.quest_state[5] == 0

    # propose a team with players 0, 1, 3
    # move on to vote
    # only two accept the team
    typewrite("1\n0\n1\n0\n0\n")
    a.propose_team([0, 1, 3], a.cur_quest(), a.people_per_quest[a.cur_quest()], 'y')

    # assert our tally for rejected missions has gone up
    assert a.quest_state[5] == 1

    # propose a team with players 0, 1, 4
    # move on to vote
    # four accept the team
    typewrite("1\n0\n1\n1\n1\n")
    # the quest succeeds
    typewrite("1\n1\n1\n")
    a.propose_team([0, 1, 4], a.cur_quest(), a.people_per_quest[a.cur_quest()], 'y')

    ana = Analysis(a)
    ana.start_analysis()
    ana.analyze(10)
    print("Guess good/evil: ", ana.player_values)

    assert a.quest_state[5] == 0

    # propose a team with players 0, 3; trying to weed out an evil
    # move on to vote
    # all GOOD PEOPLE accept the team
    typewrite("1\n1\n1\n0\n0\n")
    # the quest fails
    typewrite("0\n1\n")
    a.propose_team([0, 3], a.cur_quest(), a.people_per_quest[a.cur_quest()], 'y')
    
    # go back to the team of 3 that succeeded before

    # propose a team with players 0, 1, 4
    # move on to vote
    # three accept the team, including both BAD PEOPLE
    typewrite("1\n0\n0\n1\n1\n")
    # the quest fails
    typewrite("0\n1\n1\n")
    a.propose_team([0, 1, 4], a.cur_quest(), a.people_per_quest[a.cur_quest()], 'y')

    ana = Analysis(a)
    ana.start_analysis()
    ana.analyze(10)
    print("Guess good/evil: ", ana.player_values)

    # only one quest left!

    # propose a team with players 1, 2, 3 (good guys)
    # move on to vote
    # three good guys accept the team
    typewrite("1\n1\n1\n0\n0\n")
    # the quest succeeds
    typewrite("1\n1\n1\n")
    a.propose_team([1, 2, 3], a.cur_quest(), a.people_per_quest[a.cur_quest()], 'y')


    # a.cl_known(2, 2) # player 2, is merlin
    # a.cl_known(0, 1)
    # a.cl_known(1, 1)


    # print(get_all_players(a))
    # print(get_known_players(a))
    # print(create_possibilities(a))
    
    ana = Analysis(a)
    ana.start_analysis()
    ana.analyze()
    print("Guess good/evil: ", ana.player_values)

    # a.print_all()

    assert a.game_state == 2 # the minions of mordred need to decide who the merlin is

    # guess the merlin right!
    a.guess_merlin(2, 2)

    assert a.game_state == 0

    print("All tests passed.")