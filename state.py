from constants import F_TITLE, F_BIG, F_REGULAR, M_BUTTONDIMENSIONS, M_BUTTONSPACING, M_OFFSET, L_ESCAPE, G_FOV, P_ROTATIONSPEED
from pygame.locals import MOUSEMOTION, MOUSEBUTTONDOWN, K_TAB, K_LSHIFT, K_w, K_a, K_s, K_d, K_o, K_p, K_SPACE
import pygame
import graphic
import gui
import setting
import pack
import easygui
import world
import utility
import file
import editor

class StateManager(object):
    def __init__(self, defaultstate, states):
        '''
        Description
            Manages states.
        
        Parameters:
            defaultstate: The starting state (Integer)
            states: A list of states
        
        Notes:
            A state class needs to include these methods:
                enable(): Called when the state gains focus
                disable(newstate): Called when the state loses focus, the newstate is the state that is gaining focus afterwards
                update(surface, delta, events, keys, mousepos): Called every update in the main lo
                
        '''
        
        #Link all states to current state manager
        for state in states:
            state.manager = self
        
        self.states = states
        self.currentState = defaultstate
        self.lastState = defaultstate
        self.getCurrentState().enable()
    
    def getCurrentState(self):
        return self.states[self.currentState]
    
    def getState(self, name):
        for state in self.states:
            if state.name == name:
                return state
    
    def setState(self, name):
        for position, state in enumerate(self.states):
            if state.name == name:
                self.getCurrentState().disable(self.states[position])
                self.lastState, self.currentState = self.currentState, position
                self.getCurrentState().enable()
    
    def swapState(self):
        self.getCurrentState().disable(self.states[self.currentState])
        self.lastState, self.currentState = self.currentState, self.lastState
        self.getCurrentState().enable()
    
    def update(self, surface, delta, events, keys):
        self.getCurrentState().update(surface, delta, events, keys)

class Main(object):
    name = "Main"
    
    def __init__(self):
        self.level = world.Level("core/Menu.level")
        
        self.title = gui.AlignedLabel(F_TITLE, "Raycaster", True, (238, 238, 238), 1, (setting.resolution()[0] / 2, setting.resolution()[1] / 4), M_OFFSET)
        self.menu = gui.TextMenu(setting.resolution(), F_REGULAR, M_BUTTONDIMENSIONS, M_BUTTONSPACING, M_OFFSET,[
                            ("START GAME", (255, 193, 7), (255, 202, 40)),
                            ("EDITOR", (156, 39, 176), (171, 71, 188)),
                            ("SETTINGS", (76, 175, 80), (102, 187, 106)),
                            ("QUIT", (244, 67, 54), (239, 83, 80))
                            ])
        self.selected = ""
    
    def enable(self):
        #Check dimensions
        self.title.setLocation((setting.resolution()[0] / 2, setting.resolution()[1] / 4))
        self.menu.setDimensions(M_BUTTONDIMENSIONS, setting.resolution(), M_BUTTONSPACING, M_OFFSET)
    
    def disable(self, newstate=None):
        None
    
    def update(self, surface, delta, events, keys):
        #Slowly rotate and render the the menu level
        self.level.player.rotate(5 * delta)
        
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.selected == 0:
                    self.manager.setState("Selector")
                
                elif self.selected == 1:
                    self.manager.setState("Editor")
                
                elif self.selected == 2:
                    self.manager.setState("Settings")
                
                elif self.selected == 3:
                    utility.exitPygame(pygame)
            
            elif event.type == MOUSEMOTION:
                self.selected = self.menu.update(event.pos)
        
        
        
        graphic.render3D(surface, self.level, G_FOV, setting.renderquality())
        self.title.render(surface)
        self.menu.render(surface)

