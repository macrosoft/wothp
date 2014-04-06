#!/usr/bin/python
# -*- coding: utf-8 -*-
import BigWorld
import cPickle
import GUI
import json
import os
from Avatar import PlayerAvatar
from ClientArena import ClientArena
from gui import g_guiResetters
from gui.Scaleform.Battle import Battle, VehicleMarkersManager
from messenger import MessengerEntry
from xml.dom import minidom
from Vehicle import Vehicle
from debug_utils import *

class Wothp(object):
    obj = None
    window = None
    shadow = None
    label = None
    config = {}
    hpDict = {}
    playerTeam = 0

    def __init__(self):
        g_guiResetters.add(self.onChangeScreenResolution)
        path_items = minidom.parse(os.path.join(os.getcwd(), 'paths.xml')).getElementsByTagName('Path')
        for root in path_items:
            path = os.path.join(os.getcwd(), root.childNodes[0].data)
            if os.path.isdir(path):
                conf_file = os.path.join(path, 'scripts', 'client', 'mods', 'totalhp.json')
                if os.path.isfile(conf_file):
                    with open(conf_file) as data_file:
                        self.config = json.load(data_file)
                        break
        colors = colors = self.config.get('colors')
        for item in colors:
            item['color'] = self.hexToRgba(item['color'])

    def __new__(self, *dt, **mp):
        if self.obj is None:
            self.obj = object.__new__(self, *dt, **mp)
        return self.obj

    @staticmethod
    def hexToRgba(hex):
        rgba = [int(hex[i:i+2], 16) for i in range(1,6,2)]
        rgba.append(255)
        return tuple(rgba)

    @staticmethod
    def gradColor(startColor, endColor, val):
        grad = []
        for i in [0, 1, 2, 3]:
            grad.append(startColor[i]*(1.0 - val) + endColor[i]*val)
        return tuple(grad)

    def onChangeScreenResolution(self):
        if self.window is None:
            return
        sr = GUI.screenResolution()
        x = self.config.get('x', -1)
        if x < 0:
            x = sr[0]/2 - self.window.width/2 + 2
        y = self.config.get('y', -1)
        if y < 0:
            y = 30
        self.window.position = (x, y, 1)

    def installItem(self, item, x, y):
        font = self.config.get('font', 'Courier New_15.dds')
        item.font = font
        self.window.addChild(item)
        item.verticalAnchor = "TOP"
        item.horizontalAnchor = "CENTER"
        item.horizontalPositionMode = 'PIXEL'
        item.verticalPositionMode = 'PIXEL'
        item.position = (self.window.width/2 + x, y, 1)

    def createLabel(self):
        background = os.path.join('scripts', 'client', 'mods', 'totalhp_bg.dds') \
            if self.config.get('background',True) else ''
        self.window = GUI.Window(background)
        self.window.colour = (255, 255, 255, 255)
        self.window.materialFX = "BLEND"
        self.window.verticalAnchor = "TOP"
        self.window.horizontalAnchor = "LEFT"
        self.window.horizontalPositionMode = 'PIXEL'
        self.window.verticalPositionMode = 'PIXEL'
        self.window.heightMode = 'PIXEL'
        self.window.widthMode = 'PIXEL'
        self.window.width = self.config.get('width', 186)
        self.window.height = self.config.get('height', 24)
        GUI.addRoot(self.window)
        self.shadow = GUI.Text('')
        self.shadow.colour = (0, 0, 0, 255)
        self.installItem(self.shadow, 1, 1)
        self.label = GUI.Text('')
        self.label.colour = (255, 255, 255, 0)
        self.installItem(self.label, 0, 0)
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
        delimiter = ':'
        if totalAlly > totalEnemy:
            delimiter = '>'
        elif totalAlly < totalEnemy:
            delimiter = '<'
        text = "{:>6} {:1} {:<6}".format(totalAlly, delimiter, totalEnemy)
        self.shadow.text = text
        self.label.text = text
        ratio = float(totalAlly)/max(totalEnemy, 1)
        colors = self.config.get('colors')
        color = (255, 255, 255, 255)
        if ratio <= colors[0]['value']:
            color = colors[0]['color']
        elif ratio >= colors[-1]['value']:
            color = colors[-1]['color']
        else:
            sVal = colors[0]['value']
            eVal = colors[1]['value']
            i = 1
            while eVal < ratio:
                sVal = colors[i]['value']
                i += 1
                eVal = colors[i]['value']
            val = float(ratio - sVal)/(eVal - sVal)
            color = self.gradColor(colors[i - 1]['color'], colors[i]['color'], val)
        self.label.colour = color

    def insertVehicle(self, vid, health):
        self.hpDict[vid] = health

    def updateVehicle(self, vid, health):
        if self.hpDict.get(vid, -1) > health:
            self.hpDict[vid] = max(health, 0)
            self.update()

    def getVehicleHealth(self, vid):
        return self.hpDict.get(vid, 0)

    def setVisible(self, flag):
        self.window.visible = flag
        self.shadow.visible = flag
        self.label.visible = flag

old_PlayerAvatar_setVisibleGUI = PlayerAvatar._PlayerAvatar__setVisibleGUI

def new_PlayerAvatar_setVisibleGUI(self, bool):
    old_PlayerAvatar_setVisibleGUI(self, bool)
    wothp = Wothp()
    wothp.setVisible(bool)

PlayerAvatar._PlayerAvatar__setVisibleGUI = new_PlayerAvatar_setVisibleGUI

old_Battle_afterCreate = Battle.afterCreate

def new_Battle_afterCreate(self):
    old_Battle_afterCreate(self)
    wothp = Wothp()
    wothp.reset()
    wothp.createLabel()
    vehicles = BigWorld.player().arena.vehicles
    for key in vehicles.keys():
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

old_createMarker = VehicleMarkersManager.createMarker

def new_createMarker(self, vProxy):
    result = old_createMarker(self, vProxy)
    wothp = Wothp()
    wothp.updateVehicle(vProxy.id, vProxy.health)
    return  result

VehicleMarkersManager.createMarker = new_createMarker

old_Vehicle_onHealthChanged = Vehicle.onHealthChanged

def new_Vehicle_onHealthChanged(self, newHealth, attackerID, attackReasonID):
    if newHealth > 0 and self.health <= 0:
        return None
    elif not self.isStarted:
        return None
    else:
        old_Vehicle_onHealthChanged(self, newHealth, attackerID, attackReasonID)
        wothp = Wothp()
        damage = wothp.getVehicleHealth(self.id) - max(0, newHealth)
        player = BigWorld.player()
        attacker = player.arena.vehicles.get(attackerID)
        if damage > 0 and player.team == self.publicInfo.team and \
            attacker['team'] == self.publicInfo.team and self.id != attackerID:
            message = wothp.config.get('team_damage', '')
            message = message.replace('{{damage}}', str(damage))
            message = message.replace('{{victim-name}}', self.publicInfo.name)
            message = message.replace('{{victim-vehicle}}', self.typeDescriptor.type.shortUserString)
            message = message.replace('{{attacker-name}}', attacker['name'])
            message = message.replace('{{attacker-vehicle}}', attacker['vehicleType'].type.shortUserString)
            MessengerEntry.g_instance.gui.addClientMessage(message)
        wothp.updateVehicle(self.id, newHealth)
        return None

Vehicle.onHealthChanged = new_Vehicle_onHealthChanged
