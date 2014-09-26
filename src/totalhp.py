#!/usr/bin/python
# -*- coding: utf-8 -*-
import BigWorld
import cPickle
import GUI
import json
import os
import ResMgr
from Avatar import PlayerAvatar
from ClientArena import ClientArena
from gui import g_guiResetters
from gui.Scaleform.Battle import Battle, VehicleMarkersManager
from messenger import MessengerEntry
from Vehicle import Vehicle
from debug_utils import *

class TextLabel(object):
    label = None
    shadow = None
    window = None

    def __init__(self, parent, x, y, font):
        self.window = parent
        self.shadow = GUI.Text('')
        self.installItem(self.shadow, x + 1, y + 1, font)
        self.label = GUI.Text('')
        self.installItem(self.label, x, y, font)

    def installItem(self, item, x, y, font):
        item.font = font
        self.window.addChild(item)
        item.verticalAnchor = "TOP"
        item.horizontalAnchor = "CENTER"
        item.horizontalPositionMode = 'PIXEL'
        item.verticalPositionMode = 'PIXEL'
        item.position = (self.window.width/2 + x, y, 1)
        item.colourFormatting = True

    def setVisible(self, flag):
        self.shadow.visible = flag
        self.label.visible = flag

    def setText(self, text, color = 'FFFFFF'):
        self.shadow.text = '\c000000FF;' + text
        self.label.text = '\c' + color + 'FF;' + text
        
class Wothp(object):
    obj = None
    window = None
    hpPanel = None
    mainCaliber = None
    config = {}
    hpDict = {}
    playerTeam = 0

    def __init__(self):
        g_guiResetters.add(self.onChangeScreenResolution)
        res = ResMgr.openSection('../paths.xml')
        sb = res['Paths']
        vals = sb.values()[0:2]
        for vl in vals:
            path = vl.asString + '/scripts/client/mods/'
            if os.path.isdir(path):
                conf_file = path + 'totalhp.json'
                if os.path.isfile(conf_file):
                    with open(conf_file) as data_file:
                        self.config = json.load(data_file)
                        break
        colors = self.config.get('colors')
        for item in colors:
            item['color'] = item['color'][1:]

    def __new__(self, *dt, **mp):
        if self.obj is None:
            self.obj = object.__new__(self, *dt, **mp)
        return self.obj

    @staticmethod
    def gradColor(startColor, endColor, val):
        grad = []
        startColor = [int(startColor[i:i+2], 16) for i in range(0,5,2)]
        endColor = [int(endColor[i:i+2], 16) for i in range(0,5,2)]
        for i in [0, 1, 2]:
            grad.append(startColor[i]*(1.0 - val) + endColor[i]*val)
        return '%02x%02x%02x' % (grad[0], grad[1], grad[2])

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

    def createLabel(self):
        background = os.path.join('scripts', 'client', 'mods', 'totalhp_bg.dds') \
            if self.config.get('background',True) else ''
        self.window = GUI.Window(background)
        self.window.materialFX = "BLEND"
        self.window.verticalAnchor = "TOP"
        self.window.horizontalAnchor = "LEFT"
        self.window.horizontalPositionMode = 'PIXEL'
        self.window.verticalPositionMode = 'PIXEL'
        self.window.heightMode = 'PIXEL'
        self.window.widthMode = 'PIXEL'
        self.window.width = self.config.get('width', 186)
        self.window.height = self.config.get('height', 32)
        GUI.addRoot(self.window)
        font = self.config.get('font', 'default_medium.font')
        self.hpPanel = TextLabel(self.window, 0, 0, font)
        font = self.config.get('main_caliber_font', 'default_smaller.font')
        self.mainCaliber = TextLabel(self.window, 145, 0, font)
        self.mainCaliber.setText(self.config.get('main_caliber_text', 'Main caliber: ') + '-')
        self.onChangeScreenResolution()

    def deleteLabel(self):
        GUI.delRoot(self.window)
        self.window = None
        self.totalAlly = 0
        self.totalEnemy = 0

    def reset(self):
        self.playerTeam = BigWorld.player().team
        self.hpDict = {}

    def update(self):
        if self.window is None:
            return
        self.totalAlly = 0
        self.totalEnemy = 0
        vehicles = BigWorld.player().arena.vehicles
        for key in self.hpDict:
            vehicle = vehicles.get(key)
            if vehicle['team'] == self.playerTeam:
                self.totalAlly += self.hpDict[key]
            else:
                self.totalEnemy += self.hpDict[key]
        delimiter = ':'
        if self.totalAlly > self.totalEnemy:
            delimiter = '>'
        elif self.totalAlly < self.totalEnemy:
            delimiter = '<'
        text = "{:>6} {:1} {:<6}".format(self.totalAlly, delimiter, self.totalEnemy)
        ratio = float(self.totalAlly)/max(self.totalEnemy, 1)
        colors = self.config.get('colors')
        color = 'FFFFFF'
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
        self.hpPanel.setText(text, color)

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
        self.hpPanel.setVisible(flag)

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
    mainCaliberValue = int(wothp.totalEnemy/5)
    if mainCaliberValue*5 < wothp.totalEnemy:
        mainCaliberValue += 1
    wothp.mainCaliber.setText(wothp.config.get('main_caliber_text', 'Main caliber: ') + str(mainCaliberValue))

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
        message = wothp.config.get('team_damage', '')
        if not len(message):
            return None
        damage = wothp.getVehicleHealth(self.id) - max(0, newHealth)
        player = BigWorld.player()
        attacker = player.arena.vehicles.get(attackerID)
        if damage > 0 and player.team == self.publicInfo.team and \
            attacker['team'] == self.publicInfo.team and self.id != attackerID:
            message = message.replace('{{damage}}', str(damage))
            message = message.replace('{{victim-name}}', self.publicInfo.name)
            message = message.replace('{{victim-vehicle}}', self.typeDescriptor.type.shortUserString)
            message = message.replace('{{attacker-name}}', attacker['name'])
            message = message.replace('{{attacker-vehicle}}', attacker['vehicleType'].type.shortUserString)
            MessengerEntry.g_instance.gui.addClientMessage(message)
        wothp.updateVehicle(self.id, newHealth)
        return None

Vehicle.onHealthChanged = new_Vehicle_onHealthChanged
