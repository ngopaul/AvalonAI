# pygame front end for avalon AI

from main import *
import time
import sys, pygame, traceback
pygame.init()
pygame.font.init()
background = (30, 30, 30)
size = width, height = 1280, 800
screen = pygame.display.set_mode(size)

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)

""" Make an event occur in the pygame event queue. The eventname is the keyword that
most pygame objects will use to decide how to update themselves. The errorstate
is a boolean value, True if the event is an error and false otherwise. """
def make_event(eventname, errorstate):
    new_event = pygame.event.Event(pygame.USEREVENT, {"name": eventname, "error": errorstate})
    pygame.event.post(new_event)

""" There are many different states in the game. In order to easily be able to 
change between states and therefore change the available commands, this 
function will populate the commands list properly. It takes in a list of commands,
and changes the ManyItems of ActionBoxes. """
# accuse, trust, known, propose team, print, analyze is the standard
def commands_change(list_commands):
    commands.remove_all()
    actionbox_loc = [270, 140]
    # making all the commands
    for command in list_commands:
        commands.append(ActionBox(actionbox_loc[0], actionbox_loc[1],command,'radio', COLOR_INACTIVE, 'mainstate', command))
        actionbox_loc[1] += 35

""" This is the MainGame object, which handles every event 
 and puts it into an Avalon Object. """
