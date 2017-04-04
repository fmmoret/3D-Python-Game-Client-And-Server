from MatchWorld import MatchWorld
from ClientNetworking import *
from Player import Player, Projectile
from threading import Thread
import direct.directbase.DirectStart
import os
# uitest uses cefpython to render gui in headless browser
# uitest copied from panda3d cefpython example
#from cefpython3 import cefpython
#import uitest

PROFILE = os.environ.get('GAME_PROFILE', False)
if PROFILE:
    import cProfile, pstats, StringIO
    from panda3d.core import PStatClient

class MatchClient:
    def __init__(self, connection):
        self.world = MatchWorld(self)
        self.connection = connection
        for i in xrange(3):
            packet = read_server_packet(self.connection)
            if packet._type == 'your_id':
                self.my_id = packet.my_id
            elif packet._type == 'create_object':
                self.world.create_object(Player, packet.object_id, me=(packet.object_id==self.my_id))
            else:
                raise Exception('Did not get id and create object packets')

        self.my_player = self.world.objects[self.my_id]

        self.connection_thread = Thread(target=self.read_communications)
        self.packets = []
        self.send_thread = Thread(target=self.send_communications)
        self.send_thread.daemon = True
        self.connection_thread.daemon = True
        self.connection_thread.start()
        self.send_thread.start()
        if PROFILE:
            prof = cProfile.Profile()
            PStatClient.connect()
            prof.enable()
            try:
                run()
            finally:
                prof.disable()
                s = StringIO.StringIO()
                ps = pstats.Stats(prof, stream=s).sort_stats('tottime')
                ps.print_stats()
                print s.getvalue()
        else:
            run()
        #cefpython.Shutdown()

    def read_communications(self):
        while 1:
            packet = read_server_packet(self.connection)
            if packet:
                if packet._type == 'move_update' or packet._type == 'cast_update' or packet._type == 'status_update':
                    obj = self.world.objects[packet.args[0]]
                    getattr(obj, packet._type)(*packet.args[1:])
                elif packet._type == 'create_object':
                    #self.world.create_object(Player, *packet.args[1:])
                    self.world.create_object(Projectile, packet.object_id)
                elif packet._type == 'delete_object':
                    obj = self.world.objects[packet.object_id]
                    obj.actor.delete()
                    del self.world.objects[packet.object_id]

            else:
                # dc'd
                print "DISCONNECTED"
                break

    def send_communications(self):
        while 1:
            try:
                if self.packets:
                    pops = [0]*len(self.packets)
                    data = ''.join([packet.data for packet in map(self.packets.pop, pops)])
                    self.connection.sendall(data)
            except:
                print "DC'd"
                break

    def send_move(self, direction_delta, velocity):
        packet = MovePacket(direction_delta, velocity)
        self.my_player.simulate_move(direction_delta, velocity)
        self.packets.append(packet)

    def send_cast(self, spell_num, target_id):
        packet = CastSpellPacket(spell_num, target_id)
        self.packets.append(packet)