class Settings(object):
    name = "Settings"
    
    def __init__(self):        
        self.title = gui.AlignedLabel(F_TITLE, "Settings", True, (238, 238, 238), 1, (setting.resolution()[0] / 2, setting.resolution()[1] / 4), M_OFFSET)
        self.menu = gui.TextMenu(setting.resolution(), F_REGULAR, M_BUTTONDIMENSIONS, M_BUTTONSPACING, M_OFFSET,[
                            ("RESOLUTION: " + str(setting.resolution()), (76, 175, 80), (102, 187, 106)),
                            ("RENDER QUALITY: " + str(setting.renderquality()), (76, 175, 80), (102, 187, 106)),
                            ("BACK", (244, 67, 54), (239, 83, 80))
                            ])
        self.selected = ""
    
    def enable(self):
        self.level = self.manager.getState("Main").level
    
    def disable(self, newstate=None):
        None
    
    def update(self, surface, delta, events, keys):
        self.level.player.rotate(5 * delta)
        
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.selected is not None:
                if self.selected == 0:
                    setting.changeResolution()
                    
                    pygame.display.set_mode(setting.resolution())
                    
                    self.title.setLocation((setting.resolution()[0] / 2, setting.resolution()[1] / 4))
                    self.menu.setDimensions(M_BUTTONDIMENSIONS, setting.resolution(), M_BUTTONSPACING, M_OFFSET)
                    
                    self.menu.getButton(0).setText("RESOLUTION: " + str(setting.resolution()))
                
                elif self.selected == 1:
                    setting.changeRenderquality()
                    
                    self.menu.getButton(1).setText("RENDER QUALITY: " + str(setting.renderquality()))
                
                elif self.selected == 2:
                    self.manager.swapState()
            elif event.type == MOUSEMOTION:
                self.selected = self.menu.update(event.pos)
        
        graphic.render3D(surface, self.level, G_FOV, setting.renderquality())
        self.title.render(surface)
        self.menu.render(surface)

class Selector(object):
    name = "Selector"
    
    def __init__(self):
        self.title = gui.AlignedLabel(F_TITLE, "Level Select", True, (238, 238, 238), 1, (setting.resolution()[0] / 2, setting.resolution()[1] / 4), M_OFFSET)
        
        self.dictionaries = []
        
        #Scan for levels then add them as buttons
        buttons = []
        for fileName in file.listContents("levels/"):
            if fileName.split(".")[1] == "level":
                data = file.loadJson("levels/" + fileName)
                
                self.dictionaries += [(data['name'], data)]
                buttons += [(data['name'], (63, 81, 181), (92, 107, 192))]
        #Add a back butotn
        buttons += [("BACK", (244, 67, 54), (239, 83, 80))]
        
        self.menu = gui.TextMenu(setting.resolution(), F_REGULAR, M_BUTTONDIMENSIONS, M_BUTTONSPACING, M_OFFSET, buttons)
        self.levelSelected = None
        self.selected = ""
    
    def enable(self):
        self.title.setLocation((setting.resolution()[0] / 2, setting.resolution()[1] / 4))
        self.menu.setDimensions(M_BUTTONDIMENSIONS, setting.resolution(), M_BUTTONSPACING, M_OFFSET)
    
    def disable(self, newstate=None):
        #When this state is disabled, if the new state is play then load the current world
        if newstate.name == "Play":
            for dictionary in self.dictionaries:
                if dictionary[0] == self.levelSelected:
                    newstate.level = world.Level(dictionary[1])
                    break
                
    
    def update(self, surface, delta, events, keys):
        #Pausese if escape is clicked
        L_ESCAPE.update(keys)
        if L_ESCAPE.isClicked():
            self.manager.swapState()
            return
        
        surface.fill((13, 13, 13))
        
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.selected is not None:
                if self.selected == self.menu.getSize() - 1:
                    self.manager.swapState()
                else:
                    self.levelSelected = self.menu.getButton(self.selected).getText()
                    self.manager.setState("Play")
            elif event.type == MOUSEMOTION:
                self.selected = self.menu.update(event.pos)
        
        self.title.render(surface)
        self.menu.render(surface)

