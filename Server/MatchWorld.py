__all__ = []
import __builtin__ as builtins
from pandac.PandaModules import CollisionTraverser,CollisionNode
from pandac.PandaModules import CollisionHandlerQueue,CollisionRay
from pandac.PandaModules import PandaNode,NodePath
from pandac.PandaModules import Vec3,Vec4,BitMask32
from panda3d.core import loadPrcFileData
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
import random, sys, os, math

DEBUG = os.environ.get('GAME_DEBUG', False)

if DEBUG:
    print 'DEBUG MODE'
else:
    loadPrcFileData('', 'window-type none')
#loadPrcFileData('', 'audio-library-name null')

import direct.directbase.DirectStart
builtins._world = None

class MatchWorld(DirectObject):

    def __init__(self):
        self.render = NodePath('worldrender');
        self.render = render
        if _world:
            raise Exception('You should only create one MatchWorld for now')
        # Set up the environment
        #
        # This environment model contains collision meshes.  If you look
        # in the egg file, you will see the following:
        #
        #    <Collide> { Polyset keep descend }
        #
        # This tag causes the following mesh to be converted to a collision
        # mesh -- a mesh which is optimized for collision, not rendering.
        # It also keeps the original mesh, so there are now two copies ---
        # one optimized for rendering, one for collisions.

        self.environ = loader.loadModel("../models/world")
        self.environ.reparentTo(self.render)
        self.environ.setPos(0,0,0)

        if DEBUG:
            base.cam.setPosHpr(0,-130,30,0,-15,0)

    def create_object(self, match, object_id, object_type, start_pos=(0.0, 0.0, 0.0), start_hpr=(0.0, 0.0, 0.0)):
        actor = Actor(object_type.model)
        actor.reparentTo(self.render)
        actor.setScale(1)
        actor.setPosHpr(Vec3(*start_pos), Vec3(*start_hpr))
        obj = object_type(object_id, actor, self, match)
        return obj

    # deals with grid checking and collision detection
    def move_along_terrain(self, obj, time_delta):

        # save actors's initial position so that we can restore it,
        # in case he falls off the map or runs into something.
        actor = obj.actor

        startpos = actor.getPos()

        actor.setY(actor, time_delta*obj.velocity*obj.speed)

        # Now check for collisions.

        obj.collision_traverser.traverse(self.render)

        # Adjust actors's Z coordinate.  If actors's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.

        #print(obj.ground_handler.getNumEntries())

        entries = []
        for i in range(obj.ground_handler.getNumEntries()):
            entry = obj.ground_handler.getEntry(i)
            entries.append(entry)

        entries.sort(lambda x,y: cmp(y.getSurfacePoint(self.render).getZ(),
                                     x.getSurfacePoint(self.render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            actor.setZ(entries[0].getSurfacePoint(self.render).getZ())
        else:
            actor.setPos(startpos)

        actor.setP(0)

    def check_los_and_range(self, obj, target, los_required, max_range):
        obj_direction = render.getRelativeVector(obj.actor, Vec3(0.0,1.0,0.0))
        vec_to_target = target.actor.getPos() - obj.actor.getPos()
        vec_to_target = Vec3(vec_to_target) + Vec3(0.0,0.0,.5)
        vt_length = vec_to_target.length()
        vec_to_target.normalize()
        # see if caster is facing target
        dot =  vec_to_target.dot(obj_direction)
        in_los = not(los_required)
        in_range = not(max_range) or (vt_length <= max_range)
        if in_range and los_required and (dot >= 0):
            start_hpr = obj.actor.getHpr()
            obj.actor.setHpr(0,0,0)
            obj.los_ray.setDirection(vec_to_target)
            obj.los_traverser.traverse(self.render)

            entries = obj.los_handler.getNumEntries()
            obj.los_handler.sortEntries()
            if entries:
                entry = obj.los_handler.getEntry(0)
                hit_pos = entry.getSurfacePoint(self.render)
                vec_to_collision = Vec3(hit_pos - obj.actor.getPos())
                if vec_to_collision.length() > vt_length:
                    in_los = True
            else:
                in_los = True
            obj.actor.setHpr(start_hpr)
        return in_los and in_range


if not builtins._world:
    builtins._world = MatchWorld()