class MainGame:
    def __init__(self):
        self.num_players = 0
        self.a = Avalon(1)
        self.accuse = []
        self.trust = []
        self.proposed_team = []
        self.vote_list  = []
        self.known = []
        self.quest_votes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.known_player = 0
        self.merlin_guess = 0
        self.actual_merlin = 0
        self.analyze_num = -1

    # return to a state where everything recorded is empty.
    # does not reset the game, only resets what is selected.
    def reset(self):
        self.accuse = []
        self.trust = []
        self.proposed_team = []
        self.vote_list = [0 for i in range(self.num_players)]
        self.known = []
        self.quest_votes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        players.deactivate()

    # the main game only handles events, 
    # and should not be displayed, as it is abstract.
    def update(self): 
        pass
    
    def handle_event(self, event):
        if self.a.game_state < 2: # the game is over
            commands_change(['analyze', 'print'])
        if event.type == pygame.USEREVENT and not event.__dict__['error']:
            try: # to catch errors and instead throw an Event error
                if current_event == "submitnext":
                    if prev_event == "chooseroles":
                        role_types = {'Normal Bad': 0, 'Normal Good': 0, 'Merlin': 0, 'Percival': 0, 'Morgana': 0, 'Mordred': 0, 'Oberon': 0}
                        for role in roles_involved:
                            if role.active:
                                role_types[role.text] += 1
                        role_types['Normal Bad'] = player_alignment[self.num_players][1] - (role_types['Morgana'] + role_types['Mordred'] + role_types['Oberon'])
                        role_types['Normal Good'] = player_alignment[self.num_players][0] - (role_types['Merlin'] + role_types['Percival'])
                        if role_types['Normal Bad'] < 0 or role_types['Normal Good'] < 0: # selected too many roles
                            assert 1 == 0
                        print("a.initialize(%s, %s, 0)" % (self.num_players, role_types))
                        self.a.initialize(self.num_players, role_types, 0)
                        # making all the players
                        for i in range(self.num_players):
                            players.append(Player(i))
                        # setting up the gameboard
                        items.append(GameBoard(320, 385, 0.125, str(self.num_players) + "playerboard.jpg", 0, 0))
                        # making the rotate buttons
                        rotate_buttons.append(Rotate(600, 320, pygame.image.load("resources/" + "arrowleft.png"),pi/40))
                        rotate_buttons.append(Rotate(640, 320, pygame.image.load("resources/" + "arrowright.png"),-pi/40))
                        # prepopulating vote_list
                        self.vote_list = [0 for i in range(self.num_players)]
                        # showing the right commands
                        commands_change(["accuse", "trust", 'known', 'propose_team', 'analyze', 'print'])
                        roles_involved.items = [] # to save on time
                        # start the mainstate of the game!
                        make_event("mainstate", False)
                    # every command has self.reset() except propose_team, 
                    # because you can propose a team and then decide not to go through with it.
                    elif prev_event == "accuse":
                        print("a.accuse("+str(self.accuse[0])+", "+str(self.accuse[1])+")")
                        self.a.accuse(self.accuse[0], self.accuse[1])
                        self.reset()
                    elif prev_event == "trust":
                        print("a.trust("+str(self.trust[0])+", "+str(self.trust[1])+")")
                        self.a.trust(self.trust[0], self.trust[1])
                        self.reset()
                    elif prev_event == "known":
                        print("a.known("+str(self.known)+", "+str(self.known_player)+")")
                        self.a.known(self.known, self.known_player)
                        self.reset()
                    elif prev_event == "propose_team":
                        assert self.a.people_per_quest[self.a.cur_quest()] == len(self.proposed_team)
                        players.deactivate()
                        commands_change(['proceed_on_proposed', 'cancel_on_proposed', 'print'])
                    elif prev_event == "proceed_on_proposed":
                        print("a.propose_team(%s, %s, %s, 'y', True)" % (self.proposed_team, self.a.cur_quest(), self.a.people_per_quest[self.a.cur_quest()]))
                        self.a.propose_team(self.proposed_team, self.a.cur_quest(), self.a.people_per_quest[self.a.cur_quest()], 'y', True)
                        players.deactivate()
                        commands_change(['vote', 'print'])
                    elif prev_event == "cancel_on_proposed":
                        print("a.propose_team(%s, %s, %s, 'n', True)" % (self.proposed_team, self.a.cur_quest(), self.a.people_per_quest[self.a.cur_quest()]))
                        self.a.propose_team(self.proposed_team, self.a.cur_quest(), self.a.people_per_quest[self.a.cur_quest()], 'n', True)
                        self.reset()
                        commands_change(["accuse", "trust", 'known', 'propose_team', 'analyze', 'print'])
                    elif prev_event == "vote":
                        print("a.vote(%s, %s, %s, True)" % (self.vote_list.count(1), self.vote_list.count(0), self.vote_list))
                        continue_to_quest = self.a.vote(self.vote_list.count(1), self.vote_list.count(0), self.vote_list, True)
                        if continue_to_quest:
                            commands_change(['quest', 'print'])
                            self.reset()
                        else:
                            commands_change(["accuse", "trust", 'known', 'propose_team', 'analyze', 'print'])
                            self.reset()
                    elif prev_event == "quest":
                        print("a.quest(%s, %s, %s, True)" % (self.a.quest_state[5], self.quest_votes[:self.a.people_per_quest[self.a.cur_quest()]], self.a.cur_quest()))
                        self.a.quest(self.a.quest_state[5], self.quest_votes[:self.a.people_per_quest[self.a.cur_quest()]], self.a.cur_quest(), True)
                        if self.a.game_state > 2:
                            commands_change(["accuse", "trust", 'known', 'propose_team', 'analyze', 'print'])
                        elif self.a.game_state == 2:
                            commands_change(["guess_merlin", 'analyze','print'])
                        self.reset()
                    elif prev_event == "print":
                        print("---")
                        main_game.a.print_all()
                        print("---")
                    elif prev_event == "analyze":
                        self.ana = Analysis(self.a)
                        self.ana.start_analysis()
                        print("---")
                        if self.analyze_num > 0:
                            self.ana.analyze(self.analyze_num)
                        else:
                            self.ana.analyze()
                        print("---")
                    elif prev_event == "guess_merlin":
                        make_event("check_merlin", False)
                        players.deactivate()
                        return
                    elif prev_event == "check_merlin":
                        print("a.guess_merlin(%s, %s)" % (self.merlin_guess, self.actual_merlin))
                        self.a.guess_merlin(self.merlin_guess, self.actual_merlin)
                        commands_change(["analyze", 'print'])
                    make_event('mainstate', False)
            except Exception as e:
                traceback.print_exc()
                print(e)
                make_event("Error! See Console.", True)
                make_event('mainstate', False)
                self.reset()

    # parses text input. Here we use current event, not previous event 
    # (since we don't click the check mark for text)
    def parse(self, inpt):
        # print("Parsing " + inpt, "with current_event: " + str(current_event))
        if current_event == 'initnumplayers':
            try:
                self.num_players = int(inpt)
                if 5 <= self.num_players <= 10:
                    make_event("chooseroles", False)
                else:
                    make_event("Wrong Number of Players", True)
            except:
                # print("Throwing error.")
                make_event("Improper Input", True)
        elif current_event == 'quest':
            # TODO
            pass

        elif current_event == 'analyze':
            try:
                self.analyze_num = int(inpt)
            except:
                self.analyze_num = -1
                make_event("NaN", True)

