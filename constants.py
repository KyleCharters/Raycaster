'''
Author: Kyle Charters

Description:
    The constants class contains common variables that may be used in multiple classes 

Contents:
    - Font variables
    - Menu variables
    - Listener variables
    - Graphics variables
    - World variables
    - Player variables

Notes:
    None
'''

from pygame.font import SysFont
from pygame.locals import K_ESCAPE
from utility import KeyListener

#Font constants
F_TITLE = SysFont("Segoe UI", 80)
F_BIG = SysFont("Segoe UI", 30)
F_REGULAR = SysFont("Segoe UI", 16)

#Menu constants
M_BUTTONDIMENSIONS = (320, 30)
M_BUTTONSPACING = 5
M_OFFSET = -20

#Listener constants
L_ESCAPE = KeyListener(K_ESCAPE)

#Graphics constants
G_TEXDIM = 64
G_FOV = 60

#World constants
W_WALLDIST = 0.2

#Player constants
P_ROTATIONSPEED = 80


'''
MODULE HEADER

Description:
    description

Contents:
    contentes

Notes:
    notes
'''

'''
CLASS HEADER

Author: Kyle Charters

Description
    description

Parameters:
    parameter: description

Notes:
    notes
'''

'''
FUNCTION HEADER

Description
    description

Parameters:
    parameter: description

Returns:
    returns

Notes:
    notes
'''
