'''
Author: Kyle Charters

Description:
    The graphic module contains game graphics utilities 

Contents:
    - render3D()
    - render2D()
    - renderHealth()

Notes:
    None
'''

from constants import G_TEXDIM
from math import cos, sin, radians, sqrt
import pygame
import utility

def render3D(surface, level, fov, linewidth):
    '''
    Description:
        Renders a pseudo 3d image from the player's perspective and direction.
    
    Parameters:
        level: The level used for rendering
        fov: The field of view, used for finding the direction of each ray
        linewidth: The width of each vertical stripe, this changes the amount of rays that need to be sent
    
    Notes:
        Order of rendering:
            - Ceiling and floor
            - Walls
            - Sprites
        
        Uses a similar method to that found at:
            http://lodev.org/cgtutor/raycasting.html
    '''
    
    #Store the width and height of the viewport
    width = surface.get_width()
    height = surface.get_height()
    
    #Find the player direction in radians (Used for python math methods)
    direction = radians(level.player.direction)
    #Fov of 90 degrees means that the plane vector has the same magnitude as the direction vector, which is 1
    fov = fov / 90
    
    #Create the camera vectors, these are used to find out the direction of the rays to send out
    posX = level.player.x
    posY = level.player.y
    dirX = cos(direction)
    dirY = sin(direction)
    plnX = -dirY * fov
    plnY = dirX * fov
    
    #Creates an empty array to store the distances of each strip
    distancebuffer = []
    
    #Draw the ceiling and the floor on the top and bottom half of the viewport
    pygame.draw.rect(surface, level.ceilingcolor, pygame.Rect(0, 0, width, height / 2))
    pygame.draw.rect(surface, level.floorcolor, pygame.Rect(0, height / 2, width, height / 2))
    
    #Iterate over every strip on the x axis
    for x in range(0, width + 1, linewidth):
        #Find the point on the plane vector that is equivalent to the stripe on the screen
        camX = 2 * x / width - 1
        rayPosX = posX
        rayPosY = posY
        rayDirX = dirX + (plnX * camX)
        rayDirY = dirY + (plnY * camX)
        
        #Find the ray tile position
        worldX = int(rayPosX)
        worldY = int(rayPosY)
        
        #Throws errors if ray directions are 0
        #Finds the magnitude of 
        if rayDirX == 0: rayDirX = 0.00001
        deltaDistX = 1 + sqrt((rayDirY ** 2) / (rayDirX ** 2))
        if rayDirY == 0: rayDirY = 0.00001
        deltaDistY = 1 + sqrt((rayDirX ** 2) / (rayDirY ** 2))
        
        #Check if the ray is moving to the right or left, this is used so that the ray only checks on grid lines
        if rayDirX < 0:
            stepX = -1
            sideDistX = (rayPosX - worldX) * deltaDistX
        else:
            stepX = 1
            sideDistX = (worldX + 1 - rayPosX) * deltaDistX
        
        #Check if the ray is moving up or down, this is used so that the ray only checks on grid lines
        if rayDirY < 0:
            stepY = -1
            sideDistY = (rayPosY - worldY) * deltaDistY
        else:
            stepY = 1
            sideDistY = (worldY + 1 - rayPosY) * deltaDistY
        
        #Update ray until it finds a wall
        hit = False
        while hit == False:
            #Update ray position, only moves on one axis every update, so that it can check on grid lines
            if sideDistX < sideDistY:
                sideDistX += deltaDistX
                worldX += stepX
                side = 0
            else:
                sideDistY += deltaDistY
                worldY += stepY
                side = 1
            
            if level.getElement(worldX, worldY) > 0:
                #Exit the loop if the ray hits a wall
                hit = True
        
        #Don't render if the player is inside the same tile
        if worldX == posX and worldY == posY:
            return
        
        #Find the point on the wall where the ray hit. Equation changes if the ray hit the
        #left or right side of the wall instead of the top or bottom side of the tile
        if side == 1:
            wallX = rayPosX + ((worldY - rayPosY + (1 - stepY) / 2) / rayDirY) * rayDirX
        else:
            wallX = rayPosY + ((worldX - rayPosX + (1 - stepX) / 2) / rayDirX) * rayDirY
        wallX -= int(wallX)
        
        #Finds the distance from the player to the wall
        if side == 0:
            wallDistance = abs((worldX - rayPosX + (1 - stepX) / 2) / rayDirX)
        else:
            wallDistance = abs((worldY - rayPosY + (1 - stepY) / 2) / rayDirY)
        
        #Calculates the height that the stripe should appear, pygame does not support values over 10000
        lineHeight = abs(int(height / wallDistance))
        if lineHeight > 10000: lineHeight = 10000
        
        #The top left corner of the stripe when it is centered on the y-axis
        drawStart = -lineHeight / 2 + height / 2
        
        #Find the texture position from the wall position. This compensates for the constant G_TEXDIM
        texX = int(wallX * G_TEXDIM)
        if (side == 0 and rayDirX < 0) or (side == 1 and rayDirY > 0):
            texX = G_TEXDIM - texX - 1
        
        tex = level.pack.getWallSplit(level.getElement(worldX, worldY))[texX]
        
        #Calculate a brightness for the stripe, this is based on wall distance
        lighting = 255 * max(0.2, min(0.95, -(wallDistance / 15) + 1))
        
        #Render the stripe onto the screen.
        surface.blit(utility.darkenSurface(pygame.transform.scale(tex, (linewidth, lineHeight)), lighting), (x - (linewidth / 2), drawStart))
        
        distancebuffer.append(wallDistance)
    
    #Sort entities from farthest away to closest
    entityorder = sorted(map(lambda entity: ((posX - entity.x) ** 2 + (posY - entity.y) ** 2, entity), level.statics + level.items + level.enemies + level.projectiles), key = lambda entity: entity[0], reverse = True)
    
    #Iterate through entities in the list
    for entity in entityorder:
        spriteX = entity[1].x - posX
        spriteY = entity[1].y - posY
        
        #Find the depth and location of the sprite
        invDet = 1.0 / (plnX * dirY - dirX * plnY)
        spriteDepth = invDet * (-plnY * spriteX + plnX * spriteY)
        if spriteDepth == 0: spriteDepth = 0.00001
        spriteLocation = int((width / 2) * (1 + invDet * (dirY * spriteX - dirX * spriteY) / spriteDepth))
        
        tex = level.pack.getSpriteSplit(entity[1].variation, entity[1].texture)
        
        #Find the sprite dimensions
        spriteDim = abs(height / spriteDepth)
        spriteWidth = int(spriteDim * (len(tex) / G_TEXDIM))
        spriteHeight = int(spriteDim * (tex[0].get_height() / G_TEXDIM))
        
        #The top left corner of the sprite
        drawStartY = int(-spriteHeight / 2 + height / 2 + spriteWidth * (level.pack.getSpriteOffset(entity[1].variation, entity[1].texture) / G_TEXDIM))
        
        #Find the left and right of the sprite
        drawStartX = int(-spriteWidth / 2 + spriteLocation)
        drawEndX = int(spriteWidth / 2 + spriteLocation)
        
        #Calculate a brightness for the sprite, this is based on wall distance
        lighting = 255 * max(0.2, min(0.95, -(spriteDepth / 15) + 1))
        
        #Skip if the sprit is off the screen
        if drawStartX > width or drawEndX < 0 or spriteHeight > 800:
            continue
        
        
        for x in range(drawStartX, drawEndX, linewidth):
            #Only render if the stripe is on screen, and the stripe should be closer than any of the walls
            if spriteDepth > 0 and x > 0 and x < width and spriteDepth < distancebuffer[int(x / linewidth)]:
                #Find the texture of the sprite
                texX = int((x - drawStartX) * len(tex) / spriteWidth)
                stripe = tex[texX]
                
                #Render the stripe onto the screen.
                surface.blit(utility.darkenSurface(pygame.transform.scale(stripe, (linewidth, int(spriteHeight))), lighting), (x, drawStartY))