class Play(object):
    name = "Play"
    
    def __init__(self, level = None):
        self.level = level
        
        #Game variables
        self.player = file.loadImage("core/tex/player.png")
        self.bar = file.loadImage("core/ui/bar.png")
        self.health = file.loadImage("core/ui/health.png")
    
    def enable(self):
        #Hide and lock mouse to the window, center cursor
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.mouse.set_pos((setting.resolution()[0] / 2, setting.resolution()[1] / 2))
    
    def disable(self, newstate=None):
        #Show and unlock cursor from window
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        
        if newstate is not None and newstate.name == "Pause":
            snapshot = pygame.Surface(setting.resolution())
            graphic.render3D(snapshot, self.level, G_FOV, setting.renderquality())
            newstate.screen = snapshot
    
    def update(self, surface, delta, events, keys):
        mousepos = pygame.mouse.get_pos()
        
        #Pausese if escape is clicked
        L_ESCAPE.update(keys)
        if L_ESCAPE.isClicked():
            self.manager.setState("Pause")
            return
               
        currentSpeed = 0
        
        if keys[K_LSHIFT]:
            #Sets the current move speed to 6 (Sprint)
            currentSpeed = self.level.player.sprintspeed
        else:
            currentSpeed = self.level.player.speed
        
        if keys[K_w] and not keys[K_s]:
            #Moves the camera forward
            self.level.player.walk(currentSpeed * delta)
        if keys[K_s] and not keys[K_w]:
            #Moves the camera backward
            self.level.player.walk(-currentSpeed * delta)
        if keys[K_d] and not keys[K_a]:
            #Moves the camera right
            self.level.player.strafe(currentSpeed * delta)
        if keys[K_a] and not keys[K_d]:
            #Moves the camera left
            self.level.player.strafe(-currentSpeed * delta)
        
        if keys[K_o] and not keys[K_p]:
            #Rotates the camera left
            self.level.player.rotate(-P_ROTATIONSPEED * delta)
        if keys[K_p] and not keys[K_o]:
            #Rotates the camera right
            self.level.player.rotate(P_ROTATIONSPEED * delta)
        
        #Rotate camera based on the mouse distance from middle (Only uses X delta)
        self.level.player.rotate((mousepos[0] - setting.resolution()[0] / 2) * 0.1)
        
        #Moves the mouse to the middle of the window which resets the relative mouse movement
        pygame.mouse.set_pos((setting.resolution()[0] / 2, setting.resolution()[1] / 2))
        
        if keys[K_SPACE]:
            self.level.player.shoot(self.level)
        
        self.level.update(delta)
        
        #Renders raycast on display surface
        graphic.render3D(surface, self.level, G_FOV, setting.renderquality())
        graphic.renderHealth(surface, (5, surface.get_height() - 35, 106, 30), self.level, self.bar, self.health)
        
        #If tab is being pressed, render the 2d map
        if keys[K_TAB]:
            graphic.render2D(surface, tuple(map(lambda a: int((a / 2) - 176), setting.resolution())) + (352, 352), self.level, 0.5, self.player)

class Pause(object):
    name = "Pause"
    
    def __init__(self):
        self.screen = pygame.Surface(setting.resolution())
        
        self.title = gui.AlignedLabel(F_TITLE, "PAUSED", True, (238, 238, 238), 1, (setting.resolution()[0] / 2, setting.resolution()[1] / 4), M_OFFSET)
        self.menu = gui.TextMenu(setting.resolution(), F_REGULAR, M_BUTTONDIMENSIONS, M_BUTTONSPACING, M_OFFSET,[
                            ("RETURN", (63, 81, 181), (92, 107, 192)),
                            ("SETTINGS", (76, 175, 80), (102, 187, 106)),
                            ("MAIN MENU", (244, 67, 54), (239, 83, 80))
                            ])
        
        self.selected = ""
    
    def enable(self):
        self.title.setLocation((setting.resolution()[0] / 2, setting.resolution()[1] / 4))
        self.menu.setDimensions(M_BUTTONDIMENSIONS, setting.resolution(), M_BUTTONSPACING, M_OFFSET)
    
    def disable(self, newstate=None):
        pass
    
    def update(self, surface, delta, events, keys):
        #Gets current key presses
        L_ESCAPE.update(keys)
        if L_ESCAPE.isClicked():
            self.manager.setState("Play")
            return
        
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.selected == 0:
                    self.manager.setState("Play")
                
                elif self.selected == 1:
                    self.manager.setState("Settings")
                
                elif self.selected == 2:
                    self.manager.setState("Main")
            elif event.type == MOUSEMOTION:
                self.selected = self.menu.update(event.pos)
        
        surface.blit(pygame.transform.scale(self.screen, surface.get_rect().size), (0, 0))
        self.title.render(surface)
        self.menu.render(surface)

