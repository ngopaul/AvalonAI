# pygame front end for avalon AI

from main import *
import time
import sys, pygame
pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 30)
background = (30, 30, 30)
size = width, height = 1280, 800
screen = pygame.display.set_mode(size)

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)

# we must start our event dictionary here because everything below is used by pygame
event_dict = {
    'errplayer' : 257,

    'initnumplayers' : 32768,
    'chooseroles' : 37270
}

def make_event(eventname, errorstate):
    new_event = pygame.event.Event(pygame.USEREVENT, {"name": eventname, "error": errorstate})
    pygame.event.post(new_event)

""" There are many different states in the game. In order to easily be able to 
change between states and therefore change the available commands, each of 
these functions will populate the commands list properly. """

# accuse, trust, known, propose team
def commands_change(list_commands):
    commands.remove_all()
    checkbox_loc = [40, 200]
    # making all the commands
    for command in list_commands:
        commands.append(CheckBox(checkbox_loc[0], checkbox_loc[1],command,'radio', COLOR_INACTIVE, 'mainstate', command))
        checkbox_loc[1] += 25

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

    def reset(self):
        self.accuse = []
        self.trust = []
        self.proposed_team = []
        self.vote_list = [0 for i in range(self.num_players)]
        self.known = []
        self.quest_votes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        players.deactivate()

    def update(self):
        pass
    
    def handle_event(self, event):
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
                        self.a.initialize(self.num_players, role_types, 0)

                        # making all the players
                        for i in range(self.num_players):
                            players.append(Player(i))
                        
                        # prepopulating vote_list
                        self.vote_list = [0 for i in range(self.num_players)]

                        # showing the right commands
                        commands_change(["accuse", "trust", 'known', 'propose_team'])

                        roles_involved.items = [] # to save on time

                        # start the mainstate of the game!
                        make_event("mainstate", False)

                    elif prev_event == "accuse":
                        assert len(self.accuse) == 2
                        self.a.accuse(self.accuse[0], self.accuse[1])
                    elif prev_event == "trust":
                        assert len(self.trust) == 2
                        self.a.trust(self.trust[0], self.trust[1])
                    elif prev_event == "known":
                        assert len(self.known) == 2
                        self.a.known(self.known[0], self.known[1])
                    elif prev_event == "propose_team":
                        self.a.propose_team(self.proposed_team, self.a.cur_quest(), self.a.people_per_quest[self.a.cur_quest()], 'y', True)
                        commands_change(['vote'])
                    elif prev_event == "vote":
                        self.a.vote(self.vote_list.count(1), self.vote_list.count(0), self.vote_list, True)
                        commands_change(['quest'])
                    elif prev_event == "quest":
                        self.a.quest(self.a.quest_state[5], self.quest_votes[:self.a.people_per_quest[self.a.cur_quest()]], self.a.cur_quest(), True)
                        commands_change(["accuse", "trust", 'known', 'propose_team'])
                    main_game.a.print_all()
                    print("\n")
                    make_event('mainstate', False)
                    self.reset()
            except:
                make_event("Improper Input", True)
                make_event('mainstate', False)
                self.reset()

    # parses text input. Here we use current event, not previous event 
    # (since we don't click the check mark for text)
    def parse(self, inpt):
        print("Parsing " + inpt, "with current_event: " + str(current_event))
        if current_event == 'initnumplayers':
            try:
                self.num_players = int(inpt)
                if 5 <= self.num_players <= 10:
                    make_event("chooseroles", False)
                else:
                    make_event("Wrong Number of Players", True)
            except:
                print("Throwing error.")
                make_event("Improper Input", True)
        elif current_event == 'quest':
            # TODO
            pass

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

class MainText(TextOut):
    def __init__(self, color = COLOR_ACTIVE):
        self.x = 40
        self.y = 20
        self.color = color
        self.text = "How many players?"
        self.txt_surface = FONT.render(self.text, True, self.color)
        self.txt_surface_clear = FONT.render(self.text, True, background)
    
    def update(self):
        self.clear()
        if current_event == 'initnumplayers':
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
            self.text = "Choose known person. " + str(main_game.known)
        elif current_event == 'propose_team':
            self.text = "Choose team. " + str(main_game.proposed_team)
        elif current_event == 'vote':
            self.text = "Select yes votes. " + str(main_game.vote_list)
        elif current_event == 'quest':
            self.text = "Type number of fails. " + str(main_game.quest_votes[:main_game.a.people_per_quest[main_game.a.cur_quest()]])
        self.txt_surface = FONT.render(self.text, True, self.color)
        self.txt_surface_clear = FONT.render(self.text, True, background)
        self.draw(screen)

