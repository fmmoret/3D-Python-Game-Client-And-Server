from pandac.PandaModules import PandaNode,NodePath
from pandac.PandaModules import Vec3,Vec4,BitMask32
from panda3d.core import loadPrcFileData
from direct.actor.Actor import Actor
from direct.task.Task import Task
from direct.showbase.DirectObject import DirectObject
import random, sys, os, math

import direct.directbase.DirectStart
from direct.gui.DirectGui import *
from Player import Player

class MatchWorld(DirectObject):

    def __init__(self, client):
        self.render = NodePath('worldrender');
        self.key_map = {'left':0, 'right':0, 'forward':0, 'stop':0, 'spell': -1}
        self.client = client
        self.objects = {}

        base.win.setClearColor(Vec4(0,0,0,1))
        # Set up the environment

        self.environ = loader.loadModel("../models/world")
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)

        # Accept control keys
        self.accept("escape", sys.exit)
        self.accept("1", self.set_key, ["spell",0])
        self.accept("2", self.set_key, ["spell",1])
        self.accept("3", self.set_key, ["spell",2])
        self.accept("4", self.set_key, ["spell",3])
        self.accept("a", self.set_key, ["left",1])
        self.accept("a-up", self.set_key, ["left",0])
        self.accept("d", self.set_key, ["right",1])
        self.accept("d-up", self.set_key, ["right",0])
        self.accept("w", self.set_key, ["forward",1])
        self.accept("w-up", self.set_key, ["forward",0])
        self.accept("w-up", self.set_key, ["stop",1])

        taskMgr.add(self.read_controls, 'read_controls')

    def set_key(self, key, value):
        self.key_map[key] = value

    def create_object(self, object_type, object_id, start_pos=(0.0, 0.0, 0.0), me=False):
        actor = Actor(object_type.model, object_type.animations)
        actor.reparentTo(render)
        actor.setScale(1)
        actor.setPos(Vec3(*start_pos))
        obj = object_type(actor)
        self.objects[object_id] = obj
        if me:
            base.cam.setPosHpr(0,0,0,0,0,0)
            base.cam.reparentTo(actor)
            base.cam.setY(base.cam.getY() - 40)
            base.cam.setZ(base.cam.getZ() + 15)
            base.cam.setHpr(0, -15, 0)

    def read_controls(self, task):
        turn_speed = 7.0
        if self.key_map['forward'] and not self.key_map['stop']:
            if self.key_map['left']:
                self.client.send_move(turn_speed, 1.0)
            elif self.key_map['right']:
                self.client.send_move(-turn_speed, 1.0)
            else:
                self.client.send_move(0.0, 1.0)
        else:
            if self.key_map['left']:
                self.client.send_move(turn_speed, 0.0)
            elif self.key_map['right']:
                self.client.send_move(-turn_speed, 0.0)
            elif self.key_map['stop']:
                self.client.send_move(0.0, 0.0)
            self.key_map['stop'] = 0
            self.key_map['forward'] = 0

        spell = self.key_map['spell']
        if spell >= 0:
            self.key_map['spell'] = -1
            # TODO should pass in target_id
            self.client.send_cast(spell, int(not self.client.my_id))

        return Task.cont
