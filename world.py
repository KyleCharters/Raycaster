from constants import W_WALLDIST
import math
import file
import pack

class Level(object):
    def __init__(self, info=None):
        self.finished = False
        
        if info is not None:
            #Load level by string or by dictionary
            if isinstance(info, str):
                data = file.loadJson(info)
            elif isinstance(info, dict):
                data = info
            
            self.name = data['name']
            #Must convert to list because it will be reused
            self.ceilingcolor = data['ceilingcolor']
            self.floorcolor = data['floorcolor']
            self.outerwall = data['outerwall']
            self.pack = pack.Pack(data['pack'])
            
            self.map = data['map']
            
            player = data['player']
            self.player = Player(player[0], player[1], player[2], player[3], player[4], player[5], player[6], player[7], player[8], player[9], player[10])
            self.player.level = self
            
            self.statics = []
            for static in data['statics']:
                self.addEntity(Static(static[0], static[1], static[2]))
            
            self.items = []
            for item in data['items']:
                self.addEntity(Item(item[0], item[1], item[2], item[3]))
            
            self.enemies = []
            for enemy in data['enemies']:
                self.addEntity(Enemy(enemy[0], enemy[1], enemy[2], enemy[3], enemy[4], enemy[5], enemy[6], enemy[7], enemy[8], enemy[9]))
            
            self.projectiles = []
        else:
            self.name = "Untitled"
            
            self.ceilingcolor = (235, 235, 235)
            self.floorcolor = (75, 75, 75)
            self.outerwall = 1
            self.pack = pack.Pack("Dungeon")
            
            self.loadEmpty(10, 10)
            
            self.player = Player(0.5, 0.5, 0, 4, 5, 100, 1, 0.1, 4, 5, 1)
            self.player.level = self
            self.statics = []
            self.items = []
            self.enemies = []
            self.projectiles = []
    
    def getDictionary(self):
        return {"name": self.name,
                "ceilingcolor": self.ceilingcolor,
                "floorcolor": self.floorcolor,
                "outerwall": self.outerwall,
                "pack": self.pack.name,
                "map": self.map,
                "player": (self.player.x, self.player.y, self.player.direction, self.player.speed, self.player.sprintspeed, self.player.health, self.player.regen, self.player.cooldown, self.player.projectilespeed, self.player.projectiledamage, self.player.projectiletexture),
                "statics": list(map(lambda static: (static.x, static.y, static.texture), self.statics)),
                "items": list(map(lambda item: (item.x, item.y, item.texture, item.function), self.items)),
                "enemies": list(map(lambda enemy: (enemy.x, enemy.y, enemy.direction, enemy.texture, enemy.speed, enemy.health, enemy.cooldown, enemy.projectilespeed, enemy.projectiledamage, enemy.projectiletexture), self.enemies))}
    
    def copy(self):
        return Level(self.getDictionary())
    
    def save(self, path):
        file.saveJson(path, self.getDictionary())
    
    def changeSize(self, width, height):
        currentWidth = self.getWidth()
        currentHeight = self.getHeight()
        
        if height != currentHeight:
            if height < currentHeight:
                del self.map[height:]
            else:
                self.map += [[0 for _ in range(width)] for _ in range(height - currentHeight)]
        
        if width != currentWidth:
            if width < currentWidth:
                for stripe in self.map:
                    del stripe[width:]
            else:
                for stripe in self.map:
                    stripe += [0 for _ in range(width - currentWidth)]
        
        for sprite in self.statics + self.items + self.enemies + self.projectiles:
            if sprite.x > width or sprite.y > height:
                self.removeEntity(sprite)
    
    def loadEmpty(self, width, height):
        self.map = [[0 for _ in range(width)] for _ in range(height)]
    
    def getWidth(self):
        return len(self.map[0])
    
    def getHeight(self):
        return len(self.map)
    
    def inBounds(self, x, y):
        return (0 <= x < self.getWidth() and 0 <= y < self.getHeight())
    
    def setElement(self, x, y, value):
        #Check to see if the requested x and y values are inside the map
        if self.inBounds(x, y):
            self.map[y][x] = value
            return True
        return False
    
    def getElement(self, x, y):
        #Check to see if the requested x and y values are inside the map
        if self.inBounds(x, y):
            return self.map[y][x]
        return self.outerwall
    
    def getRelativeElement(self, x, y, deltaX, deltaY):
        return self.getElement(math.floor(x + deltaX), math.floor(y + deltaY))
    
    def addEntity(self, entity):
        if entity.level is None:
            entity.level = self
            if entity.variation == 0:
                self.statics.append(entity)
            elif entity.variation == 1:
                self.items.append(entity)
            elif entity.variation == 2:
                self.enemies.append(entity)
            elif entity.variation == 3:
                self.projectiles.append(entity)
    
    def removeEntity(self, entity):
        if entity is not None:
            if entity.variation == 0:
                self.statics.remove(entity)
                del entity
            elif entity.variation == 1:
                self.items.remove(entity)
                del entity
            elif entity.variation == 2:
                self.enemies.remove(entity)
                del entity
            elif entity.variation == 3:
                self.projectiles.remove(entity)
                del entity
    
    def getEntities(self):
        return self.statics + self.items + self.enemies + self.projectiles + [self.player]
    
    def getEntity(self, x, y, variation, area=0.5):
        #Should never be used repeatedly, Inefficient.
        result = None
        
        if variation == -1:
            for sprite in self.getEntities():
                if sprite.collideCircle(x, y, area):
                    result = sprite
                    break
        else:
            if variation == 0:
                for static in self.statics:
                    if static.collideCircle(x, y, area):
                        result = static
                        break
            elif variation == 1:
                for item in self.items:
                    if item.collideCircle(x, y, area):
                        result = item
                        break
            elif variation == 2:
                for enemy in self.enemies:
                    if enemy.collideCircle(x, y, area):
                        result = enemy
                        break
            elif variation == 3:
                for projectile in self.projectiles:
                    if projectile.collideCircle(x, y, area):
                        result = projectile
                        break
        
        return result
    
    def update(self, delta):
        self.player.update(delta)
        
        for item in self.items:
            item.update(delta)
        
        for enemy in self.enemies:
            enemy.update(delta)
        
        for projectile in self.projectiles:
            projectile.update(delta)

