'''
Author: Kyle Charters

Description:
    The gui module contains graphical user interface utilities

Contents:
    - Label
    - AlignedLabel
    - Button
    - TextButton
    - ImageButton
    - TextMenu
    - ImageMenu

Notes:
    None
'''

import pygame
import file
import utility

class Label(object):
    def __init__(self, font, text, antialias, color, location):
        '''
        Description:
            This gui element holds text
        
        Parameters:
            font: The text's font
            text: The text to display
            antialias: Whether or not to use antialiasing on the text
            color: The color of the text
            location: The location of the text
        
        Notes:
            This is essentially a class based wrapper for the pygame font.render method
        '''
        
        self.font = font
        self.text = text
        self.antialias = antialias
        self.color = color
        self.location = location
        self.label = font.render(text, antialias, color)
    
    def width(self):
        return self.label.get_width()
    
    def height(self):
        return self.label.get_height()
    
    def setLocation(self, location):
        self.location = location
    
    def setText(self, text):
        self.text = text
        self.label = self.font.render(text, self.antialias, self.color)
    
    def setAntialias(self, antialias):
        self.antialias = antialias
        self.label = self.font.render(self.text, antialias, self.color)
    
    def setColor(self, color):
        self.color = color
        self.label = self.font.render(self.text, self.antialias, color)
    
    def render(self, surface):
        surface.blit(self.label, self.location)

class AlignedLabel(Label):
    def __init__(self, font, text, antialias, color, alignment, location, yoffset=0, xoffset=0):
        '''
        Description:
            This gui element holds text, and supports different alignments from the point
        
        Parameters:
            font: The text's font
            text: The text to display
            antialias: Whether or not to use antialiasing on the text
            color: The color of the text
            alignment: The alignment of the text
            location: The location of the text
            yoffset: The offset of location on the y-axis
            xoffset: The offset of location on the x-axis
        
        Notes:
            This class extends Label
            
            Alignment from point:
                0 = Text on right
                1 = Text in middle
                2 = Text on left
        '''
        
        super().__init__(font, text, antialias, color, location)
        self.yoffset = yoffset
        self.xoffset = xoffset
        self.setAlignment(alignment)
    
    def setText(self, text):
        super().setText(text)
        self.setAlignment(self.alignment)
    
    def setLocation(self, location):
        super().setLocation(location)
        self.setAlignment(self.alignment)
    
    def setAlignment(self, alignment):
        self.alignment = alignment
        
        self.xlocation = self.location[0]
        self.ylocation = self.location[1] - (self.label.get_height() / 2) + self.yoffset
        
        if self.alignment == 0:
            self.xlocation += self.xoffset
        elif self.alignment == 1:
            self.xlocation -= (self.label.get_width() / 2) - self.xoffset
        elif self.alignment == 2:
            self.xlocation -= self.label.get_width() - self.xoffset
    
    def render(self, surface):
        surface.blit(self.label, (self.xlocation, self.ylocation))

class Button(object):
    def __init__(self, rect):
        '''
        Description:
            This gui element detects mouse collision in a specified area
        
        Parameters:
            rect: The rectangle that the button occupies
        
        Notes:
            This class does not render anything
        '''
        
        self.rect = pygame.Rect(rect)
        self.selected = False
    
    def setLocation(self, x, y):
        self.rect.x = x
        self.rect.y = y
    
    def move(self, x, y):
        self.rect = self.rect.move(x, y)
    
    def setDimension(self, width, height):
        self.rect.width = width
        self.rect.height = height
    
    def update(self, mousepos):
        self.selected = self.rect.collidepoint(mousepos)
        return self.selected

