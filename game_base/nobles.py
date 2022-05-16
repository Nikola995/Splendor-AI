# -*- coding: utf-8 -*-
"""
Created on Mon May  2 17:05:45 2022

@author: Nikola
"""
from dataclasses import dataclass, field

@dataclass(frozen = True)
class Noble:
    #Number of bonuses per color (type) required to acquire noble
    bonus_required: dict[str,int] = field(default_factory=lambda: ({"green":0,
                                           "white":0,
                                           "blue":0,
                                           "black":0,
                                           "red":0}))
    
    #Number of prestige points the noble is worth
    #default = 3
    prestige_points: int = 3
    
def generate_nobles():
    nobles = []
    nobles.append(Noble({"green":4,"white":0,"blue":0,"black":0,"red":4}))
    nobles.append(Noble({"green":0,"white":3,"blue":0,"black":3,"red":3}))
    nobles.append(Noble({"green":0,"white":4,"blue":4,"black":0,"red":0}))
    nobles.append(Noble({"green":0,"white":4,"blue":0,"black":4,"red":0}))
    nobles.append(Noble({"green":4,"white":0,"blue":4,"black":0,"red":0}))
    nobles.append(Noble({"green":3,"white":0,"blue":3,"black":0,"red":3}))
    nobles.append(Noble({"green":3,"white":3,"blue":3,"black":0,"red":0}))
    nobles.append(Noble({"green":0,"white":0,"blue":0,"black":4,"red":4}))
    nobles.append(Noble({"green":0,"white":3,"blue":3,"black":3,"red":0}))
    nobles.append(Noble({"green":3,"white":0,"blue":0,"black":3,"red":3}))
    return nobles