""" An input box, which when in an active state (clicking on it), will allow
 text input which can then be parsed by the MainGame, after presing the Enter key. """
class InputBox:
    def __init__(self, x, y, w, h, text='', hidelist = []):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.hidelist = hidelist

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # print(self.text)
                    main_game.parse(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width
        if current_event not in self.hidelist:
            self.draw(screen)
        else:
            self.clear()

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def clear(self):
        pygame.draw.rect(screen, background, self.rect, 0)

""" Text displayed on the screen. """
class TextOut:
    def __init__(self, x, y, text, color = COLOR_ACTIVE):
        self.x = x
        self.y = y
        self.color = color
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.txt_surface_clear = FONT.render(text, True, background)
    
    def handle_event(self, event):
        pass
    
    def update(self):
        pass
    
    def clear(self):
        screen.blit(self.txt_surface_clear, (self.x, self.y))

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.x, self.y))

""" A TextOut class specifically designed to handle STATES in the game, 
such as during a selected action. """
class MainText(TextOut):
    def __init__(self, color = COLOR_ACTIVE):
        self.x = 140
        self.y = 40
        self.color = color
        self.text = "How many players?"
        self.txt_surface = FONT.render(self.text, True, self.color)
        self.txt_surface_clear = FONT.render(self.text, True, background)
    
    def update(self):
        self.clear()
        if main_game.a.game_state == 0:
            self.text = "Minions Win!"
        elif main_game.a.game_state == 1:
            self.text = "Servants Win!"
        elif main_game.a.game_state == 2:
            if current_event == "guess_merlin":
                self.text = "Guess-merlin time!: " + str(main_game.merlin_guess)
            else:
                self.text = "Who is actually Merlin? " + str(main_game.actual_merlin)
        elif current_event == 'initnumplayers':
            self.text = "How many players?"
        elif current_event == 'chooseroles':
            self.text = "Choose the roles involved. "
        elif current_event == 'mainstate':
            self.text = "Choose an action. "
        elif current_event == 'accuse':
            self.text = "Choose a person accusing and accused. " + str(main_game.accuse)
        elif current_event == 'trust':
            self.text = "Choose person trusting and trusted. " + str(main_game.trust)
        elif current_event == 'known':
            self.text = "Choose known person. " + str(main_game.known_player) + " is " + str([num_to_names[name] for name in main_game.known])
        elif current_event in ['propose_team']:
            self.text = "Proposing team of " + str(main_game.a.people_per_quest[main_game.a.cur_quest()]) + " people: " + str(main_game.proposed_team)
        elif current_event in ['proceed_on_proposed', 'cancel_on_proposed']:
            self.text = "Click the check mark to confirm proceeding/canceling team: " + str(main_game.a.people_per_quest[main_game.a.cur_quest()]) + " people: " + str(main_game.proposed_team)
        elif current_event == 'vote':
            self.text = "Select yes votes. " + str(main_game.vote_list)
        elif current_event == 'quest':
            self.text = "Type number of fails. " + str(main_game.quest_votes[:main_game.a.people_per_quest[main_game.a.cur_quest()]])
        elif current_event == 'print':
            self.text = "Click the checkmark to console print."
        elif current_event == 'analyze':
            analyze_num = "All" if main_game.analyze_num < 0 else str(main_game.analyze_num)
            self.text = "Click checkmark to analyze and show top: " + analyze_num + " players"
        self.txt_surface = FONT.render(self.text, True, self.color)
        self.txt_surface_clear = FONT.render(self.text, True, background)
        self.draw(screen)

""" A TextOut class specifically designed to handle and print ERRORS in the game. """
class ErrText(TextOut):
    def __init__(self, color = COLOR_ACTIVE):
        self.x = 145
        self.y = 65
        self.color = color
        self.text = ""
        self.txt_surface = FONT.render(self.text, True, self.color)
        self.txt_surface_clear = FONT.render(self.text, True, background)
        self.start_time = 0
    
    def handle_event(self, event):
        if event.type == pygame.USEREVENT:
            if event.__dict__["error"] == True:
                self.clear()
                self.text = event.__dict__["name"]
                self.start_time = time.clock()
                self.txt_surface = FONT.render(self.text, True, self.color)
                self.txt_surface_clear = FONT.render(self.text, True, background)
                self.draw(screen)
    
    def update(self):
        if ((time.clock() - self.start_time) > 2):
            self.clear()
        else:
            self.draw(screen)

