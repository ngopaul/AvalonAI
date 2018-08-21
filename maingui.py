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

class MainGame:
    def __init__(self):
        self.num_players = 0
        self.player_types = list(role_numbers.keys())

    def parse(self, inpt):
        print("Parsing " + inpt, "with current_event: " + str(current_event))
        if current_event == 'initnumplayers':
            try:
                self.num_players = int(inpt)
                if 5 <= self.num_players <= 10:
                    new_event = pygame.event.Event(pygame.USEREVENT, {"name": "chooseroles", "error": False})
                    pygame.event.post(new_event)
                    checkbox_loc = [40, 200]
                    for player_type in self.player_types:
                        checkboxes.append(CheckBox(checkbox_loc[0], checkbox_loc[1], player_type))
                        checkbox_loc[1] += 25
                else:
                    new_event = pygame.event.Event(pygame.USEREVENT, {"name": "Wrong Number of Players", "error": True})
                    pygame.event.post(new_event)
            except:
                print("Throwing error.")
                new_event = pygame.event.Event(pygame.USEREVENT, {"name": "Improper Input", "error": True})
                pygame.event.post(new_event)

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

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

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

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
    
    def handle_event(self, event):
        self.clear()
        if event.type == pygame.USEREVENT:
            event_name = event.__dict__["name"]
            if event_name == 'initnumplayers':
                self.text = "How many players?"
            if event_name == 'chooseroles':
                self.text = "Choose the roles involved."

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
        # self.txt_surface.set_alpha(max(0, 255 - 50*(time.clock() - self.start_time)))
        # self.draw(screen)
        # print(time.clock(), self.start_time)
        if ((time.clock() - self.start_time) > 2):
            self.clear()
        else:
            self.draw(screen)

class CheckBox(TextOut):
    def __init__(self, x, y, text, color = COLOR_INACTIVE):
        self.x = x
        self.y = y
        self.color = color
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.txt_surface_clear = FONT.render(text, True, background)
        self.rect = pygame.Rect(x, y, max(200, self.txt_surface.get_width()+10), 32)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            # Change the current color of the box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
    
    def update(self):
        self.draw(screen)

    def draw(self, screen):
        self.txt_surface = FONT.render(self.text, True, self.color)
        screen.blit(self.txt_surface, (self.x, self.y))

class Button():
    def __init__(self, x, y, image, eventtype = 'submitnext', typeof = 'activate'): #also toggle
        self.x = x
        self.y = y
        self.image = image
        self.imagerect = image.get_rect()
        self.imagerect.move(self.x, self.y)
        self.width = image.get_width()
        self.height = image.get_height()
        self.typeof = typeof
        self.eventtype = eventtype

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.imagerect.collidepoint(event.pos):
                new_event = pygame.event.Event(pygame.USEREVENT, {"name": self.eventtype, "error": False})
                pygame.event.post(new_event)
    
    def update(self):
        self.draw(screen)
    
    def clear(self):
        pygame.draw.rect(screen, background, pygame.Rect(self.x, self.y, self.width, self.height), 0)

    def draw(self, screen):
        screen.blit(self.image, self.imagerect)

done = False
clock = pygame.time.Clock()
input_box1 = InputBox(100, 100, 140, 32)
input_boxes = [input_box1]
checkboxes = []
main_text = MainText()
err_text = ErrText()
main_game = MainGame()
submit_button = Button(990, 30, pygame.image.load("checkmark.png"))

current_event = ""
event1 = pygame.event.Event(pygame.USEREVENT, {"name" : 'initnumplayers', "error" : False})
pygame.event.post(event1)

while not done:
    screen.fill(background)
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            if event.__dict__["error"] == False:
                current_event = event.__dict__["name"]
                print(current_event)
        if event.type == pygame.QUIT:
            done = True
        
        for box in input_boxes:
            box.handle_event(event)
        for checkbox in checkboxes:
            checkbox.handle_event(event)
        main_text.handle_event(event)
        err_text.handle_event(event)
        submit_button.handle_event(event)

    for box in input_boxes:
        box.update()
    for box in input_boxes:
        box.draw(screen)
    
    for checkbox in checkboxes:
        checkbox.update()

    main_text.draw(screen)
    err_text.update()
    submit_button.update()

    pygame.display.flip()
    clock.tick(30)