class Entity(object):
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.level = None
        #Level is set by the level class, breaks if no level is attached
    
    def collideCircle(self, x, y, size=0.5):
        '''
        Checks collision within a circle
        Uses Pythagorean theorem
        '''
        return abs(math.sqrt(((self.x - x) ** 2) + ((self.y - y) ** 2))) < size
    
    def collideAABB(self, x, y, size=0.5):
        '''
        Checks collision with axis aligned bounding boxes
        '''
        return  self.x - size <= x <= self.x + size and self.y - size <= y <= self.y + size
    
    def move(self, deltaX, deltaY, collision=True, legdist=W_WALLDIST, fast=True, independent=True):
        '''
        deltaX: Amount to move on the x-axis
        deltaY: Amount to move on the y-axis
        collision: Considers collision
        fast: Checks only sides that entity is moving towards
        legdist: Closest distance the entity can get to the wall
        independent: If collision should be checked for both x and y axis, or only once (To use, fast must be false)
        '''
        if collision:
            if fast:
                #Checks to see if the x movement is inside wall
                if(self.level.getRelativeElement(self.x, self.y, math.copysign(legdist, deltaX) + deltaX, legdist) == 0 and
                   self.level.getRelativeElement(self.x, self.y, math.copysign(legdist, deltaX) + deltaX, -legdist) == 0):
                    self.x += deltaX
                
                #Checks to see if the y movement is inside wall
                if(self.level.getRelativeElement(self.x, self.y, legdist, math.copysign(legdist, deltaY) + deltaY) == 0 and
                   self.level.getRelativeElement(self.x, self.y, -legdist, math.copysign(legdist, deltaY) + deltaY) == 0):
                    
                    self.y += deltaY
            else:
                if independent:
                    #Checks to see if the x movement is inside wall
                    if(self.level.getRelativeElement(self.x, self.y, legdist + deltaX,  legdist) == 0 and
                       self.level.getRelativeElement(self.x, self.y, legdist + deltaX, -legdist) == 0 and
                       self.level.getRelativeElement(self.x, self.y, -legdist + deltaX,  legdist) == 0 and
                       self.level.getRelativeElement(self.x, self.y, -legdist + deltaX, -legdist) == 0):
                        self.x += deltaX
                    
                    #Checks to see if the y movement is inside wall
                    if(self.level.getRelativeElement(self.x, self.y,  legdist, legdist + deltaY) == 0 and
                       self.level.getRelativeElement(self.x, self.y, -legdist, legdist + deltaY) == 0 and
                       self.level.getRelativeElement(self.x, self.y,  legdist, -legdist + deltaY) == 0 and
                       self.level.getRelativeElement(self.x, self.y, -legdist, -legdist + deltaY) == 0):
                        
                        self.y += deltaY
                else:
                    #Check to see if both the x and y together are inside a wall
                    if(self.level.getRelativeElement(self.x, self.y, legdist + deltaX,  legdist + deltaY) == 0 and
                       self.level.getRelativeElement(self.x, self.y, legdist + deltaX, -legdist + deltaY) == 0 and
                       self.level.getRelativeElement(self.x, self.y, -legdist + deltaX,  legdist + deltaY) == 0 and
                       self.level.getRelativeElement(self.x, self.y, -legdist + deltaX, -legdist + deltaY) == 0):
                        self.x += deltaX
                        self.y += deltaY
        else:
            self.x += deltaX
            self.y += deltaY
    
    def walk(self, distance, collision=True):
        '''
        Moves in the entity's current direction
        '''
        #Check movement distance on each axis
        direction = math.radians(self.direction)
        
        self.move(math.cos(direction) * distance, math.sin(direction) * distance, collision)
    
    def strafe(self, distance, collision=True):
        '''
        Moves perpendicular to the entity's current direction
        '''
        #Check movement distance on each axis
        direction = math.radians(self.direction)
        
        self.move(-math.sin(direction) * distance, math.cos(direction) * distance, collision)
    
    def rotate(self, degree):
        self.direction = (self.direction + degree) % 360

