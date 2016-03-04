'''
Author: Kyle Charters

Description:
    The file module contains file utilities

Contents:
    - fullPath()
    - fileName()
    - exists()
    - isFile()
    - listContents()
    - listFiles()
    - listFolders()
    - loadImage()
    - loadString()
    - saveString()
    - loadJson()
    - saveJson()

Notes:
    Some of the methods are only wrappers for os.path methods
'''

import os.path
import pygame.image
import json

def fullPath(path):
    #Get the full path from a relative path
    return os.path.abspath(path)

def fileName(path):
    #Get a name of a file without the extension
    return os.path.split(path)[1].split(".")[0]

def exists(path):
    #Check if a path exists
    return os.path.exists(path)

def isFile(path):
    #Check if a path is a file
    return os.path.isfile(path)

def listContents(path):
    #List the contents of a path
    return os.listdir(path)

def listFiles(path):
    #List only the files of a path
    return list(filter(lambda content: os.path.isfile(path + content), os.listdir(path)))

def listFolders(path):
    #List only the folders of a path
    return list(filter(lambda content: os.path.isdir(path + content), os.listdir(path)))

def loadImage(image, colorKey=None):
    #Load an image and set color key
    image = pygame.image.load(image)
    image.set_colorkey(colorKey)
    return image

def loadString(name):
    #Loads a file as a string
    if os.path.isfile(name):
        return open(name, 'r')
    
    return None

def saveString(name, data):
    #Saves a string as a file
    open(name, 'w').write(data)

def loadJson(name):
    #Loads a file as a json dictionary
    if os.path.isfile(name):
        return json.load(open(name, 'r'))
    
    return None

def saveJson(name, data):
    #Saves a json dictionary as a file
    json.dump(data, open(name, 'w'))