class ErrText(TextOut):
    def __init__(self, color = COLOR_ACTIVE):
        self.x = 45
        self.y = 45
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

class CheckBox(TextOut):
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

class Button():
    def __init__(self, x, y, image, eventtype = 'submitnext', typeof = 'activate', hidelist = []): #also toggle
        self.x = x
        self.y = y
        self.image = image
        self.imagerect = image.get_rect()
        self.imagerect.left = self.x
        self.imagerect.top = self.y
        self.width = image.get_width()
        self.height = image.get_height()
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

class ManyItems():
    def __init__(self, items):
        self.items = items
    
    def handle_event(self, event):
        for item in self.items:
            item.handle_event(event)
    
    def update(self):
        for item in self.items:
            item.update()

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

class Player():
    def __init__(self, number):
        theta = 2 * pi * number / main_game.num_players
        r = 100
        self.number = number
        self.x, self.y = polar_to_cartesian(r, theta)
        self.x = int(self.x + 640) # center x and y
        self.y = int(self.y + 400)
        self.active = False
        self.color = COLOR_INACTIVE
        self.rect = pygame.Rect(self.x - 15, self.y - 15, 30, 30)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and current_event != 'mainstate':
                # Toggle the active variable.
                self.active = not self.active

                # Do the current action's work (for each action)

                if current_event == "accuse":
                    if self.active and len(main_game.accuse) < 2: # you selected it
                        main_game.accuse.append(self.number)
                    elif not self.active: # you deselected it
                        try:
                            main_game.accuse.remove(self.number)
                        except:
                            pass
                    print("accuse:", main_game.accuse)
                elif current_event == "trust":
                    if self.active and len(main_game.trust) < 2: # you selected it
                        main_game.trust.append(self.number)
                    elif not self.active: # you deselected it
                        try:
                            main_game.trust.remove(self.number)
                        except:
                            pass
                    print("trust:", main_game.trust)
                elif current_event == "propose_team":
                    if self.active: # you selected it
                        main_game.proposed_team.append(self.number)
                    elif not self.active: # you deselected it
                        try:
                            main_game.proposed_team.remove(self.number)
                        except:
                            pass
                    print("proposed team:", main_game.proposed_team)
                elif current_event == "vote":
                    if self.active: # you selected it
                        main_game.vote_list[self.number] = 1
                    else: # you deselected it
                        main_game.vote_list[self.number] = 0
                    print("current votes:", main_game.vote_list)
                elif current_event == "quest":
                    if self.active: # you selected it
                        main_game.quest_votes[self.number] = 1
                    else: # you deselected it
                        main_game.quest_votes[self.number] = 0
                    print("current quest outcome:", main_game.quest_votes[:main_game.a.people_per_quest[main_game.a.cur_quest()]])
            # Change the current color of the box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

    def update(self):
        self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        self.draw(screen)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15, 0)

done = False
clock = pygame.time.Clock()

# initialize roles involved right now because that's what you want 
# to work with at the start of the game
checkboxes = []
checkbox_loc = [40, 200]
for player_type in list(role_numbers.keys()):
    if player_type != "Normal Bad" and player_type != "Normal Good":
        checkboxes.append(CheckBox(checkbox_loc[0], checkbox_loc[1], player_type))
        checkbox_loc[1] += 25
roles_involved = ManyItems(checkboxes)

# we'll initialize COMMANDS later.
commands = ManyItems([])
# we'll initialize PLAYERS later.
players = ManyItems([])

# Our main input box for text input
main_input = InputBox(100, 100, 140, 32, hidelist=['chooseroles', 'mainstate', 'accuse', 'trust', 'known', 'propose_team', 'vote', 'quest', 'vote_merlin'])
# Our main text
main_text = MainText()
# our error messages
err_text = ErrText()
# a handler between pygame and avalon
main_game = MainGame()
# our two buttons for summission and cancelation
submit_button = Button(990, 30, pygame.image.load("checkmark.png"), hidelist = ['initnumplayers'])
cancel_button = Button(1030, 30, pygame.image.load("xmark.png"), 'cancelnext', hidelist = ['initnumplayers'])

# we iterate through our items to update them
items = [main_game, players, commands, main_input, main_text, err_text, submit_button, cancel_button, roles_involved]

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
            print("Current event:", current_event)
            print("Previous event:", prev_event)
        for item in items:
            item.handle_event(event)
    for item in items:
        item.update()
    pygame.display.flip()
    clock.tick(30)
