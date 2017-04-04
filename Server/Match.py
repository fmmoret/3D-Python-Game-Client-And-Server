from ServerNetworking import *
from Player import Player
import MatchWorld
from utils import call_repeatedly
from threading import Thread


from time import time, sleep

class Match:
    def __init__(self, players, fps=60.0):
        self.interval = 1.0/float(fps)
        self.players = []
        self.objects = {}
        self.num_objects = 0
        self._objects_to_delete = set()
        for connection, client_address in players:
            player = self.create_object(Player, send=False)
            player.connection = connection
            player.packets = []
            player.connection.sendall(YourIdPacket(player._id).data)
            self.players.append(player)
        for player in self.players:
            for player_2 in self.players:
                actor = player_2.actor
                player.connection.sendall(CreateObjectPacket(player_2._id, 1, actor.getH(), player_2.velocity > 0, *actor.getPos()).data)
        self.read_connection_threads = []
        self.send_connection_threads = []
        self.end_event = None
        self.packets = {}

    def create_object(self, object_type, start_pos=(0.0, 0.0, 0.0), start_hpr=(0.0, 0.0, 0.0), send=True):
       object_id = self.num_objects
       obj = _world.create_object(self, object_id, object_type, start_pos, start_hpr)
       self.objects[object_id] = obj
       self.num_objects += 1
       if send:
           for player in self.players:
               actor = obj.actor
               player.packets.append(CreateObjectPacket(object_id, 1, actor.getH(), obj.velocity >0, *actor.getPos()))

       return obj

    def delete_object(self, object_id):
        self._objects_to_delete.add(object_id)

    # Don't call externally
    # or race condition occurs
    def _delete_object(self, object_id):
        obj = self.objects[object_id]
        obj.actor.delete();
        del self.objects[object_id]
        for player in self.players:
            player.packets.append(DeleteObjectPacket(object_id))

    def _delete_objects(self):
        to_delete = list(self._objects_to_delete)
        self._objects_to_delete.symmetric_difference_update(to_delete)
        map(self._delete_object, to_delete)

    def read_communications(self, player):
        while self.match_running:
            try:
                packet = read_client_packet(player.connection)
                if packet:
                    self.packets[player] = packet
                else:
                    #player dc'd
                    break
            except:
                print "PLAYER DC'D"
                self.end()

    def send_communications(self, player):
        #optimized
        pop = player.packets.pop
        packets = player.packets
        _len = len
        _map = map
        _attr = getattr
        sendall = player.connection.sendall
        while self.match_running:
            try:
                if packets:
                    pops = [0]*_len(packets)
                    data = ''.join([packet.data for packet in _map(pop,pops)])
                    sendall(data)
            except:
                print "PLAYER DC'D 2"
                self.end()

    def process_communications(self):
        for player in self.players:
            if player in self.packets:
                packet = self.packets.pop(player)
                getattr(player, packet._type)(*packet.args)

    def send_updates(self):
        # movement updates
        for _id, obj in self.objects.items():
            actor = obj.actor
            x, y, z = actor.getPos()
            packet = MoveUpdatePacket(_id, actor.getH(), obj.velocity > 0, x, y, z)
            for player in self.players:
                player.packets.append(packet)
        for player_obj in self.players:
            # cast time updates
            if player_obj.cast_time != None:
                spell_num = player_obj.spell_num
                packet = CastUpdatePacket(player_obj._id, spell_num, player_obj.curr_spell.cast_time, player_obj.cast_time)
                if player_obj.cast_time == 0:
                    player_obj.clear_cast()
                for player in self.players:
                    player.packets.append(packet)
            # health and cooldown updates
            packet = StatusUpdatePacket(player_obj._id, player_obj.health, player_obj.alive, player_obj.cooldowns)
            for player in self.players:
                player.packets.append(packet)

        self._delete_objects()

        if any([not player.alive for player in self.players]):
            print 'ENDING MATCH'
            self.end()

    def step(self):
        self.process_communications()
        for obj in self.objects.values():
            obj.update(self.interval)
        self.send_updates()

    def start(self):
        self.match_running = True
        self.end_event = call_repeatedly(self.interval, self.step)
        for player in self.players:
            read_thread = Thread(target=self.read_communications, args=[player])
            read_thread.daemon = True
            send_thread = Thread(target=self.send_communications, args=[player])
            send_thread.daemon = True
            read_thread.start()
            send_thread.start()
            self.read_connection_threads.append(read_thread)
            self.send_connection_threads.append(send_thread)

    def end(self):
        self.match_running = False
        self.end_event()
        sleep(3.0)
        # TODO should probably do something better with connections
        for player in self.players:
            #player.connection.shutdown()
            player.connection.close()
        for object_id in self.objects:
            self._objects_to_delete.add(object_id)
        self._delete_objects()
        print 'MATCH ENDED.'


