'''
Author: Kyle Charters

Description:
    The editor module contains gui elements for a map editor

Contents:
    - Pack Selector
    - Tool Selector
    - Map editor

Notes:
    All of the elements are composed of the gui module contents
    
    These standards are used throughout all 3 classes
    
    Tools:
        0 = Wall Pencil
        1 = Wall Eraser
        2 = Sprite Pencil
        3 = Sprite Eraser
        4 = Sprite Mover
        5 = Sprite Menu
    
    Brush tuple (Variation, Tile):
        Variation:
            0 = Walls
            1 = Statics
            2 = Items
            3 = Enemies
        Tile:
            The tile location inside current pack
'''

from constants import G_TEXDIM
import pygame
import easygui
import math
import gui
import world
import file
import utility

class PackSelector(object):
    def __init__(self, rect, font, pack, mapeditor):
        '''
        Description:
            A pack selector analyzes a pack and creates a list of menus based on the walls and sprites
        
        Parameters:
            rect: The viewport rectangle, (x, y, width, height)
            font: The font that should be used by section titles
            pack: The pack that is displayed in menus
            mapeditor: The map editor that the tool selector is linked to
        
        Notes:
            Supports scrolling as long as the menus height is larger than the pack selector viewport
            
            The categories are:
                - Walls
                - Statics
                - Items
                - Enemies
        '''
        
        self.rect = pygame.Rect(rect)
        self.font = font
        self.setPack(pack)
        self.mapeditor = mapeditor
    
    def setPack(self, pack):
        '''
        Description:
            Sets the pack selectors current pack
        
        Parameters:
            pack: The pack that is displayed in menus
        
        Notes:
            Resets height and offset
        '''
        
        #Initialize all text and menu variables
        self.wallstext = None
        self.wallsmenu = None
        self.staticstext = None
        self.staticsmenu = None
        self.itemstext = None
        self.itemsmenu = None
        self.enemiestext = None
        self.enemiesmenu = None
        
        self._wallsloaded = False
        self._staticsloaded = False
        self._itemsloaded = False
        self._enemiesloaded = False
        
        y = 10
        #Check to see if there are any walls in the current pack
        if len(pack.wall) != 0:
            #Create wall text and menu
            self.wallstext = gui.AlignedLabel(self.font, "WALLS:", True, (13, 13, 13), 0, (5, y))
            y += 10
            self.wallsmenu = gui.ImageMenu((0, y, self.rect.width, 0), 48, 4, pack.wall)
            y += self.wallsmenu.rect.height + 10
            self._wallsloaded = True
        
        #Check to see if there are any statics in the current pack
        if len(pack.sprite[0]) != 0:
            #Create statics text and menu
            self.staticstext = gui.AlignedLabel(self.font, "STATICS:", True, (13, 13, 13), 0, (5, y))
            y += 10
            self.staticsmenu = gui.ImageMenu((0, y, self.rect.width, 0), 48, 4, pack.sprite[0])
            y += self.staticsmenu.rect.height + 10
            self._staticsloaded = True
        
        #Check to see if there are any items in the current pack
        if len(pack.sprite[1]) != 0:
            #Create items text and menu
            self.itemstext = gui.AlignedLabel(self.font, "ITEMS:", True, (13, 13, 13), 0, (5, y))
            y += 10
            self.itemsmenu = gui.ImageMenu((0, y, self.rect.width, 0), 48, 4, pack.sprite[1])
            y += self.itemsmenu.rect.height + 10
            self._itemsloaded = True
        
        #Check to see if there are any enemies in the current pack
        if len(pack.sprite[2]) != 0:
            #Create enemies text and menu
            self.enemiestext = gui.AlignedLabel(self.font, "ENEMIES:", True, (13, 13, 13), 0, (5, y))
            y += 10
            self.enemiesmenu = gui.ImageMenu((0, y, self.rect.width, 0), 48, 4, pack.sprite[2])
            y += self.enemiesmenu.rect.height + 10
            self._enemiesloaded = True
        
        self.height = y
        self.offset = 0
    
    def scroll(self, amount):
        '''
        Description:
            Moves the menus up and down
        
        Parameters:
            amount: The distance to scroll
        
        Notes:
            Scrolling does not work if the height of all the menus is less than the viewport height
        '''
        
        #Scrolling cannot move past the top of the first menu or the bottom of the last
        if self.height > self.rect.height and self.rect.height - self.height <= self.offset + amount <= 0:
            self.offset += amount
            #Move loaded menus by specified amount
            if self._wallsloaded:
                self.wallsmenu.scroll(amount)
                self.wallstext.setLocation((self.wallstext.location[0], self.wallstext.location[1] + amount))
            if self._staticsloaded:
                self.staticsmenu.scroll(amount)
                self.staticstext.setLocation((self.staticstext.location[0], self.staticstext.location[1] + amount))
            if self._itemsloaded:
                self.itemsmenu.scroll(amount)
                self.itemstext.setLocation((self.staticstext.location[0], self.staticstext.location[1] + amount))
            if self._enemiesloaded:
                self.enemiesmenu.scroll(amount)
                self.enemiestext.setLocation((self.staticstext.location[0], self.staticstext.location[1] + amount))
    
    def update(self, mousepos):
        '''
        Description:
            Updates all menus
        
        Parameters:
            mousepos: The mouse position inside the window
        
        Returns:
            The selected variation and tile (Variation, Tile)
               
        Notes:
            None
        '''
        
        #Find mouse position in relation to the top left of viewport
        mouseposrel = (mousepos[0] - self.rect.left, mousepos[1] - self.rect.top)
        
        #Update each menu if it is loaded
        wallselected = None
        if self._wallsloaded:
            wallselected = self.wallsmenu.update(mouseposrel)
        
        staticselected = None
        if self._staticsloaded:
            staticselected = self.staticsmenu.update(mouseposrel)
        
        itemselected = None
        if self._itemsloaded:
            itemselected = self.itemsmenu.update(mouseposrel)
        
        enemyselected = None
        if self._enemiesloaded:
            enemyselected = self.enemiesmenu.update(mouseposrel)
        
        if wallselected is not None:
            return (0, wallselected + 1)
        elif staticselected is not None:
            return (1, staticselected + 1)
        elif itemselected is not None:
            return (2, itemselected + 1)
        elif enemyselected is not None:
            return (3, enemyselected + 1)
        else:
            return None
    
    
    def render(self, surface):
        '''
        Description:
            Draws all menus
        
        Parameters:
            surface: The surface to render to
               
        Notes:
            None
        '''
        
        #Create base surface for temporary rendering
        image = pygame.Surface(self.rect.size)
        image.fill((255, 255, 255))
        image.set_colorkey((255, 255, 255))
        
        #Load all buttons into an array for iteration
        buttons = [None, None, None, None]
        if self._wallsloaded:
            buttons[0] = self.wallsmenu.buttons
        if self._staticsloaded:
            buttons[1] = self.staticsmenu.buttons
        if self._itemsloaded:
            buttons[2] = self.itemsmenu.buttons
        if self._enemiesloaded:
            buttons[3] = self.enemiesmenu.buttons
        
        for variation, items in enumerate(buttons):
            if items is None:
                continue
            
            for position, button in enumerate(items):
                #If the current button is the currently selected tile, draw a coloured border instead of black
                if self.mapeditor.brush == (variation, position + 1):
                    if variation > 0:
                        color = (0, 188, 212)
                    else:
                        color = (255, 152, 0)
                else:
                    color = (0, 0, 0)
                
                pygame.draw.rect(image, color, button.rect.inflate(4, 4))
        
        #Update each menu if it is loaded
        if self._wallsloaded:
            self.wallstext.render(image)
            self.wallsmenu.render(image)
        
        if self._staticsloaded:
            self.staticstext.render(image)
            self.staticsmenu.render(image)
        
        if self._itemsloaded:
            self.itemstext.render(image)
            self.itemsmenu.render(image)
        
        if self._enemiesloaded:
            self.enemiestext.render(image)
            self.enemiesmenu.render(image)
        
        #Render the view to the screen
        surface.blit(image, self.rect.topleft)

