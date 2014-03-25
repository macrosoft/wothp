#!/usr/bin/python
# -*- coding: utf-8 -*-
import BigWorld
from gui.Scaleform.Battle import Battle
from debug_utils import *

old_Battle_afterCreate = Battle.afterCreate

def new_Battle_afterCreate(self):
    old_Battle_afterCreate(self)
    LOG_NOTE("hello world!")

Battle.afterCreate = new_Battle_afterCreate
