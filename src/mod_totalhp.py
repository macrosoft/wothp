#!/usr/bin/python
# -*- coding: utf-8 -*-
import BigWorld
import cPickle
import GUI
import json
import os
import ResMgr
from Account import Account
from adisp import process
from Avatar import PlayerAvatar
from ClientArena import ClientArena
from gui import g_guiResetters
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import VehicleMarkerPlugin
from gui.shared import g_itemsCache
from messenger import MessengerEntry
from PlayerEvents import g_playerEvents
from Vehicle import Vehicle
from debug_utils import *

@process
def updateDossier():
    if hasattr(BigWorld.player(), 'arena'):
        return
    g_itemsCache.items.invalidateCache()
    yield g_itemsCache.update(6)
    wothp = Wothp()
    for key in g_itemsCache.items.getVehicles().keys():
        dossier = g_itemsCache.items.getVehicleDossier(key)
        avgDmg = dossier.getRandomStats().getAvgDamage()
        wothp.avgDmgDict[key] = int(avgDmg) if avgDmg else None

class TextLabel(object):
    label = None
    shadow = None
    window = None
    text = ''
    color = '\cFFFFFFFF;'
    visible = True
    x = 0
    y = 0
    hcentered = False
    vcentered = False
    mainCaliberValue = 0

    def __init__(self, config):
        self.text = config.get('text', '')
        if config.get('color', False):
            self.color = '\c' + config.get('color')[1:] + 'FF;'
        self.visible = config.get('visible', True)
        self.x  = config.get('x', 0)
        self.y  = config.get('y', 0)
        self.hcentered  = config.get('hcentered', False)
        self.vcentered  = config.get('vcentered', False)
        background = os.path.join('scripts', 'client', 'gui', 'mods', config.get('background')) \
            if config.get('background', '') else ''
        self.window = GUI.Window(background)
        self.window.materialFX = "BLEND"
        self.window.verticalAnchor = "TOP"
        self.window.horizontalAnchor = "LEFT"
        self.window.horizontalPositionMode = 'PIXEL'
        self.window.verticalPositionMode = 'PIXEL'
        self.window.heightMode = 'PIXEL'
        self.window.widthMode = 'PIXEL'
        self.window.width = config.get('width', 186)
        self.window.height = config.get('height', 32)
        GUI.addRoot(self.window)
        self.shadow = GUI.Text('')
        font = config.get('font', 'default_medium.font')
        self.installItem(self.shadow, font)
        self.label = GUI.Text('')
        self.installItem(self.label, font)
        self.setVisible(self.visible)

    def installItem(self, item, font):
        item.font = font
        self.window.addChild(item)
        item.verticalAnchor = "TOP"
        item.horizontalAnchor = "CENTER"
        item.horizontalPositionMode = 'PIXEL'
        item.verticalPositionMode = 'PIXEL'
        item.position = (self.window.width/2, 0, 1)
        item.colourFormatting = True

    def setVisible(self, flag):
        flag = flag and self.visible
        self.window.visible = flag
        self.shadow.visible = flag
        self.label.visible = flag

    def setText(self, text, color = None):
        shadowText = text.replace('\c60FF00FF;','')
        self.shadow.text = '\c000000FF;' + shadowText
        color = '\c' + color + 'FF;' if color else self.color
        self.label.text = color + text
        