def render2D(surface, rect, level, zoom, playerimage):
    '''
    Description:
        Renders walls and sprites in a 2d top-view perspective, the camera is centered around the player
    
    Parameters:
        rect: The rectangle to draw the view in
        level: The level used for rendering
        zoom: The size of walls and sprites
        playerimage: The image to be used for the player
    
    Notes:
        Order of rendering:
            - Walls
            - Sprites
    '''
    
    #Find the middle of the screen
    middlex = rect[2] / 2
    middley = rect[3] / 2
    tilesize = G_TEXDIM * zoom
    
    #Create image
    image = pygame.Surface(rect[2:])
    image.fill(level.floorcolor)
    pygame.draw.rect(image, (0, 0, 0), pygame.Rect(-level.player.x * tilesize + middlex, -level.player.y * tilesize + middley, level.getWidth() * tilesize, level.getHeight() * tilesize), 2)
    
    #Render walls
    for rowposition, row in enumerate(level.map):
        for colposition, tile in enumerate(row):
            if tile != 0:
                image.blit(pygame.transform.scale(level.pack.getWall(tile), (round(tilesize), round(tilesize))), ((colposition - level.player.x) * tilesize + middlex, (rowposition - level.player.y) * tilesize + middley))
    
    #Render entities
    for entity in level.statics + level.items + level.enemies + level.projectiles:
        texture = utility.aspect(level.pack.getSprite(entity.variation, entity.texture), (int(tilesize / 2), int(tilesize / 2)))
        x = int((entity.x - level.player.x) * tilesize + middlex - int(texture.get_width() / 2))
        y = int((entity.y - level.player.y) * tilesize + middley - int(texture.get_height() / 2))
        image.blit(texture, (x, y))
    
    #Rotate player
    player = pygame.transform.rotozoom(playerimage, -level.player.direction, zoom)
    
    image.blit(player, (middlex - player.get_width() / 2, middley - player.get_height() / 2))
    
    #Render a border around the map in the ceiling colour
    pygame.draw.rect(surface, level.ceilingcolor, image.get_rect(left = rect[0], top = rect[1]).inflate(6, 6), 6)
    surface.blit(image, rect[:2])

def renderHealth(surface, rect, level, barimage, sliverimage):
    '''
    Description:
        Render a health bar in the bottom left corner
    
    Parameters:
        rect: The rectangle to draw the healthbar in
        level: The level used for player health
        barimage: The image used as the background of the health bar
        sliverimage: Resized based on the amount of health the player has
    
    Notes:
        The amount of health is a ratio, the health bar has ha maximum width of 100
    '''
    
    rect = pygame.Rect(rect)
    surface.blit(pygame.transform.scale(barimage, (rect.size)), (rect.topleft))
    surface.blit(pygame.transform.scale(sliverimage, (int((level.player.health / level.player.maxhealth) * 100), sliverimage.get_height())), (rect.left +3, rect.top +3))