class TexturedEntity(Entity):
    def __init__(self, x, y, direction, texture):
        super().__init__(x, y, direction)
        self.texture = texture

class CharacterEntity(Entity):
    def __init__(self, x, y, direction, speed, health, cooldown, projectilespeed, projectiledamage, projectiletexture):
        super().__init__(x, y, direction)
        self.speed = speed
        self.maxhealth = health
        self.health = health
        self.dead = False
        self.cooldown = cooldown
        self.cooldowntime = 0
        self.projectilespeed = projectilespeed
        self.projectiledamage = projectiledamage
        self.projectiletexture = projectiletexture
    
    def update(self, delta):
        self.cooldowntime += delta
    
    def heal(self, amount):
        self.health = min(self.maxhealth, self.health + amount)
    
    def damage(self, amount):
        if self.health - amount > 0:
            self.health -= amount
        else:
            self.dead = True
            self.health = 0
    
    def shoot(self, level):
        if self.cooldowntime > self.cooldown:
            self.cooldowntime = 0
            newProjectile = Projectile(self.x, self.y, self.direction, self.projectiletexture, self)
            newProjectile.walk(1, False)
            level.addEntity(newProjectile)

'''
SPRITE VARIATIONS:
0 = STATIC
1 = ITEM
2 = ENEMY
3 = PROJECTILE
'''

class Player(CharacterEntity):
    variation = -1
    
    def __init__(self, x, y, direction, speed, sprintspeed, health, regen, cooldown, projectilespeed, projectiledamage, projectiletexture):
        super().__init__(x, y, direction, speed, health, cooldown, projectilespeed, projectiledamage, projectiletexture)
        self.sprintspeed = sprintspeed
        self.regen = regen
        self.cooldowntime = 0
    
    def update(self, delta):
        super().update(delta)
        if not self.dead:
            self.heal(self.regen * delta)
        
class Static(TexturedEntity):
    variation = 0
    
    def __init__(self, x, y, texture):
        super().__init__(x, y, 0, texture)

class Item(TexturedEntity):
    variation = 1
    
    def __init__(self, x, y, texture, function):
        super().__init__(x, y, 0, texture)
        self.function = function
        
    def update(self, delta):
        if self.collideAABB(self.level.player.x, self.level.player.y, 0.5):
            if self.function == 0:
                self.level.finished = True
                self.level.removeEntity(self)
            elif self.function == 1:
                self.level.player.heal(50)
                self.level.removeEntity(self)

class Enemy(CharacterEntity):
    variation = 2
    
    def __init__(self, x, y, direction, texture, speed, health, cooldown, projectilespeed, projectiledamage, projectiletexture):
        super().__init__(x, y, direction, speed, health, cooldown, projectilespeed, projectiledamage, projectiletexture)
        self.texture = texture
        self.cooldowntime = 0
    
    def update(self, delta):
        super().update(delta)
        
        if self.dead:
            self.level.removeEntity(self)
        
        self.rotate(min(10, math.degrees(math.atan2(self.level.player.y - self.y, self.level.player.x - self.x)) - self.direction))
        
        if not self.collideCircle(self.level.player.x, self.level.player.y, 4) and self.collideCircle(self.level.player.x, self.level.player.y, 12):
            self.walk(self.speed * delta)
        
        if self.cooldowntime > self.cooldown:
            self.cooldowntime = 0
            newProjectile = Projectile(self.x, self.y, self.direction, 2, self)
            newProjectile.walk(1, False)
            self.level.addEntity(newProjectile)

class Projectile(TexturedEntity):
    variation = 3
    
    def __init__(self, x, y, direction, texture, spawn):
        super().__init__(x, y, direction, texture)
        self.spawn = spawn
        self.speed = spawn.projectilespeed
        self.damage = spawn.projectiledamage
    
    def update(self, delta):
        self.walk(self.speed * delta, False)
        
        if self.level.getElement(math.floor(self.x), math.floor(self.y)) != 0:
            self.level.removeEntity(self)
        elif self.level.player != self.spawn and self.collideAABB(self.level.player.x, self.level.player.y):
            self.level.player.damage(self.damage)
            self.level.removeEntity(self)
        else:
            for enemy in self.level.enemies:
                if enemy != self.spawn and self.collideAABB(enemy.x, enemy.y):
                    enemy.damage(self.damage)
                    self.level.removeEntity(self)
                    break