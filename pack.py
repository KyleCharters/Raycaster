'''
Author: Kyle Charters

Description:
    The pack module contains all pack related items

Contents:
    - Pack
    - listPacks()

Notes:
    None
'''

import file
import utility

class Pack(object):
    def __init__(self, name):
        '''
        Description
            A pack contains all world related textures
        
        Parameters:
            name: The name of the pack
        
        Notes:
            Loads packs from folders inside the "pack" folder
        '''
        
        self.name = name
        
        #Create empty arrays
        self.wall = []
        self.wallsplit = []
        self.sprite = [[], [], [], []]
        self.spritesplit = [[], [], [], []]
        self.spriteoffset = [[], [], [], []]
        
        directory = "packs/" + name + "/"
        if file.exists(directory):
            data = file.loadJson(directory + "pack.def")
            
            for texture in data['wall']:
                image = file.loadImage(directory + texture)
                
                self.wall.append(image)
                self.wallsplit.append(utility.splitSurface(image))
            
            for texture in data['sprite']:
                image = file.loadImage(directory + texture[1], (0, 0, 0))
                
                self.sprite[texture[0]].append(image)
                self.spritesplit[texture[0]].append(utility.splitSurface(image, (0, 0, 0), True))
                self.spriteoffset[texture[0]].append(texture[2])
            
            self.unknown = file.loadImage("core/tex/unknown.png")
            self.unknownsplit = utility.splitSurface(self.unknown)
    
    def getWall(self, index):
        if 0 < index <= len(self.wall):
            return self.wall[index - 1]
        return self.unknown
    
    def getWallSplit(self, index):
        if 0 < index <= len(self.wallsplit):
            return self.wallsplit[index - 1]
        return self.unknownsplit
    
    def getSprite(self, variation, index):
        if 0 < index <= len(self.sprite[variation]):
            return self.sprite[variation][index - 1]
        return self.unknown
    
    def getSpriteSplit(self, variation, index):
        if 0 < index <= len(self.spritesplit[variation]):
            return self.spritesplit[variation][index - 1]
        return self.unknownsplit
    
    def getSpriteOffset(self, variation, index):
        if 0 < index <= len(self.spriteoffset[variation]):
            return self.spriteoffset[variation][index - 1]
        return 0

def listPacks():
    return list(map(lambda name: name.capitalize(), file.listFolders("packs/")))