""" An ActionBox has TEXT, which when clicked, will MAKE an EVENT with name TEXT. 
Most commands, like accuse, propose, quest, etc. are ActionBoxes.
Note: hitbox is a rectangle, not the text. """
class ActionBox(TextOut):
    def __init__(self, x, y, text, typeof = 'check', color = COLOR_INACTIVE, activeevent = 'chooseroles', activation = ''): # another type would be radio
        self.x = x
        self.y = y
        self.color = color
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.txt_surface_clear = FONT.render(text, True, background)
        self.rect = pygame.Rect(x, y, max(200, self.txt_surface.get_width()+10), 32)
        self.active = False
        self.typeof = typeof
        self.activeevent = activeevent
        self.activation = activation

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
                if self.activation != '':
                    make_event(self.activation, False)
                    self.active = not self.active
            # Change the current color of the box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
    
    def update(self):
        if current_event == self.activeevent:
            self.draw(screen)
        else:
            self.clear()

    def draw(self, screen):
        self.txt_surface = FONT.render(self.text, True, self.color)
        screen.blit(self.txt_surface, (self.x, self.y))

""" This ActionBox specifically allows for role selection - not action. """
class RoleSelection(ActionBox):
    def __init__(self, x, y, text, color = COLOR_INACTIVE, activeeevent = 'known'):
        self.x = x
        self.y = y
        self.color = color
        self.text = text
        self.role = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.txt_surface_clear = FONT.render(text, True, background)
        self.rect = pygame.Rect(x, y, max(200, self.txt_surface.get_width()+10), 32)
        self.active = False
        self.activeevent = activeeevent
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            # Change the current color of the box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
            if self.active:
                if not role_numbers[self.role] in main_game.known:
                    main_game.known.append(role_numbers[self.role])
            else:
                if role_numbers[self.role] in main_game.known:
                    main_game.known.remove(role_numbers[self.role])

""" A Button allows some event to be added to the event queue when clicked. """
class Button():
    def __init__(self, x, y, image, eventtype = 'submitnext', typeof = 'activate', hidelist = []): #also toggle
        self.x = x
        self.y = y
        self.image = image
        self.imagerect = image.get_rect()
        self.imagerect.left = self.x
        self.imagerect.top = self.y
        self.typeof = typeof
        self.eventtype = eventtype
        self.hidelist = hidelist

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.imagerect.collidepoint(event.pos):
                make_event(self.eventtype, False)
    
    def update(self):
        if current_event not in self.hidelist:
            self.draw(screen)
        else:
            self.clear()
    
    def clear(self):
        pygame.draw.rect(screen, background, self.imagerect, 0)

    def draw(self, screen):
        screen.blit(self.image, self.imagerect)

""" Acts like a list of Objects. Any normal object method applied to ManyItems, 
such as .update or .draw or .handle_event, will be applied to each of its items.
Has special handling for Player objects. """
class ManyItems():
    def __init__(self, items):
        self.items = items
        self.angle = 0
    
    def handle_event(self, event):
        for item in self.items:
            item.handle_event(event)
    
    def update(self):
        for item in self.items:
            item.update()
        for i in range(len(self.items)):
            if isinstance(self.items[i], Player):
                theta = 2 * pi * i / main_game.num_players + self.angle
                r = 100
                self.items[i].reposition(r, theta)

    def draw(self, screen):
        for item in self.items:
            item.draw(screen)
    
    def clear(self):
        for item in self.items:
            item.clear()
    
    def __iter__(self):
        return self.items.__iter__()
    
    def append(self, item):
        self.items.append(item)
    
    def remove_all(self):
        self.items = []

    def deactivate(self):
        for item in self.items:
            item.active = False
    
    def length(self):
        return len(self.items)

