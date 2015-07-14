#!/usr/bin/env python3.5
import sys
import base64
import json
    
def nice_encode(some_shit):
    return str(base64.b64encode(some_shit),"ascii")

class Snapshot():
    def __init__(self):
        self.config = None
        self.data_time = None
        self.records = {}
    

    def package(self):
        pkg_dict = {}
        if self.config is not None:
            pkg_dict['config'] = nice_encode(self.config)
        if self.data_time is not None:
            pkg_dict['data_time'] = nice_encode(self.data_time)
        pkg_dict['records'] = {}
        for frame in self.records.keys():
            pkg_dict['records'][frame] = list(map(lambda x: nice_encode(x), self.records[frame]))

        return pkg_dict


class Database():
    def __init__(self):
        self.current_snapshot_category = 0
        self.current_snapshot_number = 0
        self.current_snapshot = None
        self.pids = {}
        self.snapshots = {}
        self.configs = {}

    def package(self):
        pkg_dict = {"pids":{},
                    "configs":{},
                    "snapshots":{}}

        for pid in self.pids.keys():
            pkg_dict["pids"][pid] = nice_encode(self.pids[pid])

        for category in self.configs.keys():
            pkg_dict["configs"][category] = nice_encode(self.configs[category])

        for category in self.snapshots.keys():
            pkg_dict["snapshots"][category] = {}
            for number in self.snapshots[category].keys():
                pkg_dict["snapshots"][category][number] = self.snapshots[category][number].package()

        return pkg_dict


def read_pid(payload):
    if payload[0] in [0xfc, 0xfd, 0xfe]:
        pid = (payload[0] << 8) | payload[1]
    else:
        pid = payload[0]

    return pid

def read_pid_and_data(payload):
    pid = read_pid(payload)
    if pid > 255:
        data = payload[2:]
    else:
        data = payload[1:]

    return (pid,data)

def is_snapshot_config_msg(msg):
    return len(msg) >= 5 and msg[:5] == b'\x80\xfe\xac\x90\xcf'

def parse_snapshot_config_msg(msg):
    assert is_snapshot_config_msg(msg)
    return msg[5:]

def is_snapshot_data_time_msg(msg):
    return len(msg) >= 6 and msg[:6] == b'\x80\xfe\xac\x90\xfc\x1c'

def parse_snapshot_data_time_msg(msg):
    assert is_snapshot_data_time_msg(msg)
    return msg[6:]

def is_snapshot_data_message(msg):
    return len(msg) >= 5 and msg[:5] == b'\x80\xfe\xac\x90\xd3'

def parse_snapshot_data_message(msg):
    assert is_snapshot_data_message(msg)

    category = msg[5]
    snapshot = msg[6]
    frame = msg[8]
    message = msg[9]
    data = msg[10:]

    return (category, snapshot, frame, message, data)

def is_snapshot_set_message(msg):
    return len(msg) >= 5 and msg[:5] == b'\x80\xfe\xac\x90\xd1'

def parse_snapshot_set_message(msg):
    assert is_snapshot_set_message(msg)

    category = msg[5]
    snapshot = msg[6]
    
    return (category, snapshot)


def is_read(msg):
    code = msg[3] & 0xF0
    return code in [0xd0,0x70]

def print_usage():
    print('''USAGE: %s <logfile> <outfile>''' % sys.argv[0])

def process_log_line(log_line,db):
    [direction, text_data] = log_line.split(' ')
    if direction == "SM":
        return
        

    msg = bytes(list(map(lambda x: int(x,16), text_data.split(','))))

    if is_snapshot_set_message(msg):
        (db.current_snapshot_category, db.current_snapshot_number) = parse_snapshot_set_message(msg)
        if not db.current_snapshot_category in db.snapshots:
            db.snapshots[db.current_snapshot_category] = {}
        if not db.current_snapshot_number in db.snapshots[db.current_snapshot_category]:
            db.snapshots[db.current_snapshot_category][db.current_snapshot_number] = Snapshot()

        print("setting current snapshot to %d %d" % (db.current_snapshot_category, db.current_snapshot_number))
        db.current_snapshot = db.snapshots[db.current_snapshot_category][db.current_snapshot_number]

    elif is_snapshot_config_msg(msg):
        db.configs[db.current_snapshot_category] = parse_snapshot_config_msg(msg)

    elif is_snapshot_data_time_msg(msg):
        db.current_snapshot.data_time = parse_snapshot_data_time_msg(msg)

    elif is_snapshot_data_message(msg):
        (category, snapshot, frame, message, data) = parse_snapshot_data_message(msg)
        if not frame in db.current_snapshot.records:
            db.current_snapshot.records[frame] = []

        db.current_snapshot.records[frame].append(data)

    else:
        payload = msg[4:]
        (pid,data) = read_pid_and_data(payload)
        db.pids[pid] = data
    

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(-1)

    database = Database()
    with open(sys.argv[1]) as f:
        lines = [line.strip() for line in f]

    print('loading log file')

    for line in lines:
        process_log_line(line,database)

    print('processing log file')
    print("Got %d pids, %d snapshots" % (len(database.pids),len(database.snapshots)))
    for category in database.snapshots.keys():
        for number in database.snapshots[category].keys():
            print("Number of records for snapshot %s %s: %s" % (category,number,len(database.snapshots[category][number].records)))

    with open(sys.argv[2],'w') as f:
        json.dump(database.package(), f)



    print('writing database to %s' % sys.argv[2])

    


