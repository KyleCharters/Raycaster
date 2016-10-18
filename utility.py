'''
Author: Kyle Charters

Description:
    The utility module contains code that doesn't exactly fit anywhere else, these are strictly used for utility

Contents:
    - exitPygame()
    - aspect()
    - splitSurface()
    - darkenSurface()
    - KeyListener
    - Debugger

Notes:
    None
'''

from pygame.constants import K_F1, K_F2
import pygame
import constants

#Use lambda because it is a one-liner
exitPygame = lambda pygame: pygame.event.post(pygame.event.Event(pygame.QUIT))

def aspect(image, parentsize):
    #Store image size
    imagesize = image.get_size()
    
    #If image width / height is equal to parent width / height respectively
    if imagesize[0] == parentsize[0] or imagesize[1] == parentsize[1]:
        return image
    #If width is bigger than height, multiply height by size ratio
    elif imagesize[0] > imagesize[1]:
        size = parentsize[0], int(imagesize[1] * (parentsize[0] / imagesize[0]))
    #If height is bigger than width, multiply width by size ratio
    else:
        size = int(imagesize[0] * (parentsize[1] / imagesize[1])), parentsize[1]
    
    #Return the scaled image
    return pygame.transform.scale(image, size)

def splitSurface(image, colorKey=None, convert=False):
    #Create an empty surfaces array to hold every strip
    surfaces = []
    #Iterate over every strip on the x-axis
    for x in range(image.get_width()):
        #Create a surface 1 pixel wide
        surface = pygame.Surface((1, image.get_height()))
        #Converts the surface to the display surface pixel format for fast blitting
        if convert:
            surface = surface.convert()
        #Sets the newly generated surface's color key to the color key supplied. (None is accepted by pygame)
        surface.set_colorkey(colorKey)
        #Render the image onto the 1 pixel wide surface
        surface.blit(image, (-x, 0))
        #Add the new surface to the surfaces array
        surfaces.append(surface)
    
    return surfaces

def darkenSurface(image, value):
    #Creates a new surface with the images size, default color is black
    darkness = pygame.Surface(image.get_size())
    #Changes the blank black surface's alpha, this is transparency
    darkness.set_alpha(255 - value)
    #Set color key to white to prevent textures becoming invisible if they are too dark
    darkness.set_colorkey((255, 255, 255))
    #Render the blank black surface over the texture
    image.blit(darkness, (0, 0))
    
    #Return image to allow one-liners
    return image

class KeyListener(object):
    def __init__(self, key):
        self.key = key
        self.clicked = False
        self.pressed = False
    
    def update(self, keys):
        self.pressed = keys[self.key]
        
        if not self.pressed and self.clicked:
            self.clicked = False
    
    def isClicked(self):
        if self.pressed:
            if not self.clicked:
                self.clicked = True
                return True
        else:
            self.clicked = False
        
        return False

class Debugger():
    def __init__(self):
        self.listener1 = KeyListener(K_F1)
        self.listener2 = KeyListener(K_F2)
        self.log = []
        self.tracking = False
        self.showfps = False
    
    def update(self, surface, delta, events, keys, fpsclock):
        self.listener1.update(keys)
        if self.listener1.isClicked():
            self.showfps = not self.showfps
        
        #Start and stop fps tracking if the listener's key is pressed
        self.listener2.update(keys)
        if self.listener2.isClicked():
            self.tracking = not self.tracking
            if self.tracking:
                #If tracking just started show a message
                print("++++++++++++++++++++")
                print("FPS Tracking started")
                print("--------------------")
            else:
                #If tracking just stopped, print the average fps and clear the fps log
                print("Average FPS:")
                print(sum(self.log)/len(self.log))
                print("--------------------")
                self.log.clear()
        
        fps = fpsclock.get_fps()
        
        if self.tracking:
            #Append fps to the log
            self.log.append(fps)
        
        if self.showfps:
            #Display FPS in the top right corner
            label = constants.F_REGULAR.render(str(int(fps)), 1, (255, 255, 255))
            surface.blit(label, (surface.get_width() - label.get_width() - 5, 0))