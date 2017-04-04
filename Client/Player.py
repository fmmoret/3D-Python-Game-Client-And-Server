class MovingObject:
    model = '../models/ralph2'
    animations = {'run': '../models/ralph-run2',
                    'walk': '../models/ralph-walk2'}
    moving = False
    direction = 0.0
    speed = 20
    def __init__(self, actor):
        self.actor = actor

    def simulate_move(self, direction, velocity):
        pass

    def move_update(self, direction, moving, x, y, z):
        self.actor.setPos(x, y, z)
        self.actor.setH(direction)
        if self.moving and not moving:
            self.actor.stop()
            self.actor.pose('walk', 5)
            self.moving = False
        elif not self.moving and moving:
            self.actor.loop('run')
            self.moving = True

class Player(MovingObject):
    health = 100
    cast_time = None
    spell_num = None
    def __init__(self, actor):
        MovingObject.__init__(self, actor)
        self.cooldowns = [0.0, 0.0, 0.0, 0.0]

    def cast_update(self, spell_num, total_time, time_remaining):
        self.spell_num = spell_num
        self.cast_time = time_remaining
        '''if total_time:
            self.cast_bar['value'] = time_remaining / float(total_time) * 100
        else:
            self.cast_bar['value'] = 0
        self.cast_bar['text'] = str(round(time_remaining,2))'''

    def status_update(self, health, alive, *cooldowns):
        self.health = health
        #self.health_bar['value'] = health
        #self.health_bar['text'] = str(health)
        self.alive = alive
        self.cooldowns = cooldowns
        #for i, cd in enumerate(cooldowns):
        #    self.cooldown_bars[i]['text'] = str(round(cd,2))

class Projectile(MovingObject):
    model = '../models/arrow'
    animations = {}
    def __init__(self, actor):
        MovingObject.__init__(self, actor)
