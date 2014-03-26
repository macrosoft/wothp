#!/usr/bin/python
# -*- coding: utf-8 -*-
import BigWorld
import GUI
from gui.Scaleform.Battle import Battle
from debug_utils import *

class Wothp(object):
    obj = None

    def __init__(self):
        self.window = None
        self.label = None

    def __new__(self, *dt, **mp):
        if self.obj is None:
            self.obj = object.__new__(self, *dt, **mp)
        return self.obj

    def createLabel(self):
        self.window = GUI.Window('')
        sr = GUI.screenResolution()
        self.window.heightMode = 'PIXEL'
        self.window.widthMode = 'PIXEL'
        self.window.width = sr[0]
        self.window.height = sr[1]
        GUI.addRoot(self.window)
        self.label = GUI.Text("12345 / 67890")
        self.label.font = 'Courier New_15.dds'
        self.label.colour = (255.0, 255.0, 255.0, 255.0)
        self.label.materialFX = 'ADD'
        self.window.addChild(self.label)
        self.label.horizontalPositionMode = 'PIXEL'
        self.label.verticalPositionMode = 'PIXEL'
        self.label.position = (sr[0]/2, 45, 1)

    def deleteLabel(self):
        GUI.delRoot(self.window)
        self.window = None

old_Battle_afterCreate = Battle.afterCreate

def new_Battle_afterCreate(self):
    old_Battle_afterCreate(self)
    wothp = Wothp()
    wothp.createLabel()

Battle.afterCreate = new_Battle_afterCreate

old_Battle_beforeDelete = Battle.beforeDelete

def new_beforeDelete(self):
    old_Battle_beforeDelete(self)
    wothp = Wothp()
    wothp.deleteLabel()

Battle.beforeDelete = new_beforeDelete