""" A player is an object which can be selected to affect game state when different
actions are currently being done. For example, in 'mainstate', they cannot be selected.
However, in the 'accuse' state, they can be selected, and the first two selected will
be added to the MainGame's accuse list for when the accusal is submitted with the checkmark."""
class Player():
    def __init__(self, number):
        theta = 2 * pi * number / main_game.num_players
        r = 100
        self.number = number
        self.x, self.y = polar_to_cartesian(r, theta)
        self.x = int(self.x + 640) # center x and y
        self.y = int(self.y + 200)
        self.active = False
        self.color = COLOR_INACTIVE
        self.rect = pygame.Rect(self.x - 15, self.y - 15, 30, 30)
        self.txt_surface = FONT.render(str(self.number), True, (0, 0, 0))
    
    def reposition(self, r, theta):
        self.x, self.y = polar_to_cartesian(r, theta)
        self.x = int(self.x + 640) # center x and y
        self.y = int(self.y + 200)
        self.rect = pygame.Rect(self.x - 15, self.y - 15, 30, 30)
        self.txt_surface = FONT.render(str(self.number), True, (0, 0, 0))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos) and current_event not in ['mainstate', 'cancel_on_proposed', 'proceed_on_proposed'] :
            # Toggle the active variable.
            self.active = not self.active
            # Do the current action's work (for each action)
            try: #this try handles if main_game.____.remove(___) doesn't work
                if current_event == "accuse":
                    if self.active and len(main_game.accuse) < 2: # you selected it
                        main_game.accuse.append(self.number)
                    elif not self.active: # you deselected it
                            main_game.accuse.remove(self.number)
                elif current_event == "trust":
                    if self.active and len(main_game.trust) < 2: # you selected it
                        main_game.trust.append(self.number)
                    elif not self.active: # you deselected it
                        try:
                            main_game.trust.remove(self.number)
                        except:
                            pass
                elif current_event == "known":
                    if self.active:
                        players.deactivate()
                        self.active = True
                        main_game.known_player = self.number
                elif current_event == "propose_team":
                    if self.active: # you selected it
                        main_game.proposed_team.append(self.number)
                    elif not self.active: # you deselected it
                        main_game.proposed_team.remove(self.number)
                elif current_event == "vote":
                    if self.active: # you selected it
                        main_game.vote_list[self.number] = 1
                    else: # you deselected it
                        main_game.vote_list[self.number] = 0
                    # print("current votes:", main_game.vote_list)
                elif current_event == "quest":
                    if self.active: # you selected it
                        main_game.quest_votes[self.number] = 1
                    else: # you deselected it
                        main_game.quest_votes[self.number] = 0
                    # print("current quest outcome:", main_game.quest_votes[:main_game.a.people_per_quest[main_game.a.cur_quest()]])
                elif current_event == "guess_merlin":
                    if self.active:
                        players.deactivate()
                        self.active = True
                        main_game.merlin_guess = self.number
                elif current_event == "check_merlin":
                    if self.active:
                        players.deactivate()
                        self.active = True
                        main_game.actual_merlin = self.number
            except:
                pass
        # Change the current color of the player.
        self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

    def update(self):
        self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        self.draw(screen)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15, 0)
        screen.blit(self.txt_surface, (self.x - 7, self.y - 9))

""" Rotate button. Specifically designed to rotate players. """
class Rotate():
    def __init__(self, x, y, image, rotation):
        self.x = x
        self.y = y
        self.image = image
        self.imagerect = image.get_rect()
        self.imagerect.left = self.x
        self.imagerect.top = self.y
        self.width = image.get_width()
        self.height = image.get_height()
        self.rotation = rotation

    def handle_event(self, event):
        pass
    
    def update(self):
        # if the mouse is down and is in the picture
        if self.imagerect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                players.angle += self.rotation
        self.draw(screen)
    
    def clear(self):
        pygame.draw.rect(screen, background, self.imagerect, 0)

    def draw(self, screen):
        screen.blit(self.image, self.imagerect)

""" A token is an image which will be displayed at location X, Y with an IMAGE and a SCALE.
In the case of Avalon GUI, it literally displays tokens used in the game. """
class Token():
    def __init__(self, x, y, image, scale = 0.53):
        self.x = x
        self.y = y
        self.image = image
        self.image = pygame.transform.rotozoom(self.image, 0, scale)
        self.imagerect = image.get_rect()
        self.imagerect.left = self.x
        self.imagerect.top = self.y
        self.imagerect.width = self.imagerect.width / 2
        self.imagerect.height = self.imagerect.height / 2
    
    def update(self):
        self.draw(screen)
    
    def draw(self, screen):
        screen.blit(self.image, self.imagerect)