class Wothp(object):
    obj = None
    hpPanel = None
    mainCaliberPanel = None
    avgDmgPanel = None
    avgDmg = None
    config = {}
    hpDict = {}
    aliveDict = {}
    avgDmgDict = {}
    playerTeam = 0

    def __init__(self):
        g_guiResetters.add(self.onChangeScreenResolution)
        g_playerEvents.onBattleResultsReceived += self.battleResultsReceived
        res = ResMgr.openSection('../paths.xml')
        sb = res['Paths']
        vals = sb.values()[0:2]
        for vl in vals:
            path = vl.asString + '/scripts/client/gui/mods/'
            if os.path.isdir(path):
                conf_file = path + 'mod_totalhp.json'
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

    @staticmethod
    def addSeparator(val):
        sVal = format(val, ',d')
        return sVal.replace(',', ' ')

    def onChangeScreenResolution(self):
        sr = GUI.screenResolution()
        for panel in [self.hpPanel, self.mainCaliberPanel, self.avgDmgPanel]:
            if panel is None:
                continue
            x = sr[0]/2 - panel.window.width /2 + panel.x if panel.hcentered else panel.x
            y = sr[1]/2 - panel.window.height/2 + panel.y if panel.vcentered else panel.y
            panel.window.position = (x, y, 1)

    def battleResultsReceived(self, isActiveVehicle, results):
        updateDossier()

    def createLabels(self):
        self.hpPanel = TextLabel(self.config.get('hp_panel', {}))
        self.mainCaliberPanel = TextLabel(self.config.get('maincaliber_panel', {}))
        self.avgDmgPanel = TextLabel(self.config.get('avgdamage_panel', {}))
        self.onChangeScreenResolution()

    def deleteLabels(self):
        GUI.delRoot(self.hpPanel.window)
        self.hpPanel = None
        GUI.delRoot(self.mainCaliberPanel.window)
        self.mainCaliberPanel = None
        GUI.delRoot(self.avgDmgPanel.window)
        self.avgDmgPanel = None
        self.totalAlly = 0
        self.totalEnemy = 0

    def reset(self):
        self.playerTeam = BigWorld.player().team
        self.mainCaliberValue = 0
        self.hpDict = {}
        self.aliveDict = {}

    def update(self):
        if self.hpPanel is None:
            return
        self.totalAlly = 0
        self.totalEnemy = 0
        vehicles = BigWorld.player().arena.vehicles
        for key in self.hpDict:
            if not self.aliveDict[key]:
                continue
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
        mainCaliberText = self.mainCaliberPanel.text
        mainCaliberText += self.addSeparator(self.mainCaliberValue) if self.mainCaliberValue > 0 \
            else '\c60FF00FF;+' + self.addSeparator(abs(self.mainCaliberValue))
        self.mainCaliberPanel.setText(mainCaliberText)
        if self.avgDmg is None:
            return
        avgDmgText =  self.avgDmgPanel.text
        avgDmgText += self.addSeparator(self.avgDmg) if self.avgDmg > 0 \
            else '\c60FF00FF;+' + self.addSeparator(abs(self.avgDmg))
        self.avgDmgPanel.setText(avgDmgText)

    def insertVehicle(self, vid, health):
        self.hpDict[vid] = health
        self.aliveDict[vid] = True

    def updateVehicle(self, vid, health):
        if self.hpDict.get(vid, -1) > health:
            self.hpDict[vid] = max(health, 0)
            self.update()

    def killVehicle(self, vid):
        self.aliveDict[vid] = False

    def getVehicleHealth(self, vid):
        return self.hpDict.get(vid, 0)

    def setVisible(self, flag):
        self.hpPanel.setVisible(flag)
        self.mainCaliberPanel.setVisible(flag)
        self.avgDmgPanel.setVisible(flag and self.avgDmg is not None)

old_PlayerAvatar_setComponentsVisibility = PlayerAvatar.setComponentsVisibility

def new_PlayerAvatar_setComponentsVisibility(self, bool):
    old_PlayerAvatar_setComponentsVisibility(self, bool)
    wothp = Wothp()
    wothp.setVisible(bool)

PlayerAvatar.setComponentsVisibility = new_PlayerAvatar_setComponentsVisibility

old_PlayerAvatar__startGUI = PlayerAvatar._PlayerAvatar__startGUI