class ToolSelector(object):
    def __init__(self, rect, font, mapeditor):
        '''
        Description:
            Creates 6 different tool buttons and section titles.
        
        Parameters:
            rect: The viewport rectangle, (x, y, width, height)
            font: The font that should be used by section titles
            mapeditor: The map editor that the tool selector is linked to
        
        Notes:
            The selectable tools are:
                - Wall Pencil
                - Wall Eraser
                - Sprite Pencil
                - Sprite Eraser
                - Sprite Mover
                - Sprite Menu
        '''
        
        self.rect = pygame.Rect(rect)
        self.mapeditor = mapeditor
        
        self.wallpencil = gui.ImageButton("core/ui/wallpencil.png", (self.rect.left + 5, self.rect.bottom - 30, 25, 25))
        self.walleraser = gui.ImageButton("core/ui/walleraser.png", (self.rect.left + 35, self.rect.bottom - 30, 25, 25))
        self.walltext = gui.AlignedLabel(font, "WALL", True, (0, 0, 0), 0, (self.rect.left + 65, self.rect.top + 17))
        
        self.spritepencil = gui.ImageButton("core/ui/spritepencil.png", (self.rect.right - 30, self.rect.bottom - 30, 25, 25))
        self.spriteeraser = gui.ImageButton("core/ui/spriteeraser.png", (self.rect.right - 60, self.rect.bottom - 30, 25, 25))
        self.spritemover = gui.ImageButton("core/ui/spritemover.png", (self.rect.right - 90, self.rect.bottom - 30, 25, 25))
        self.spritemenu = gui.ImageButton("core/ui/spritemenu.png", (self.rect.right - 120, self.rect.bottom - 30, 25, 25))
        self.spritetext = gui.AlignedLabel(font, "SPRITES", True, (0, 0, 0), 2, (self.rect.right - 125, self.rect.top + 17))
        
    def update(self, mousepos):
        '''
        Description:
            Draws buttons and text onto the screen
        
        Parameters:
            mousepos: The mouse position inside the window
        
        Returns:
            The tool value
        
        Notes:
            None
        '''
        
        #Update all buttons
        
        selected = None
        
        if self.wallpencil.update(mousepos):
            selected = 0
        elif self.walleraser.update(mousepos):
            selected = 1
        elif self.spritepencil.update(mousepos):
            selected = 2
        elif self.spriteeraser.update(mousepos):
            selected = 3
        elif self.spritemover.update(mousepos):
            selected = 4
        elif self.spritemenu.update(mousepos):
            selected = 5
        
        return selected
    
    def render(self, surface):
        '''
        Description:
            Draws buttons and text onto the screen
        
        Parameters:
            surface: The surface to render to
        
        Returns:
            The tool value
        
        Notes:
            None
        '''
        pygame.draw.rect(surface, (156, 39, 176), self.rect)
        self.walltext.render(surface)
        self.spritetext.render(surface)
        
        #Render a border around currently selected tool
        if self.mapeditor.tool == 0:
            color = (255, 193, 7)
            rect = self.wallpencil.rect
        elif self.mapeditor.tool == 1:
            color = (255, 193, 7)
            rect = self.walleraser.rect
        elif self.mapeditor.tool == 2:
            color = (0, 188, 212)
            rect = self.spritepencil.rect
        elif self.mapeditor.tool == 3:
            color = (0, 188, 212)
            rect = self.spriteeraser.rect
        elif self.mapeditor.tool == 4:
            color = (0, 188, 212)
            rect = self.spritemover.rect
        elif self.mapeditor.tool == 5:
            color = (0, 188, 212)
            rect = self.spritemenu.rect
        else:
            rect = None
        
        if rect is not None:
            pygame.draw.rect(surface, color, rect.inflate(4, 4))
        
        self.wallpencil.render(surface)
        self.walleraser.render(surface)
        self.spritepencil.render(surface)
        self.spriteeraser.render(surface)
        self.spritemover.render(surface)
        self.spritemenu.render(surface)
        