""" The GameBoard is a way to show the user what the real-life Avalon Board should look like. """
class GameBoard():
    def __init__(self, x, y, zoom = 0.3, image_name = "7playerboard.jpg", offsetx = 0, offsety = 0):
        self.board = pygame.image.load("resources/" + image_name)
        self.board = pygame.transform.rotozoom(self.board, 0, zoom)
        self.quests = ManyItems([])
        self.x = x
        self.y = y
        self.boardrect = self.board.get_rect()
        self.boardrect.left = self.x + offsetx
        self.boardrect.top = self.y + offsety
    
    def handle_event(self, event):
        pass

    def update(self):
        if self.quests.length() < len(main_game.a.quest_history):
            self.quests.append(Token(self.x + 25 + self.quests.length() * 113, self.y + 182, 
            pygame.image.load("resources/" + "successfulquest.png") if main_game.a.quest_history[len(main_game.a.quest_history) - 1][1] else
            pygame.image.load("resources/" + "failedquest.png")))
        self.rejected = Token(self.x + 36 + main_game.a.quest_state[5] * 82, self.y + 344, pygame.image.load("resources/" + "questmarker.png"), 0.59)
        self.draw(screen)
    
    def draw(self, screen):
        screen.blit(self.board, self.boardrect)
        self.quests.update()
        self.rejected.update()

# initialize loop and time
done = False
clock = pygame.time.Clock()

# initialize roles involved right now because that's what you want 
# to work with at the start of the game
actionboxes = []
actionbox_loc = [270, 140]
for player_type in list(role_numbers.keys()):
    if player_type != "Normal Bad" and player_type != "Normal Good":
        actionboxes.append(ActionBox(actionbox_loc[0], actionbox_loc[1], player_type))
        actionbox_loc[1] += 35
roles_involved = ManyItems(actionboxes)

# When KNOWN players need to be selected, this will show up
roleselectboxes = []
roleselect_loc = [825, 80]
for player_type in list(role_numbers.keys()):
    roleselectboxes.append(RoleSelection(roleselect_loc[0], roleselect_loc[1], player_type))
    roleselect_loc[1] += 35
known_selection = ManyItems(roleselectboxes)

# we'll fill in COMMANDS later.
commands = ManyItems([])
# we'll fill in PLAYERS later.
players = ManyItems([])
# we'll fill in ROTATE buttons later.
rotate_buttons = ManyItems([])

# Our main input box for text input (it will hide in the HIDELIST active states)
main_input = InputBox(200, 100, 140, 32, hidelist=['chooseroles', 'mainstate', 
'accuse', 'trust', 'known', 'propose_team', 'vote', 'quest', 'vote_merlin', 
'proceed_on_proposed', 'cancel_on_proposed', 'guess_merlin', 'check_merlin',
'print'])
# Our main text
main_text = MainText()
# our error messages
err_text = ErrText()
# a handler between pygame and avalon
main_game = MainGame()
# our two buttons for summission and cancelation
submit_button = Button(990, 30, 
pygame.image.load("resources/" + "checkmark.png"), hidelist = ['initnumplayers'])
cancel_button = Button(1030, 30, 
pygame.image.load("resources/" + "xmark.png"), 'cancelnext', hidelist = ['initnumplayers'])

# we iterate through our items to update them
items = [main_game, players, rotate_buttons, commands, main_input, 
main_text, err_text, submit_button, cancel_button, roles_involved, known_selection]

# keeping track of the state of the game
prev_event = ""
current_event = ""

# starts the game off with the initnumplayers mode
make_event('initnumplayers', False)

while not done:
    screen.fill(background)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.USEREVENT and event.__dict__["error"] == False:
            # not a cancel
            if event.__dict__["name"] != 'cancelnext':
                # keep track of the previous event
                if current_event not in ['submitnext']:
                    prev_event = current_event
                # update the current event
                current_event = event.__dict__["name"]
            # it is a cancel
            else: 
                # you cannot cancel the things in the list
                if not current_event in ['mainstate', 'initnumplayers']: 
                    current_event = prev_event
                    main_game.reset()
                # you tried canceling things in the list
                else: 
                    make_event("Can't cancel now!", True)
            # print("Current event:", current_event)
            # print("Previous event:", prev_event)
        for item in items:
            item.handle_event(event)
    for item in items:
        item.update()
    pygame.display.flip()
    clock.tick(30)
