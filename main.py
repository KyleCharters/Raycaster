'''
Author: Kyle Charters

The Raycaster program

Level Features:
    - Name
    - Ceiling Color
    - Floor Color
    - Outer Wall Type
    - Texture Packs
    - Sprites
    - Walls
Game Features:
    - Level Selector
    - Level Player
    - Level Editor
    - Settings
'''

def start():
    #Initialize pygame before everything else because of dependencies
    import pygame
    pygame.display.init()
    pygame.font.init()
    
    import setting
    import state
    import file
    import utility
    
    #Loads settings into memory
    setting.loadSettings()
    
    #Sets the pygame window title to "Raycaster"
    pygame.display.set_caption("Raycaster")  
    #Sets the window icon to the image at "ui/icon.png"
    pygame.display.set_icon(file.loadImage("core/ui/icon.png"))
    
    #Create display and save the display surface
    window = pygame.display.set_mode(setting.resolution())
    #Create a pygame clock for time management
    fpsclock = pygame.time.Clock()
    
    #Create a statemanager and load all of the states
    statemanager = state.StateManager(0, (state.Main(),
                                          state.Selector(),
                                          state.Play(),
                                          state.Pause(),
                                          state.Settings(),
                                          state.Editor()))
    #Create the debugger class
    debugger = utility.Debugger()
    
    running = True
    while running:
        #Find current update data
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        mousepos = pygame.mouse.get_pos()
        delta = min(fpsclock.get_time() / 1000, 0.5)
        
        #Update the current state as well as the debugger
        statemanager.update(window, delta, events, keys, mousepos)
        debugger.update(window, delta, events, keys, mousepos, fpsclock)
        
        #Quit game if pygame called a quit event
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        #Swaps the screen buffer (Same as .update() except it updates entire surface) 
        pygame.display.flip()
        fpsclock.tick(60)
    
    #Saves the settings to settings.json
    setting.saveSettings()
    
    #Exits pygame and the console
    pygame.quit()

if __name__ == "__main__":
    start()