class MapEditor(object):
    def __init__(self, rect, level):
        '''
        Description:
            The map editor draws a grid, walls and sprites in a 2d top-view perspective
            it also allows the user to pan, zoom, as well as act on map information using the specified tool
        
        Parameters:
            rect: The viewport rectangle, (x, y, width, height)
            level: The object that the map editor modifies
            
        Notes:
            The camera has a 2d position, and a zoom scalar
        '''
        
        self.rect = pygame.Rect(rect)
        self.setLevel(level)
        
        #Camera variables
        self.middlex = self.rect.width / 2
        self.middley = self.rect.height / 2
        
        self.playertexture = file.loadImage("core/tex/player.png")
        
        #Variable that turns true when user is right clicking
        self.grab = False
        
        #Editing variables
        self.tool = 0
        self.brush = (0, 1)
        self.selected = None
    
    def setLevel(self, level):
        '''
        Description:
            Sets the level that the map editor modifies
        
        Parameters:
            level: The new level object
        
        Notes:
            Resets camera
        '''
        
        self.level = level
        
        self.x = self.level.getWidth() / 2
        self.y = self.level.getHeight() / 2
        self.scale = 1
        self.tilesize = int(G_TEXDIM * self.scale)
    
    def zoom(self, amount):
        '''
        Description:
            Zooms the camera in
        
        Parameters:
            amount: The amount to zoom the camera in
        
        Notes:
            A scale of 1 means a tilesize the same as the texture dimension
        '''
        
        self.scale = max(0.1, min(2, self.scale + amount))
        self.tilesize = int(G_TEXDIM * self.scale)
    
    def pan(self, movement):
        '''
        Description:
            Pans the camera based on movement
        
        Parameters:
            movement: The distance to move the camera
        
        Notes:
            The camera cannot move outside of map
        '''
        
        self.x = max(0, min(self.level.getWidth(), self.x - movement[0] / self.tilesize))
        self.y = max(0, min(self.level.getHeight(), self.y - movement[1] / self.tilesize))
    
    def act(self, mousepos, painting):
        '''
        Description:
            Modifies the level based on current tool
        
        Parameters:
            mousepos: The mouse position inside the window
            painting: Only modifies the world if this is true
        
        Notes:
            Finds mouse cursor location in world space, this compensates for the viewport location, camera location and tile size
            If cursor is inside map and mouse is being pressed, paint based on the current tool
        '''
        
        #Find world x and y positions
        x = (mousepos[0] - self.rect.left - self.middlex) / self.tilesize + self.x
        y = (mousepos[1] - self.rect.top - self.middley) / self.tilesize + self.y
        xfloor = math.floor(x)
        yfloor = math.floor(y)
        
        if 0 <= x <= self.level.getWidth() and 0 <= y  <= self.level.getHeight() and painting:
            #Add a wall to the map
            if self.tool == 0:
                
                if self.brush[0] == 0:
                    #Push entities out of the way if they are occupying the same space
                    for entity in self.level.getEntities():
                        if entity.collideAABB(x + 0.5, y + 0.5, 1):
                            #Math magic for finding which axis we have to move the least
                            if abs((entity.x % 1) - 0.5) > abs((entity.y % 1) - 0.5):
                                entity.x = round(entity.x)
                            else:
                                entity.y = round(entity.y)
                    self.level.setElement(xfloor, yfloor, self.brush[1])
            
            #Erase a wall from the map
            elif self.tool == 1:
                self.level.setElement(xfloor, yfloor, 0)
            
            #Add a entity to the map
            elif self.tool == 2:
                if self.brush[0] != 0:
                    if self.level.getEntity(x, y, -1, 0.8) is None and self.level.getElement(xfloor, yfloor) == 0:
                        if self.brush[0] == 1:
                            self.level.addEntity(world.Static(x, y, self.brush[1]))
                        elif self.brush[0] == 2:
                            self.level.addEntity(world.Item(x, y, self.brush[1], 0))
                        elif self.brush[0] == 3:
                            self.level.addEntity(world.Enemy(x, y, 0, self.brush[1], 4, 50, 0.5, 4, 5, 1))
            
            #Erase a entity from the map
            elif self.tool == 3:
                self.level.removeEntity(self.level.getEntity(x, y, -1, 0.4))
            
            #Move an existing entity in map
            elif self.tool == 4:
                if self.selected is not None:
                    self.selected.move(x - self.selected.x, y - self.selected.y, legdist=0, fast=False, independent=False)
                else:
                    self.selected = self.level.getEntity(x, y, -1, 0.4)
            
            #Edit an existing entity's properities
            elif self.tool == 5:
                entity = self.level.getEntity(x, y, -1)
                if entity is not None:
                    if entity.variation is -1 or entity.variation is 2:
                        direction = easygui.integerbox("Enter Direction: ", "Edit entity", entity.direction, 0, 360)
                        if direction is not None:
                            entity.direction = direction
                        else:
                            return
                        
                        speed = easygui.integerbox("Enter speed: ", "Edit entity", entity.speed, 0, 20)
                        if speed is not None:
                            entity.speed = speed
                        else:
                            return
                        
                        if entity.variation is -1:
                            sprint = easygui.integerbox("Enter sprint speed: ", "Edit entity", entity.sprintspeed, 0, 30)
                            if sprint is not None:
                                entity.sprint = sprint
                        else:
                            return
                        
                        health = easygui.integerbox("Enter health: ", "Edit entity", entity.health, 1, 1000)
                        if health is not None:
                            entity.health = health
                        else:
                            return
                        
                        if entity.variation is -1:
                            regen = easygui.integerbox("Enter health regeneration / second: ", "Edit entity", entity.regen, 0, 10)
                            if regen is not None:
                                entity.regen = regen
                        else:
                            return
                        
                        cooldown = easygui.integerbox("Enter projectile cooldown (miliseconds): ", "Edit entity", entity.cooldown * 1000, 1, 1000)
                        if cooldown is not None:
                            #Convert milliseconds to seconds
                            entity.cooldown = cooldown / 1000
                        else:
                            return
                        
                        projectilespeed = easygui.integerbox("Enter projectile speed: ", "Edit entity", entity.projectilespeed, 1, 30)
                        if projectilespeed is not None:
                            entity.projectilespeed = projectilespeed
                        else:
                            return
                        
                        projectiledamage = easygui.integerbox("Enter projectile damage: ", "Edit entity", entity.projectiledamage, 0, 1000)
                        if projectiledamage is not None:
                            entity.projectiledamage = projectiledamage
                        else:
                            return
                        
                        projectiletexture = easygui.integerbox("Enter projectile texture: ", "Edit entity", entity.projectiletexture, 1, len(self.level.pack.sprite[3]))
                        if projectiletexture is not None:
                            entity.projectiletexture = projectiletexture
                        else:
                            return
                    elif entity.variation == 1:
                        function = easygui.integerbox("Enter item function (0 is victory, 1 is healthpack): ", "Edit entity", entity.function, 0, 1)
                        if function is not None:
                            entity.function = function
                        else:
                            return
                        
        elif self.selected is not None:
            self.selected = None
    
    def update(self, mousepos, mousepress):
        '''
        Description:
            Also updates input
        
        Parameters:
            mousepos: The mouse position inside the window
            mousepress: A tuple of 3 that contains mouse button states
        
        Notes:
            None
        '''
        
        selected = self.rect.collidepoint(mousepos)
        
        #Right click movement
        if selected and mousepress[2]:
            self.pan(pygame.mouse.get_rel())
        else:
            #Must update mouse relation anyways to prevent click movement
            pygame.mouse.get_rel()
        
        #Left click painting
        if selected:
            self.act(mousepos, mousepress[0])
    
    def render(self, surface):
        '''
        Description:
            Draws grid, tiles, sprites and player inside map editor viewport
        
        Parameters:
            surface: The surface to render to
        
        Notes:
            None
        '''
        image = pygame.Surface(self.rect.size)
        image.fill(self.level.floorcolor)
        
        width = self.level.getWidth()
        height = self.level.getHeight()
        
        #Render grid lines along the x-axis
        for row in range(height + 1):
            y = (row - self.y) * self.tilesize + self.middley
            xstart = -self.x * self.tilesize + self.middlex
            xend = (width - self.x) * self.tilesize + self.middlex
            pygame.draw.line(image, (0, 0, 0), (xstart, y), (xend, y), 1)
        
        #Render grid lines along the y-axis
        for col in range(width + 1):
            x = (col - self.x) * self.tilesize + self.middlex
            ystart = -self.y * self.tilesize + self.middley
            yend = (height - self.y) * self.tilesize + self.middley
            pygame.draw.line(image, (0, 0, 0), (x, ystart), (x, yend), 1)
        
        #Render tiles on top of grid
        for rowposition, row in enumerate(self.level.map):
            for colposition, tile in enumerate(row):
                if tile != 0:
                    x = (colposition - self.x) * self.tilesize + self.middlex + 1
                    y = (rowposition - self.y) * self.tilesize + self.middley + 1                    
                    image.blit(pygame.transform.scale(self.level.pack.getWall(tile), [self.tilesize - 1] * 2), (x, y))
        
        #Render entities
        for entity in self.level.statics + self.level.items + self.level.enemies:
            #Find location of sprite as well as texture
            texture = utility.aspect(self.level.pack.getSprite(entity.variation, entity.texture), (int(self.tilesize / 2), int(self.tilesize / 2)))
            x = int((entity.x - self.x) * self.tilesize + self.middlex - int(texture.get_width() / 2))
            y = int((entity.y - self.y) * self.tilesize + self.middley - int(texture.get_height() / 2))
            
            #Render a line for direction if the entity is an enemy
            if entity.variation is 2:
                #Find the middle of the sprite
                linestartx = x + (self.tilesize / 4)
                linestarty = y + (self.tilesize / 4)
                #Line is the size half a tile in the enemy's direction
                lineendx = linestartx + (math.cos(math.radians(-entity.direction)) * (self.tilesize / 2))
                lineendy = linestarty + (math.sin(math.radians(-entity.direction)) * (self.tilesize / 2))
                pygame.draw.line(image, (255, 0, 0), (linestartx, linestarty), (lineendx, lineendy), 2)
            
            image.blit(texture, (x, y))
        
        #Render rotated player
        x = int((self.level.player.x - self.x) * self.tilesize + self.middlex)
        y = int((self.level.player.y - self.y) * self.tilesize + self.middley)
        image.blit(pygame.transform.rotozoom(self.playertexture, -self.level.player.direction, self.scale), (x - 25 * self.scale, y - 25 * self.scale))
        
        #Render view on surface
        surface.blit(image, self.rect.topleft)
        