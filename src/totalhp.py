#!/usr/bin/python
# -*- coding: utf-8 -*-
import BigWorld
import cPickle
import GUI
from ClientArena import ClientArena
from gui import g_guiResetters
from gui.Scaleform.Battle import Battle
from debug_utils import *

class Wothp(object):
    obj = None
    window = None
    label = None
    hpDict = {}
    playerTeam = 0

    def __init__(self):
        g_guiResetters.add(self.onChangeScreenResolution)

    def __new__(self, *dt, **mp):
        if self.obj is None:
            self.obj = object.__new__(self, *dt, **mp)
        return self.obj

    def onChangeScreenResolution(self):
        if self.window is None:
            return
        sr = GUI.screenResolution()
        self.window.width = sr[0]
        self.window.height = sr[1]
        self.label.position = (sr[0]/2, 45, 1)

    def createLabel(self):
        self.window = GUI.Window('')
        self.window.heightMode = 'PIXEL'
        self.window.widthMode = 'PIXEL'
        GUI.addRoot(self.window)
        self.label = GUI.Text("- / -")
        self.label.font = 'Courier New_15.dds'
        self.label.colour = (255.0, 255.0, 255.0, 255.0)
        self.label.materialFX = 'ADD'
        self.window.addChild(self.label)
        self.label.horizontalPositionMode = 'PIXEL'
        self.label.verticalPositionMode = 'PIXEL'
        self.onChangeScreenResolution()

    def deleteLabel(self):
        GUI.delRoot(self.window)
        self.window = None

    def reset(self):
        self.playerTeam = BigWorld.player().team
        self.hpDict = {}

    def update(self):
        if self.window is None:
            return
        totalAlly = 0
        totalEnemy = 0
        vehicles = BigWorld.player().arena.vehicles
        for key in self.hpDict:
            vehicle = vehicles.get(key)
            if vehicle['team'] == self.playerTeam:
                totalAlly += self.hpDict[key]
            else:
                totalEnemy += self.hpDict[key]
        self.label.text = str(totalAlly) + ' / ' + str(totalEnemy)

    def insertVehicle(self, vid, health):
        self.hpDict[vid] = health

    def updateVehicle(self, vid, health):
        if self.hpDict.get(vid, -1) > health:
            self.hpDict[vid] = health
            self.update()

old_Battle_afterCreate = Battle.afterCreate

def new_Battle_afterCreate(self):
    old_Battle_afterCreate(self)
    wothp = Wothp()
    wothp.reset()
    wothp.createLabel()
    vehicles = BigWorld.player().arena.vehicles
    for key in self._Battle__vehicles.keys():
        vehicle = vehicles.get(key)
        wothp.insertVehicle(key, vehicle['vehicleType'].maxHealth)
    wothp.update()

Battle.afterCreate = new_Battle_afterCreate

old_Battle_beforeDelete = Battle.beforeDelete

def new_beforeDelete(self):
    old_Battle_beforeDelete(self)
    wothp = Wothp()
    wothp.deleteLabel()

Battle.beforeDelete = new_beforeDelete

old_ClientArena_onVehicleKilled = ClientArena._ClientArena__onVehicleKilled

def new_ClientArena__onVehicleKilled(self, argStr):
    old_ClientArena_onVehicleKilled(self, argStr)
    victimID, killerID, reason = cPickle.loads(argStr)
    wothp = Wothp()
    wothp.updateVehicle(victimID, 0)

ClientArena._ClientArena__onVehicleKilled = new_ClientArena__onVehicleKilled
