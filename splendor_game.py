# -*- coding: utf-8 -*-
"""
Created on Mon May  2 11:45:24 2022.

@author: Nikola
"""

from game_base.game_interface import GameInterfaceConsole
from random import seed

seed(10)
def main():
    console_interface = GameInterfaceConsole()
    console_interface.run()


if __name__ == '__main__':
    main()
