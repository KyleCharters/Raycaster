import file

#List of resolution options, list of tuples
resolutionoptions = ((320, 240), (640, 480), (1280, 960))
#Current resolution setting, defaults to 1, (640, 480)
resolutionsetting = 1

def resolution():
    '''
    Returns the current resolution setting (Tuple (width, height))
    '''
    
    return resolutionoptions[resolutionsetting]

def changeResolution():
    '''
    Increases the current resolution setting option by 1, when it reaches the limit it resets
    '''
    
    #Use the global render quality setting variable
    global resolutionsetting
    
    #Add 1 to current resolution setting
    resolutionsetting += 1
    #If the resolution setting is out of the option range, reset to 0
    if resolutionsetting >= len(resolutionoptions):
        resolutionsetting = 0

#List of resolution options, list of integers
renderqualityoptions = (1, 2, 4)
#Current resolution setting, defaults to 1, (2)
renderqualitysetting = 1

def renderquality():
    '''
    Returns the current render quality setting (Integer)
    '''
    
    return renderqualityoptions[renderqualitysetting]

def changeRenderquality():
    '''
    Increases the current render quality setting option by 1, when it reaches the limit it resets
    '''
    
    #Use the global render quality setting variable
    global renderqualitysetting
    
    #Add 1 to current render quality setting
    renderqualitysetting += 1
    #If the render quality setting is out of the option range, reset to 0
    if renderqualitysetting >= len(renderqualityoptions):
        renderqualitysetting = 0

def saveSettings():
    '''
    Saves the resolution and render quality setting to core/Settings.json
    '''
    
    file.saveJson("core/Settings.json", {'resolution' : resolutionsetting, 'renderquality' : renderqualitysetting})

def loadSettings():
    '''
    Loads the resolution and render quality setting from core/Settings.json
    '''
    
    global resolutionsetting
    global renderqualitysetting
    
    data = file.loadJson("core/Settings.json")
    if data is not None:
        resolutionsetting = data['resolution']
        renderqualitysetting = data['renderquality']