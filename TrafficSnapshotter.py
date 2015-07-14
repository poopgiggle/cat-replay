import time
import threading
import J1587Driver
import J1939Driver
import JMessage
import queue

class Snapshot():
    def __init__(self):
        self.j1939_traffic_list = []
        self.j1587_traffic_list = []

    def j1939_callback(self, msg_tuple,sent=False):
        (pgn,priority,src_addr,dst_addr,data) = msg_tuple
        if None in (pgn,priority):
            return
        found = False
        for message in self.j1939_traffic_list:
            if message.sent == sent and message.pgn == pgn and message.data == data:
                message.count += 1
                found = True
                break
        if not found:
            self.j1939_traffic_list.append(JMessage.J1939Raw(time=time.time(),pgn=pgn,pri=priority,sa=src_addr,
                                                        da=dst_addr,data=data,sent=sent))

    def j1939_recv_callback(self,msg_tuple):
        self.j1939_callback(msg_tuple,sent=False)

    def j1939_send_callback(self,msg_tuple):
        self.j1939_callback(msg_tuple,sent=True)

    def j1587_callback(self,msg,sent=False):
        mid = msg[0]
        data = msg[1:]

        found = False
        for message in self.j1587_traffic_list:
            if message.sent == sent and message.mid == mid and message.data == data:
                message.count += 1
                found = True
                break
        if not found:
            self.j1587_traffic_list.append(JMessage.J1708Raw(time=time.time(),mid=mid,data=data,sent=sent))

    def j1587_recv_callback(self,msg):
        self.j1587_callback(msg,sent=False)

    def j1587_send_callback(self,msg):
        self.j1587_callback(msg,sent=True)

    def generate_snapshot(self):
        snapshot = self.j1939_traffic_list + self.j1587_traffic_list
        return sorted(snapshot,key=lambda msg: msg.time)

    def dump_to_log(self,filename):
        traffic = sorted(self.j1587_traffic_list+self.j1939_traffic_list,key=lambda x: x.time)
        with open(filename,'w') as f:
            for message in traffic:
                f.write(message.get_log_line())



class J1587WorkerThread(threading.Thread):
    def __init__(self,parent):
        super(J1587WorkerThread,self).__init__()
        self.parent = parent
        self.driver = J1587Driver.J1587Driver(0xac)
        self.stopped = threading.Event()

    def run(self):
        while not self.stopped.is_set():
            try:
                msg = self.driver.read_message(True,0.2)
            except queue.Empty:
                msg = None
            if msg is None:
                continue
            self.parent.j1587_recv_callback(msg)
        

    def send_message(self,msg):
        self.driver.send_message(msg)

    def join(self,timeout=None):
        self.stopped.set()
        self.driver.cleanup()
        super(J1587WorkerThread,self).join(timeout=timeout)

    

class J1939WorkerThread(threading.Thread):
    def __init__(self,parent):
        super(J1939WorkerThread,self).__init__()
        self.parent = parent
        self.driver = J1939Driver.J1939Driver()
        self.my_id = self.driver.my_id
        self.stopped = threading.Event()

    def run(self):
        while not self.stopped.is_set():
            msg = self.driver.read_message()
            if msg is None:
                continue
            self.parent.j1939_recv_callback(msg)

    def send_message(self,priority,pgn,data,da=0xFF):
        return self.driver.send_message(priority,pgn,data,sa=self.my_id,da=da)

    def join(self,timeout=None):
        self.stopped.set()
        self.driver.unbind()
        super(J1939WorkerThread,self).join(timeout=timeout)
        



class TrafficSnapshotter():
    def __init__(self):
        self.snapshot = Snapshot()
        self.subscribers = [self.snapshot]
        self.j1939_worker = J1939WorkerThread(self)
        self.j1587_worker = J1587WorkerThread(self)
        self.j1939_worker.start()
        self.j1587_worker.start()
        self.my_id = self.j1939_worker.my_id



    def j1587_recv_callback(self,msg):
        for subscriber in self.subscribers:
            subscriber.j1587_recv_callback(msg)

    def j1939_recv_callback(self,msg):
        for subscriber in self.subscribers:
            subscriber.j1939_recv_callback(msg)

    def send_j1587(self,msg):
        self.j1587_worker.send_message(msg)
        for subscriber in self.subscribers:
            subscriber.j1587_send_callback(msg)

    def send_j1939(self,priority,pgn,data,da=0xFF):
        x = self.j1939_worker.send_message(priority,pgn,data,da=da)
        for subscriber in self.subscribers:
            subscriber.j1939_send_callback((pgn,priority,self.my_id,da,data))
        return x

    def subscribe(self,subscriber):
        self.subscribers.append(subscriber)

    def cleanup(self):
        self.j1939_worker.join(timeout=.1)
        self.j1587_worker.join(timeout=.1)

    def __del__(self):
        self.j1939_worker.join(timeout=1)
        self.j1587_worker.join(timeout=1)

