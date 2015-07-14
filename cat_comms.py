import TrafficSnapshotter
import threading
import queue
import time
import base64
import arrow
import math

__keyarray = [0x19,0xAB,0x5C,0x7D,0xED,0x91,0x96,
              0x1B,0x8B,0xB7,0xA2,0x78,0x7A,0x89,
              0x5E,0x0B,0x92,0x4D,0x84]


def _is_proprietary(msg):
    if len(msg) < 2 or msg[1] != 0xFE:
        return False
    else:
        return True

def _is_encrypted(msg):
    try:
        command_code = msg[3]
        return command_code >= 0xA0 and command_code <= 0xF0
    except IndexError:
        return False

def _decrypt_buf(key,data):
    l_buf = list(data)
    return bytes(list(map(lambda x: x ^ __keyarray[key], l_buf)))

def _encrypt_buf(key,data):
    return _decrypt_buf(key,data)

def _get_key(sess_key,code):
    return sess_key + (code % 4)


def _is_setup(msg):
    return _is_encrypted(msg) and (msg[3] & 0xF0) == 0xF0

def _process_msg(msg,sess_key):
    if len(msg) <= 4 or not is_encrypted(msg):
        return msg
    else:
        code = (msg[3] & 0x0F) % 4
        command = bytes([msg[3] & 0xF0])
        decrypted = decrypt_buf(sess_key + code, msg[4:-1])
        return msg[:3]+command+decrypted

def _convert_time(byte_list):
    [sec,minutes,hr,day,mon,yr] = byte_list[-6:]
    ret_sec =math.ceil(sec/4)
    ret_day =math.ceil(day/4)
    ret_yr = yr + 1985
    reported_time = '%d-%02d-%02dT%02d:%02d:%02d+00:00'  % (ret_yr,mon,ret_day,hr,minutes,ret_sec)
    return reported_time




class CatComms():
    _my_session_key = 5
    _other_session_key = 0
    _session_setup = threading.Event()
    _receive_queue = queue.Queue()

    def __init__(self):
        self.snapshotter = TrafficSnapshotter.TrafficSnapshotter()
        self.snapshotter.subscribe(self)

    def cleanup(self):
        self.snapshotter.cleanup()

    @property
    def snapshot(self):
        return self.snapshotter.snapshot

    def j1939_recv_callback(self,msg_tuple):
        pass

    def j1939_send_callback(self,msg_tuple):
        pass

    def j1587_recv_callback(self,msg):
        if not _is_proprietary(msg):
            return #we don't care about non-proprietary messages right now.
        elif _is_setup(msg):
            self._other_session_key = msg[-2] & 0x0F
            self.snapshotter.send_j1587(b'\x80\xfe\xac\xf0'+bytes([self._my_session_key]))
            self._session_setup.set()
            thismsg = msg[:-1]
        elif _is_encrypted(msg):
            decrypted_msg = _process_msg(msg,self._other_session_key)
            thismsg = decrypted_msg
        else:
            thismsg = msg[:-1]

        self._receive_queue.put(thismsg)

    def j1587_send_callback(self,msg):
        pass

    def read_message(self,block=True,timeout=None):
        return self._receive_queue.get(block=block,timeout=timeout)

    def wait_for_message_with_prefix(self,prefix,timeout=2):
        found = False
        start_time = time.time()
        while not found:
            try:
                msg = self.read_message(timeout=timeout)
                if msg is None:
                    return None
                elif msg[:len(prefix)] == prefix:
                    return msg
                elif time.time() - start_time > timeout:
                    return None
            except queue.Empty:
                return None

    def send_message(self,msg):
        self.snapshotter.send_j1587(msg)

    #thin wrapper around Cat's ATA encrypted commands
    def _send_encrypted_ata(self, command, data):
        if not self._session_setup.is_set():
            raise Exception("Tried to send encrypted ATA command before session setup.")

        code = 3 #let's just always make it 3. ECMs don't care.
        prefix = b'\x80\xfe\xac'
        command_byte = bytes([command | code])
        thiskey = _get_key(self._my_session_key, code)
        enc_data = _encrypt_buf(thiskey,data)
        self.send_message(prefix+command_byte+enc_data)

    def send_encrypted_read(self,data):
        self._send_encrypted_ata(0xC0, data)

    def send_encrypted_write(self,data):
        self._send_encrypted_ata(0xD0, data)

    def send_encrypted_response(self,data):
        self._send_encrypted_ata(0xE0, data)

    def _send_plaintext_ata(self, command, data):
        prefix = b'\x80\xfe\xac'
        command_byte = bytes([command])
        this_data = data

        self.send_message(prefix+command_byte+this_data)

    def send_read(self,data):
        self._send_plaintext_ata(0x70,data)

    def send_write(self,data):
        self._send_plaintext_ata(0x80,data)

    def send_plain_response(self,data):
        self._send_plaintext_ata(0x90,data)

    def setup_session(self,timeout=3):
        self._session_setup.clear()
        start_time = time.time()
        while not self._session_setup.is_set() and time.time() - start_time < timeout:
            self.send_message(b'\xac\xfe\x80\xf0'+bytes([self._my_session_key]))
            time.sleep(.5)

        if not self._session_setup.is_set():
            raise Exception("Could not initiate CAT ECM session")

    def get_snapshots(self):
        snapshot_numbers = {1:0,
                            2:0,
                            3:0}
        snaps = []

        for category in sorted(snapshot_numbers.keys()):
            snapshot_numbers[category] = self.get_num_snapshots(category)

        for category in sorted(snapshot_numbers.keys()):
            print("Getting category %s" % category)
            for i in range(snapshot_numbers[category]):
                print("Getting snapshot %d" % (i+1))
                this_snap = self.get_snapshot(category,i+1)
                snaps.append(this_snap)

        return snaps