class TextButton(Button):
    def __init__(self, font, text, color, highlightcolor, rect):
        '''
        Description:
            This gui element detects mouse collision in a specified area, and renders a solid rectangle with text in the middle
        
        Parameters:
            font: The text's font
            text: The text to display
            color: The color of the button
            highlightccolor: The color of the button when the mouse collides with the rectangle
            rect: The rectangle that the button occupies
        
        Notes:
            None
        '''
        
        super().__init__(rect)
        
        self.label = AlignedLabel(font, text, True, (0, 0, 0), 1, self.rect.center)
        self.color = color
        self.highlightcolor = highlightcolor
    
    def getText(self):
        return self.label.text
    
    def setText(self, text):
        self.label.setText(text)
    
    def setCol(self, color, highlightcolor):
        self.color = color
        self.highlightcolor = highlightcolor
    
    def setLocation(self, x, y):
        super().setLocation(x, y)
        self.label.setLocation(self.rect.center)
    
    def move(self, x, y):
        super().move(x, y)
        self.label.setLocation(self.rect.center)
    
    def setDimension(self, dimension):
        super().setDimension(dimension)
        self.label.setDimension(self.rect.center)
    
    def render(self, surface):
        if self.selected:
            pygame.draw.rect(surface, self.highlightcolor, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
        
        self.label.render(surface)

class ImageButton(Button):
    def __init__(self, image, rect):
        '''
        Description:
            This gui element detects mouse collision in a specified area, and renders an image
        
        Parameters:
            image: The image to display
            rect: The rectangle that the button occupies
        
        Notes:
            None
        '''
        
        super().__init__(rect)
        
        self.setImage(image)
        
        #Creates a blank white texture with a transparency of 80
        self.selection = pygame.Surface(self.rect.size)
        self.selection.set_alpha(80)
        self.selection.fill((255, 255, 255))
    
    def setImage(self, image):
        #Image value can either be string or already loaded image
        if isinstance(image, str):
            self.image = file.loadImage(image)
        else:
            self.image = image
        
        self.image = utility.aspect(self.image, self.rect.size)
    
    def setDimension(self, dimension):
        super().setDimension(self, dimension)
        self.image = utility.aspect(self.image, self.rect.size)
    
    def render(self, surface):
        surface.blit(self.image, self.rect.topleft)
        
        if self.selected:
            surface.blit(self.selection, self.rect.topleft)

class TextMenu(object):
    def __init__(self, parentdim, font, buttondim, spacing, offset, buttons):
        '''
        Description:
            This gui element creates a list of buttons from the center of the parent dimension and down
        
        Parameters:
            parentdim: The dimensions of the parent
            font: The text's font
            buttondim: The dimensions of the buttons
            spacing: The distance between buttons
            offset: The vertical offset
            buttons: A list of 3 element tuples that make up the buttons
        
        Notes:
            The 3 element button tuples are:
                (Text, Color, HighlightColor)
        '''
        
        self.buttons = []
        
        for position, button in enumerate(buttons):
            self.buttons.append(TextButton(font, button[0], button[1], button[2],
                                       ((parentdim[0] / 2) - (buttondim[0] / 2),
                                       (parentdim[1] / 2) + ((buttondim[1] + spacing) * position) + offset,
                                       buttondim[0], buttondim[1])))
    
    def setDimensions(self, buttondim, parentdim, spacing, offset):
        for position in range(len(self.buttons)):
            self.getButton(position).setLocation(
                                    (parentdim[0] / 2) - (buttondim[0] / 2),
                                    (parentdim[1] / 2) + ((buttondim[1] + spacing) * position) + offset)
    
    def scroll(self, amount):
        for button in self.buttons:
            button.move(0, amount)
    
    def getButton(self, pos):
        return self.buttons[pos]
    
    def getSize(self):
        return len(self.buttons)
    
    def update(self, mousepos):
        result = None
        
        for position, button in enumerate(self.buttons):
            if button.update(mousepos):
                result = position
        
        return result
    
    def render(self, surface):
        for button in self.buttons:
            button.render(surface)

class ImageMenu(object):
    def __init__(self, parentrect, buttondim, columns, images):
        '''
        Description:
            This gui element creates a list of buttons from the center of the parent dimension and down
        
        Parameters:
            parentrect: The dimensions of the parent
            buttondim: The dimensions of the buttons
            columns: The amount of columns inside teh menu
            buttons: A list of images / strings
        
        Notes:
            None
        '''
        
        self.rect = pygame.Rect(parentrect)
        self.buttondim = buttondim
        self.columns = columns
        self.spacing = (self.rect.width - buttondim * columns) / (columns + 1)
        
        self.setImages(images)
    
    def setImages(self, images):
        #The operator // means integer division, it automatically finds the floor of the number
        self.rect.height = self.spacing + (self.spacing + self.buttondim) * (max(len(images), self.columns) // self.columns)
        
        self.buttons = []
        for position, image in enumerate(images):
            x = self.rect.left + self.spacing + (self.spacing + self.buttondim) * (position  % self.columns)
            y = self.rect.top + self.spacing + (self.spacing + self.buttondim) * (position // self.columns)
            self.buttons.append(ImageButton(image, (x, y, self.buttondim, self.buttondim)))
    
    def scroll(self, amount):
        for button in self.buttons:
            button.move(0, amount)
    
    def update(self, mousepos):
        result = None
        
        for position, button in enumerate(self.buttons):
            if button.update(mousepos):
                result = position
        
        return result
    
    def render(self, surface):
        for button in self.buttons:
            button.render(surface)