class Editor():
    name = "Editor"
    
    def __init__(self, path = None):
        if path is None:
            self.level = world.Level()
        else:
            self.level = world.Level(path)
        
        self.play = None
        self.mapeditorselected = False
        
        self.mapeditor = editor.MapEditor((0, 50, 530, 445), self.level)
        
        self.topbar = pygame.Rect(0, 0, 530, 50)
        self.back = gui.ImageButton("core/ui/back.png", (0, 0, 50, 50))
        self.namelabel = gui.AlignedLabel(F_BIG, self.level.name, True, (238, 238, 238), 0, (55, 25))
        self.packlabel = gui.AlignedLabel(F_REGULAR, self.level.pack.name, True, (238, 238, 238), 2, (477, 13))
        self.sizelabel = gui.AlignedLabel(F_REGULAR, str(self.level.getWidth()) + " x " + str(self.level.getHeight()), True, (238, 238, 238), 2, (477, 37))
        self.ceilingtile = pygame.Rect(482, 2, 46, 22)
        self.floortile = pygame.Rect(482, 26, 46, 22)
        
        self.sidebar = pygame.Rect(530, 0, 230, 530)
        self.packselector = editor.PackSelector((530, 0, 230, 420), F_REGULAR, self.level.pack, self.mapeditor)
        self.load = gui.TextButton(F_REGULAR, "Load", (156, 39, 176), (171, 71, 188), (535, 425, 110, 30))
        self.save = gui.TextButton(F_REGULAR, "Save", (156, 39, 176), (171, 71, 188), (645, 425, 110, 30))
        self.settings = gui.TextButton(F_REGULAR, "Settings", (156, 39, 176), (171, 71, 188), (535, 460, 220, 30))
        self.test = gui.TextButton(F_REGULAR, "Test", (156, 39, 176), (171, 71, 188), (535, 495, 220, 30))
        
        self.toolselector = editor.ToolSelector((0, 495, 530, 35), F_REGULAR, self.mapeditor)
        
        self.selected = ""
    
    def enable(self):
        pygame.display.set_mode((760, 530))
    
    def disable(self, newstate=None):
        pygame.display.set_mode(setting.resolution())
    
    def update(self, surface, delta, events, keys):
        L_ESCAPE.update(keys)
        if L_ESCAPE.isClicked():
            if self.play is not None:
                self.play.disable()
                self.play = None
                self.enable()
            else:
                self.manager.swapState()
            return
        
        if self.play is not None:
            self.play.update(surface, delta, events, keys)
            return
        
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.back.selected:
                    self.manager.swapState()
                
                elif self.brush is not None:
                    self.mapeditor.brush = self.brush
                    #Change tool if the current tool is unsuitable for selected tile
                    if self.brush[0] == 0 and self.mapeditor.tool != 0:
                        self.mapeditor.tool = 0
                    elif self.brush[0] != 0 and self.mapeditor.tool != 2:
                        self.mapeditor.tool = 2
                
                elif self.tool is not None:
                    self.mapeditor.tool = self.tool
                    if self.tool <= 1 and self.mapeditor.brush[0] != 0:
                        self.mapeditor.brush = (0, 1)
                    elif self.tool >= 2 and self.mapeditor.brush[0] == 0:
                        self.mapeditor.brush = (1, 1)
                
                elif self.load.selected:
                    path = easygui.fileopenbox("Choose which level to load", "Load level", file.fullPath("levels") + "\\*.level")
                    
                    if path is not None and path is not '.':
                        self.__init__(path)
                
                elif self.save.selected:
                    path = easygui.filesavebox("Choose where to save your level", "Save level", file.fullPath("levels") + "\\" + self.level.name + ".level")
                    
                    if path is not None:
                        self.level.save(path)
                
                elif self.settings.selected:
                    while True:
                        setting = easygui.buttonbox("Select the setting to change.", "Change settings", ("Name", "Size", "Ceiling Colour", "Floor Colour", "Outer Wall", "Pack", "Done"))
                        
                        if setting == "Name":
                            name = easygui.enterbox("Enter a level name:", "Change Name", self.level.name)
                            
                            if name is not None:
                                self.level.name  = name
                                self.namelabel.setText(self.level.name)
                        
                        elif setting == "Size":
                            width = easygui.integerbox("Enter a level width [2-100]:", "Change size", self.level.getWidth(), 2, 100)
                            if width is not None:
                                height = easygui.integerbox("Enter a level height [2-100]:", "Change size", self.level.getHeight(), 2, 100)
                            else:
                                height = None
                            
                            if not None in (width, height):
                                self.level.changeSize(width, height)
                                self.sizelabel.setText(str(width) + " x " + str(height))
                                self.mapeditor.x = width / 2
                                self.mapeditor.y = height / 2
                        
                        elif setting == "Ceiling Colour":
                            r = easygui.integerbox("Enter Red Value (RGB Colour) [0-255]:", "Change Ceiling Colour", self.level.ceilingcolor[0], 0, 255)
                            if r is not None:
                                g = easygui.integerbox("Enter Green Value (RGB Colour) [0-255]:", "Change Ceiling Colour", self.level.ceilingcolor[1], 0, 255)
                                if g is not None:
                                    b = easygui.integerbox("Enter Blue Value (RGB Colour) [0-255]:", "Change Ceiling Colour", self.level.ceilingcolor[2], 0, 255)
                                else:
                                    b = None
                            else:
                                b = None
                                g = None
                            
                            if not None in (r, g, b):
                                self.level.ceilingcolor = (r, g, b)
                        
                        elif setting == "Floor Colour":
                            r = easygui.integerbox("Enter Red Value (RGB Colour) [0-255]:", "Change Floor Colour", self.level.floorcolor[0], 0, 255)
                            if r is not None:
                                g = easygui.integerbox("Enter Green Value (RGB Colour) [0-255]:", "Change Floor Colour", self.level.floorcolor[1], 0, 255)
                                if g is not None:
                                    b = easygui.integerbox("Enter Blue Value (RGB Colour) [0-255]:", "Change Floor Colour", self.level.floorcolor[2], 0, 255)
                                else:
                                    b = None
                            else:
                                b = None
                                g = None
                            
                            if not None in (r, g, b):
                                self.level.floorcolor = (r, g, b)
                        
                        elif setting == "Outer Wall":
                            outerwall = easygui.integerbox("Enter the outer wall tile position:", "Change Outer Wall", self.level.outerwall, 1, len(self.level.pack.wall))
                            
                            if outerwall is not None:
                                self.level.outerwall = outerwall
                        
                        elif setting == "Pack":
                            packname = easygui.choicebox("Select a pack from the list below.\nIf you want to install a new pack, move it into the \"pack\" folder next to the executable.", "Change pack", pack.listPacks())
                            
                            if packname is not None:
                                self.level.pack = pack.Pack(packname)
                                self.packselector.setPack(self.level.pack)
                                self.packlabel.setText(self.level.pack.name)
                        
                        elif setting == "Done" or setting is None:
                            break
                    
                    pygame.event.clear()
                
                elif self.test.selected:
                    self.disable()
                    self.play = Play(self.level.copy())
                    self.play.enable()
                
            elif event.type == MOUSEBUTTONDOWN:
                if self.mapeditor.rect.collidepoint(event.pos):
                    if event.button == 2:
                        self.mapeditor.tool = (self.mapeditor.tool + 1) % 6
                    elif event.button == 4:
                        self.mapeditor.zoom(0.05)
                    elif event.button == 5:
                        self.mapeditor.zoom(-0.05)
                elif self.packselector.rect.collidepoint(event.pos):
                    if event.button == 4:
                        self.packselector.scroll(5)
                    elif event.button == 5:
                        self.packselector.scroll(-5)
            
            elif event.type == MOUSEMOTION:
                self.back.update(event.pos)
                self.load.update(event.pos)
                self.save.update(event.pos)
                self.settings.update(event.pos)
                self.test.update(event.pos)
                self.mapeditor.update(event.pos, event.buttons)
                self.brush = self.packselector.update(event.pos)
                self.tool = self.toolselector.update(event.pos)
        
        pygame.draw.rect(surface, (33, 33, 33), self.topbar)
        pygame.draw.rect(surface, (238, 238, 238), self.sidebar)
        
        self.back.render(surface)
        self.namelabel.render(surface)
        self.packlabel.render(surface)
        self.sizelabel.render(surface)
        
        pygame.draw.rect(surface, self.level.ceilingcolor, self.ceilingtile)
        pygame.draw.rect(surface, self.level.floorcolor, self.floortile)
        
        self.load.render(surface)
        self.save.render(surface)
        self.settings.render(surface)
        self.test.render(surface)
        
        self.packselector.render(surface)
        self.toolselector.render(surface)
        self.mapeditor.render(surface)