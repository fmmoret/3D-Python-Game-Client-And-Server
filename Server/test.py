import MatchWorld
from Player import Player
player = _world.create_player(Player)
print player.actor.getPos()
player.update(.1)
print "after update=.1, moving=0", player.actor.getPos()
player.moving = 1.0
player.update(.1)
print "after update=.1, moving=1", player.actor.getPos()
world2 = MatchWorld.MatchWorld()
player2 = world2.create_player(Player)
player.update(.1)
player2.moving = 1.0
player2.update(.1)
print "after update=.1, moving=1, 2nd world offset = 1 with player tied to world 1 and player2 tied to world2", player.actor.getPos(), player2.actor.getPos()
