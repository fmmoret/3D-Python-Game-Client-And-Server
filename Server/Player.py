from pandac.PandaModules import CollisionTraverser, CollisionNode
from pandac.PandaModules import CollisionHandlerQueue, CollisionRay
from pandac.PandaModules import Vec3, BitMask32


##############################
## BASE MOVING OBJECT
##############################

# CREATE ALL MOVING OBJECTS VIA match.create_object

class MovingObject(object):
    model = '../models/ralph2'
    velocity = 0.0
    speed = 20.0

    def __init__(self, object_id, actor, world, match):
        super(MovingObject, self).__init__()
        self._id = object_id
        self.actor = actor
        self.world = world
        self.match = match

    def delete(self):
        self.match.delete_object(self._id)

    def update(self, time_delta):
        self.actor.setY(self.actor, time_delta*self.velocity*self.speed)


##############################
## SPELLS
#############################

### BASE FLYING SPELL - MOVING OBJECT
class FlyingSpell(MovingObject):
    target = None
    velocity = 1.0
    #def __init__(self, object_id, actor, world, match):
    #    super(FlyingSpell, self).__init__(object_id, actor, world, match)

    def update(self, time_delta):
        if self.target:
            self.actor.lookAt(self.target.actor)
            if self.actor.getDistance(self.target.actor) < 1.0:
                self.collide()
        self.actor.setY(self.actor, time_delta*self.velocity*self.speed)

    def collide(self):
        self.delete()
        self.on_hit()

    # override this with via parent spell object
    # and manually set properties like target or caster
    # if flying_spell_self.on_hit = spell_obj_self.on_hit
    # function would use spell_obj's self for attributes called
    def on_hit(self):
        pass

### BASE SPELL - DOES SPELL ACTIONS ON EVENTS
class SpellObject(object):
    # override anything in this object -- all additional functions
    # need to be utilized in the on_... functions

    cast_time = 1.0
    # time until usable again after use
    cooldown = 0.0
    # max distance between caster and target to initiate casting
    max_range = 100.0
    # line of site needed to perform spell
    los_required = True
    # caster and target are only args ever passed into spells
    # utilize them if you want
    def __init__(self, caster, target):
        self.caster = caster
        self.target = target

    # override and/or manually call this
    # in an on_... function
    def create_flying_spell(self):
        actor = self.caster.actor
        match = self.caster.match
        spell_object = match.create_object(FlyingSpell, actor.getPos(), actor.getHpr())
        spell_object.target = self.target
        # this means that on_hit will run with this
        #object's self not the flying spell object's
        spell_object.on_hit = self.on_hit
        return spell_object

    # when created_objects land -- passed into them by default
    def on_hit(self):
        pass

    # while casting, does this function every server update
    def on_update(self, time_delta):
        pass

    # when casting finishes
    def on_casted(self):
        pass

##################
## EXAMPLE SPELLS
##################
class CastedSpellExample(SpellObject):
    on_hit_damage = 10
    cast_time = 1.0
    cooldown = 0.0

    def on_hit(self):
        # when flying object lands
        # do some damage
        self.target.hurt(self.on_hit_damage)

    def on_casted(self):
        # when finish casting
        # create flying object that goes faster than base
        self.flying_spell = self.create_flying_spell()
        self.flying_spell.speed = 40

class InstantDrainExample(SpellObject):
    # total damage is on_update_damage_per_sec * cast_time
    cast_time = 2.0
    on_update_damage_per_sec = 10
    cooldown = 5.0

    def on_update(self, time_delta):
        # each tick that casting is sustained
        # do damage to the target and heal the player
        self.target.hurt(self.on_update_damage_per_sec*time_delta)
        self.caster.heal(self.on_update_damage_per_sec*time_delta)

class InterruptExample(SpellObject):
    cast_time = 0.0
    cooldown = 10.0
    interrupt_time = 5.0

    def on_casted(self):
        # if target is casting
        if self.target.casting:
            # set all their cooldowns to interrupt_time seconds
            self.target.cooldowns = [self.interrupt_time for cooldown in self.target.cooldowns]
            # and stop whatever they're casting
            self.target.clear_cast()

class MeleeExample(SpellObject):
    cast_time = 0.0
    cooldown = 2.0
    max_range = 20
    on_hit_damage = 10

    def on_casted(self):
        self.target.hurt(self.on_hit_damage)


# TODO implement SpellEffects (debuffs and buffs)


#######################
## PLAYERS
#######################

