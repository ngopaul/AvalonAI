# AVALON AI

TODO:

- disallow putting in duplicates of a person on a quest
- check for the win condition of the game


proposed_team, current_quest = [], len(self.quest_history)
max_people, num_people = self.people_per_quest[current_quest], 1

while num_people <= max_people:
    added_player = sanitised_input("Choose team member " + str(num_people) + " for Quest " + str(current_quest) + ": ", int, max_=self.num_players - 1)
    if added_player in proposed_team:
        print("Player", added_player, "is already chosen to be on the quest.")
    else:
        proposed_team.append(added_player)
        num_people += 1