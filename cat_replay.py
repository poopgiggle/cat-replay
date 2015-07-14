#!/usr/bin/env python3.5
import json, base64, sys
import cat_comms
import struct


def print_usage():
    print('''USAGE: %s <dbfile>
             <dbfile>: json file containing CAT pids and snapshot data''' % sys.argv[0])

def get_command(msg):
    if len(msg) < 4 or msg[1] != 0xfe:
        return None

    return msg[3] & 0xF0
    

def is_read(msg):
    command = get_command(msg)
    if command is not None:
        return command == 0x70 or command == 0xc0
    else:
        return False

def is_write(msg):
    command = get_command(msg)
    if command is not None:
        return command == 0x80 or command == 0xd0
    else:
        return False

def is_encrypted(msg):
    command = get_command(msg)
    if command is not None:
        return command_code >= 0xA0 and command_code <= 0xF0
    else:
        return False

def get_write_response_data(msg):
    assert is_write(msg) and len(msg) >= 5

    return msg[4:]

def get_read_response(pid,data):
    if pid < 0xff:
        send_pid = struct.pack('B',pid)
    else:
        send_pid = struct.pack('>H',pid)

    return send_pid+data
    
def read_pid(payload):
    if payload[0] in [0xfc, 0xfd, 0xfe]:
        pid = (payload[0] << 8) | payload[1]
    else:
        pid = payload[0]

    return pid

def get_pid_from_read(msg):
    assert len(msg) >= 5
    
    payload = msg[4:]
    return read_pid(payload)


def is_snapshot_config_msg(msg):
    return len(msg) >= 5 and msg[:5] == b'\xac\xfe\x80\x70\xcf'

def snapshot_config_response(data):
    return b'\x80\xfe\xac\x90\xcf'+data

def is_snapshot_data_time_msg(msg):
    return len(msg) >= 6 and msg[:6] == b'\xac\xfe\x80\x70\xfc\x1c'

def snapshot_data_time_response(data):
    return b'\x80\xfe\xac\x90\xfc\x1c'+data

def is_snapshot_data_message(msg):
    return len(msg) >= 5 and msg[:5] == b'\xac\xfe\x80\x70\xd3'

def snapshot_data_response(category, snapshot, frame, message_num,data):
    return b'\x80\xfe\xac\x90\xd3'+bytes([category,snapshot,0,frame,message_num,data])

def is_snapshot_set_message(msg):
    return len(msg) >= 9 and msg[:5] == b'\xac\xfe\x80\x80\xd1'

def parse_snapshot_set_message(msg):
    assert is_snapshot_set_message(msg)

    category = msg[5]
    snapshot = msg[6]
    frame = msg[8]
    
    return (category, snapshot, frame)

def snapshot_set_response(category, snapshot, frame):
    return b'\x80\xfe\xac\x90\xd1'+bytes([category,snapshot,0,frame])


def load_data_from_dict(_data_dict):
    ecm_dict = {'configs':{},
                'snapshots':{1:{},2:{},3:{}},
                'pids':{}}

    for key in _data_dict['configs'].keys():
        ecm_dict['configs'][int(key)] = base64.b64decode(_data_dict['configs'][key])

    for key in _data_dict['pids'].keys():
        ecm_dict['pids'][int(key)] = base64.b64decode(_data_dict['pids'][key])
        
    for category in _data_dict['snapshots'].keys():
        for number in _data_dict['snapshots'][category].keys():
            ecm_dict['snapshots'][int(category)][int(number)] = {}
            if 'data_time' in _data_dict['snapshots'][category][number]:
                this_data_time = base64.b64decode(_data_dict['snapshots'][category][number]["data_time"])
                ecm_dict['snapshots'][int(category)][int(number)]['data_time'] = this_data_time
            else:
                continue
            ecm_dict['snapshots'][int(category)][int(number)]['records'] = {}
            for record in _data_dict['snapshots'][category][number]["records"].keys():
                this_record = list(map(base64.b64decode,_data_dict['snapshots'][category][number]["records"][record]))
                ecm_dict['snapshots'][int(category)][int(number)]['records'][int(record)] = this_record

    return ecm_dict
            
            

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(-1)

    with open(sys.argv[1]) as f:
        origin_data_dict = json.load(f)

    replay_data_dict = load_data_from_dict(origin_data_dict)

    client_driver = cat_comms.CatComms()
    current_snap_category = 0
    current_snap_number = 0
    current_snap_frame = 0

    while True:
        inmsg = client_driver.read_message()

        if is_snapshot_set_message(inmsg):
            print("Got snapshot set message: %s" % repr(inmsg))
            (current_snap_category, current_snap_number, current_snap_frame) = parse_snapshot_set_message(inmsg)
            response = snapshot_set_response(current_snap_category, current_snap_number, current_snap_frame)
            print("Responding with: %s" % repr(response))
            client_driver.send_message(response)

        elif is_snapshot_config_message(inmsg):
            print("Got snapshot config message: %s" % repr(inmsg))
            r_data = replay_data_dict['configs'][current_snap_category]
            response = snapshot_config_response(r_data)
            print("Responding with: %s" % repr(response))
            client_driver.send_message(response)

        elif is_snapshot_data_time_message(inmsg):
            print("Got snapshot data_time message: %s" % repr(inmsg))
            r_data = replay_data_dict['snapshots'][current_snap_category][current_snap_number]['data_time']
            response = snapshot_data_time_response(r_data)
            print("Responding with: %s" % repr(response))
            client_driver.send_message(response)

        elif is_snapshot_data_message(inmsg):
            print("Got snapshot data message: %s" % repr(inmsg))
            r_data_list = replay_data_dict['snapshots'][current_snap_category][current_snap_number]['records'][current_snap_frame]
            for i in range(len(r_data_list)):
                data_msg = snapshot_data_response(current_snap_category, current_snap_number, current_snap_frame, i+1, r_data_list[i])
                print("Sending snapshot data record: %s" % repr(data_msg))
                client_driver.send_message(data_msg)

        elif is_write(inmsg):
            print("Got write message: %s" % repr(inmsg))
            r_data = get_write_response_data(inmsg)
            if is_encrypted(inmsg):
                print("Replying encrypted")
                client_driver.send_encrypted_response(r_data)
            else:
                print("Replying plaintext")
                client_driver.send_plain_response(r_data)

        elif is_read(inmsg):
            print("Got read message: %s" % repr(inmsg))
            _pid = get_pid_from_read(inmsg)
            _data = replay_data_dict['pids'][_pid]
            _response_data = get_read_response(_pid, _data)
            if is_encrypted(inmsg):
                print("Replying encrypted: %s" % repr(_response_data))
                client_driver.send_encrypted_response(_response_data)
            else:
                print("Replying plaintext: %s" % repr(_response_data))
                client_driver.send_plain_response(_response_data)

        else:
            print("Got some weird thing (probably a broadcast request): %s" % repr(inmsg))
            
            

    

    
