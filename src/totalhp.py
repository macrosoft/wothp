#!/usr/bin/python
# -*- coding: utf-8 -*-
import BigWorld
import GUI
from gui.Scaleform.Battle import Battle
from debug_utils import *

old_Battle_afterCreate = Battle.afterCreate

def new_Battle_afterCreate(self):
    old_Battle_afterCreate(self)
    window = GUI.Window('')
    sr = GUI.screenResolution()
    window = GUI.Window('')
    window.heightMode = 'PIXEL'
    window.widthMode = 'PIXEL'
    window.width = sr[0]
    window.height = sr[1]
    GUI.addRoot(window)
    text = GUI.Text("12345 / 67890")
    text.font = 'default_smaller.font'
    text.colour = (255.0, 255.0, 255.0, 255.0)
    text.materialFX = 'ADD'
    window.addChild(text)
    text.horizontalPositionMode = 'PIXEL'
    text.verticalPositionMode = 'PIXEL'
    text.position = (sr[0]/2, 45, 1)

Battle.afterCreate = new_Battle_afterCreate
