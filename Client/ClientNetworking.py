from struct import Struct
####### OUTBOUND PACKET TYPES FOR CONSTRUCTION #########
# GIVE PACKETS UNIQUE IDS

class MovePacket():
    # consists of 1 (int) packet id, 1 (float) xy direction,
    # and 1 (float) fraction of max velocity
    _type = 'move'
    _id = 0
    data_struct = Struct('I 2f')
    def __init__(self, direction, velocity):
        self.data = self.data_struct.pack(self._id, direction, velocity)

class CastSpellPacket():
    # consists of 1 (int) packet_id, 1 (int) spell_num,
    # and 1 (int) target_id
    _type = 'cast_spell'
    _id = 1
    data_struct = Struct('3I')
    def __init__(self, spell_num, target_id):
        self.data = self.data_struct.pack(self._id, spell_num, target_id)

class StopCastingPacket():
    # consists of 1 (int) packet_id
    _type = 'stop_casting'
    _id = 2
    data_struct = Struct('I')
    def __init__(self):
        self.data = self.data_struct.pack(self._id)

####### INBOUND PACKET TYPES FOR READING ###############
# GIVE PACKETS UNIQUE IDS

def read_conn(struct, connection):
    return struct.unpack(connection.recv(struct.size))

class MoveUpdatePacket():
    # consists of 1 (int) object_id, 1 (float) xy direction,
    # 1 (boolean) moving indicator, and a 3 (float) x y z position
    _type = 'move_update'
    _id = 100
    data_struct = Struct('I f ? 3f')
    def __init__(self, connection, remaining_content):
        self.args = read_conn(self.data_struct, connection)
        self.object_id = self.args[0]

class YourIdPacket():
    # consists of 1 (int) object_id
    _type = 'your_id'
    _id = 101
    data_struct = Struct('I')
    def __init__(self, connection, remaining_content):
        self.args = read_conn(self.data_struct, connection)
        self.my_id, = self.args

class CreateObjectPacket():
    # 1 (int) object_id
    # 1 (int) object_type_id, 1 (float) xy direction,
    # 1 (boolean) moving indicator, 3 (float) xyz position
    _type = 'create_object'
    _id = 102
    data_struct = Struct('2I f ? 3f')
    def __init__(self, connection, remaining_content):
        self.args = read_conn(self.data_struct, connection)
        self.object_id = self.args[0]

class DeleteObjectPacket():
    # 1 (int) object_id
    _type = 'delete_object'
    _id = 103
    data_struct = Struct('I')
    def __init__(self, connection, remaining_content):
        self.args = read_conn(self.data_struct, connection)
        self.object_id = self.args[0]

class CastUpdatePacket():
    # 1 (int) object_id, 1 (int) spell_num, 1 (float) total_time, 1 (float) time remaining
    _type = 'cast_update'
    _id = 104
    data_struct = Struct('2I 2f')
    def __init__(self, connection, remaining_content):
        self.args = read_conn(self.data_struct, connection)

class StatusUpdatePacket():
    # 1 (int) object_id, 1 (int) health
    _type = 'status_update'
    _id = 105
    data_struct = Struct('2I ? 4f')
    def __init__(self, connection, remaining_content):
        self.args = read_conn(self.data_struct, connection)

##################### READ  ############################

# ID + Remaining length
from_server_header = Struct('2I')

#### INBOUND PACKET MAP ####
from_server_packet_map = {100: MoveUpdatePacket,
                          101: YourIdPacket,
                          102: CreateObjectPacket,
                          103: DeleteObjectPacket,
                          104: CastUpdatePacket,
                          105: StatusUpdatePacket}

#read server packet and return command for client to execute
def read_server_packet(connection):
    data = connection.recv(from_server_header.size)
    packet_type, packet_length = from_server_header.unpack(data)
    remaining_content = packet_length - from_server_header.size
    return from_server_packet_map[packet_type](connection, remaining_content)

