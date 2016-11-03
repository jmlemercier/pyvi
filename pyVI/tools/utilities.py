# -*- coding: utf-8 -*-
"""
Class for color in terminal.

@author: bouvier (bouvier@ircam.fr)
         Damien Bouvier, IRCAM, Paris

Last modified on 12 Sept. 2016
Developed for Python 3.5.1
"""

#==============================================================================
# Class
#==============================================================================

class Style:
    RESET = '\033[0m'
    BRIGHT = '\033[1m'
    BOLD = '\033[2m'
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    BBLACK = '\033[40m'
    BRED = '\033[41m'
    BGREEN = '\033[42m'
    BYELLOW = '\033[43m'
    BBLUE = '\033[44m'
    BPURPLE = '\033[45m'
    BCYAN = '\033[46m'
    BWHITE = '\033[47m'