def new_PlayerAvatar__startGUI(self):
    old_PlayerAvatar__startGUI(self)
    wothp = Wothp()
    wothp.reset()
    wothp.createLabels()
    player = BigWorld.player()
    playerVehicle = player.arena.vehicles.get(player.playerVehicleID)
    cDescr = playerVehicle['vehicleType'].type.compactDescr
    wothp.avgDmg = wothp.avgDmgDict.get(cDescr, None)
    vehicles = BigWorld.player().arena.vehicles
    for key in vehicles.keys():
        vehicle = vehicles.get(key)
        if vehicle['vehicleType']:
            wothp.insertVehicle(key, vehicle['vehicleType'].maxHealth)
    wothp.update()
    wothp.mainCaliberValue = max(1000, int(wothp.totalEnemy/5))
    if wothp.mainCaliberValue*5 < wothp.totalEnemy:
        wothp.mainCaliberValue += 1
    wothp.mainCaliberPanel.setText(wothp.mainCaliberPanel.text + wothp.addSeparator(wothp.mainCaliberValue))
    if wothp.avgDmg is not None:
        wothp.avgDmgPanel.setText(wothp.avgDmgPanel.text + wothp.addSeparator(wothp.avgDmg))
        wothp.avgDmgPanel.setVisible(True)
    else:
        wothp.avgDmgPanel.setVisible(False)

PlayerAvatar._PlayerAvatar__startGUI = new_PlayerAvatar__startGUI

old_PlayerAvatar__destroyGUI = PlayerAvatar._PlayerAvatar__destroyGUI

def new_PlayerAvatar__destroyGUI(self):
    old_PlayerAvatar__destroyGUI(self)
    wothp = Wothp()
    wothp.deleteLabels()

PlayerAvatar._PlayerAvatar__destroyGUI = new_PlayerAvatar__destroyGUI

old_ClientArena_onVehicleKilled = ClientArena._ClientArena__onVehicleKilled

def new_ClientArena__onVehicleKilled(self, argStr):
    old_ClientArena_onVehicleKilled(self, argStr)
    victimID, killerID, equipmentID, reason = cPickle.loads(argStr)
    wothp = Wothp()
    wothp.killVehicle(victimID)

ClientArena._ClientArena__onVehicleKilled = new_ClientArena__onVehicleKilled

old_VehicleMarkerPlugin__addOrUpdateVehicleMarker = VehicleMarkerPlugin._VehicleMarkerPlugin__addOrUpdateVehicleMarker

def new_VehicleMarkerPlugin__addOrUpdateVehicleMarker(self, vProxy, vInfo, guiProps, active = True):
    old_VehicleMarkerPlugin__addOrUpdateVehicleMarker(self, vProxy, vInfo, guiProps, active)
    wothp = Wothp()
    wothp.updateVehicle(vProxy.id, vProxy.health)

VehicleMarkerPlugin._VehicleMarkerPlugin__addOrUpdateVehicleMarker = new_VehicleMarkerPlugin__addOrUpdateVehicleMarker

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
        damage = wothp.getVehicleHealth(self.id) - max(0, newHealth)
        player = BigWorld.player()
        attacker = player.arena.vehicles.get(attackerID)
        if player.playerVehicleID == attackerID and player.team != self.publicInfo.team:
            wothp.mainCaliberValue -= damage
            if wothp.avgDmg is not None:
                wothp.avgDmg -= damage
        if wothp.config.get('show_team_damage', True) and damage > 0 and \
            player.team == self.publicInfo.team and attacker['team'] == self.publicInfo.team and \
            self.id != attackerID:
            message = message.replace('{{damage}}', str(damage))
            message = message.replace('{{victim-name}}', self.publicInfo.name)
            message = message.replace('{{victim-vehicle}}', self.typeDescriptor.type.shortUserString)
            message = message.replace('{{attacker-name}}', attacker['name'])
            message = message.replace('{{attacker-vehicle}}', attacker['vehicleType'].type.shortUserString)
            MessengerEntry.g_instance.gui.addClientMessage(message)
        wothp.updateVehicle(self.id, newHealth)
        return None

Vehicle.onHealthChanged = new_Vehicle_onHealthChanged

old_onBecomePlayer = Account.onBecomePlayer

def new_onBecomePlayer(self):
    old_onBecomePlayer(self)
    updateDossier()

Account.onBecomePlayer = new_onBecomePlayer
