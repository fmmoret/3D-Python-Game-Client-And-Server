from struct import Struct
####### OUTBOUND PACKET TYPES FOR CONSTRUCTION #########
# GIVE PACKETS UNIQUE IDS
int_size = Struct('I').size

class MoveUpdatePacket():
    # consists of an 1 (int) packet type, 1 (int) remaining bytes
    # 1 (int) object_id, 1 (float) xy direction,
    # 1 (boolean) moving indicator, and a 3 (float) x y z position
    _type = 'move_update'
    _id = 100
    data_struct = Struct('3I f ? 3f')
    remaining = data_struct.size - int_size
    def __init__(self, object_id, direction, moving, x, y, z):
        self.data = self.data_struct.pack(self._id, self.remaining, object_id, direction, moving, x, y, z)

class YourIdPacket():
    # consists of 1 (int) packet type, 1 int remaining bytes, 1 (int) object_id
    _type = 'your_id'
    _id = 101
    data_struct = Struct('3I')
    remaining = data_struct.size - int_size
    def __init__(self, object_id):
        self.data = self.data_struct.pack(self._id, self.remaining, object_id)

class CreateObjectPacket():
    # consists of 1 (int) packet type, 1 int remaining bytes,
    # 1 (int) object_id
    # 1 (int) object_type_id, 1 (float) xy direction,
    # 1 (boolean) moving indicator, 3 (float) xyz position
    _type = 'create_object'
    _id = 102
    data_struct = Struct('4I f ? 3f')
    remaining = data_struct.size - int_size
    def __init__(self, object_id, object_type_id, direction, moving, x, y, z):
        self.data = self.data_struct.pack(self._id, self.remaining, object_id, object_type_id, direction, moving, x, y, z)

class DeleteObjectPacket():
    # consists of 1 (int) packet type, 1 int remaining bytes,
    # 1 (int) object_id
    _type = 'delete_object'
    _id = 103
    data_struct = Struct('3I')
    remaining = data_struct.size - int_size
    def __init__(self, object_id):
        self.data = self.data_struct.pack(self._id, self.remaining, object_id)

class CastUpdatePacket():
    # consists of 1 (int) packet type, 1 int remaining bytes,
    # 1 (int) object_id, 1 (int) spell_num, 1 (float) total_time, 1 (float) time_remaining
    _type = 'cast_update'
    _id = 104
    data_struct = Struct('4I 2f')
    remaining = data_struct.size - int_size
    def __init__(self, object_id, spell_num, total_time, time_remaining):
        self.data = self.data_struct.pack(self._id, self.remaining, object_id, spell_num, total_time, time_remaining)

class StatusUpdatePacket():
    # consists of 1 (int) packet type, 1 int remaining bytes,
    # 1 (int) object_id, 1 (int) health, 1 (boolean) alive,
    # 4 (float) cooldowns
    _type = 'status_update'
    _id = 105
    data_struct = Struct('4I ? 4f')
    remaining = data_struct.size - int_size
    def __init__(self, object_id, health, alive, cooldowns):
        self.data = self.data_struct.pack(self._id, self.remaining, object_id, health, alive, *cooldowns)

####### INBOUND PACKET TYPES FOR READING ###############
# GIVE PACKETS UNIQUE IDS

def read_conn(struct, connection):
    data = connection.recv(struct.size)
    return struct.unpack(data)

class MovePacket():
    # consists of an x-y direction and a fraction of max velocity
    _type = 'move'
    _id = 0
    data_struct = Struct('2f')
    def __init__(self, connection):
        self.args = read_conn(self.data_struct, connection)
        self.direction, self.velocity = self.args

class CastSpellPacket():
    # 1 (int) spell_num,
    # and 1 (int) target_id
    _type = 'cast_spell'
    _id = 1
    data_struct = Struct('2I')
    def __init__(self, connection):
        self.args = read_conn(self.data_struct, connection)

class StopCastingPacket():
    _type = 'stop_casting'
    _id = 2
    def __init__(self, connection):
        self.args = ()




###################### READ #########################

# ID
from_client_header = Struct('I')

#### INBOUND PACKET MAP ####
from_client_packet_map = {0: MovePacket,
                        1: CastSpellPacket,
                        2: StopCastingPacket}

def read_client_packet(connection):
    try:
        packet_type, = read_conn(from_client_header, connection)
        return from_client_packet_map[packet_type](connection)
    except:
        return None