# Base Player Object - Extend for new champions
class Player(MovingObject):
    alive = True
    spells = [CastedSpellExample, InstantDrainExample, InterruptExample, MeleeExample]
    max_health = 100
    cast_time = None
    casting = False
    curr_spell = None
    spell_num = None
    _damage_modifier = 1.0
    _healing_modifier = 1.0

    def __init__(self, object_id, actor, world, match):
        super(Player, self).__init__(object_id, actor, world, match)
        self.health = self.max_health
        self.cooldowns = [0.0, 0.0, 0.0, 0.0]
        self.init_graphics()

    def init_graphics(self):
        print "BOUNDS", self.actor.node().getBounds()
        ##################
        # TERRAIN MOVEMENT
        ##################
        self.collision_traverser = CollisionTraverser()

        # shoot ray from sky towards terrain
        self.ground_ray = CollisionRay()
        self.ground_ray.setOrigin(0, 0, 1000)
        self.ground_ray.setDirection(0, 0, -1)

        self.ground_col = CollisionNode('playerRay')
        self.ground_col.addSolid(self.ground_ray)
        self.ground_col.setFromCollideMask(BitMask32.bit(0))
        self.ground_col.setIntoCollideMask(BitMask32.allOff())

        self.ground_col_np = self.actor.attachNewNode(self.ground_col)

        self.ground_handler = CollisionHandlerQueue()

        self.collision_traverser.addCollider(self.ground_col_np, self.ground_handler)

        #################
        # LINE OF SIGHT
        #################
        self.los_traverser = CollisionTraverser()

        # shoot ray from sky towards terrain
        self.los_ray = CollisionRay()
        self.los_ray.setOrigin(0, 0, 3)
        self.los_ray.setDirection(0, 1, 0)

        self.los_col = CollisionNode('playerLOSRay')
        self.los_col.addSolid(self.los_ray)
        self.los_col.setFromCollideMask(BitMask32.bit(0))
        self.los_col.setIntoCollideMask(BitMask32.allOff())

        self.los_col_np = self.actor.attachNewNode(self.los_col)

        self.los_handler = CollisionHandlerQueue()

        self.los_traverser.addCollider(self.los_col_np, self.los_handler)

    def hurt(self, damage):
        self.health = max(0, self.health - damage*self._damage_modifier)
        if self.health <= 0:
            self.die()


    def heal(self, amount):
        if self.alive:
            self.health = min(self.max_health, self.health + amount*self._healing_modifier)

    def die(self):
        self.alive = False
        self.clear_cast()
        self.velocity = 0.0

    def clear_cast(self):
        self.curr_spell = None
        self.cast_time = None
        self.target = None
        self.spell_num = None
        self.casting = False

    def move(self, direction, velocity):
        if self.alive:
            self.actor.setH(self.actor.getH() + direction)
            self.velocity = max(min(velocity, 1.0), 0.0)
            self.on_move(direction, velocity)

    # used to interrupt spell casting on movement
    # !! Override if you want
    def on_move(self, direction, velocity):
        if velocity:
            self.clear_cast()

    def update(self, time_delta):
        for index, cooldown in enumerate(self.cooldowns):
            self.cooldowns[index] = max(cooldown - time_delta, 0.0)

        if self.alive:
            spell = self.curr_spell
            if spell:
                self.cast_time = max(self.cast_time - time_delta, 0.0)
                if self.cast_time == 0:

                    if self.world.check_los_and_range(self, self.target, spell.los_required, spell.max_range):
                        spell.on_casted()
                        self.cooldowns[self.spell_num] = spell.cooldown
                        self.casting = False
                    else:
                        self.clear_cast()

                else:
                    spell.on_update(time_delta)

            if self.velocity > 0:
                self.world.move_along_terrain(self, time_delta)

    def cast_spell(self, spell_num, target_id):
        spell_num = self.interpret_spell_num(spell_num)
        if self.cast_time == None and not self.cooldowns[spell_num]:
            spell = self.spells[spell_num]
            target = self.match.objects[target_id]
            if self.world.check_los_and_range(self, target, spell.los_required, spell.max_range):
                self.cast_time = spell.cast_time
                self.target = target
                self.curr_spell = spell(self, target)
                self.spell_num = spell_num
                if self.cast_time > 0:
                    self.casting = True

    # used if you had multiple forms for example
    # but inputs stay the same from the client
    # !! Override if you want, but variable
    # length cooldown packet transmission
    # is probably not yet implemented
    def interpret_spell_num(self, spell_num):
        return spell_num


#######################
## TODO CHAMPIONS
#######################
