#!/usr/bin/env python3.5

import socket
import time

class J1939Driver():
    def __init__(self,my_id=249,interface='can1'):
        self.my_id = my_id
        self.interface = interface
        self.can_socket = socket.socket(socket.PF_CAN, socket.SOCK_DGRAM,
                                        socket.CAN_J1939)
        try:
            self.can_socket.bind((self.interface,socket.J1939_NO_NAME,socket.J1939_NO_PGN,self.my_id))
        except OSError:
            self.my_id += 1
            self.can_socket.bind((self.interface,socket.J1939_NO_NAME,socket.J1939_NO_PGN,self.my_id))
        except Exception as e:
            raise e

        self.can_socket.settimeout(5)
        socket.CMSG_SPACE(1) + socket.CMSG_SPACE(8)#what does this do?

    def unbind(self):
        self.can_socket.close()

    def send_message(self, priority, pgn, sdata, sa=249,da = 0xFF):
        spriority = (priority << 26) & 0x1C000000
        spgn      = (pgn      <<  8) & 0x03FFFF00
        ssa       = (sa       <<  0) & 0x000000FF

        
        data = bytearray(sdata)

        try:
            x = self.can_socket.sendto(data,(self.interface,socket.J1939_NO_NAME,pgn,da))
        except Exception as e:
            print(str(time.time())+" Send error: %s" % e)
            x=-1

        return x

    def read_message_raw(self):
        try:
           data, ancdata, msgflags, address = self.can_socket.recvmsg(2048,64)
        except socket.timeout:
            return (None,None,None,None)
        except OSError:
            return (None,None,None,None)
        else:
            return (data,ancdata,msgflags,address)

    def read_message(self):
        data,ancdata,msgflags,address = self.read_message_raw()
        pgn = None
        priority = None
        src_addr = None
        dst_addr = None
        
        if ancdata is not None and len(ancdata) == 1:
            priority = ancdata[0][2][0]
            dst_addr = 0xFF
        elif ancdata is not None and len(ancdata) == 2:
            priority = ancdata[1][2][0]
            dst_addr = ancdata[0][2][0]
        if address is not None:
            src_addr = address[4]
            pgn = address[3]
        return pgn,priority,src_addr,dst_addr,data

    def request_pgn(self,pgn):
        recvd = False
        start_time = time.time()
        req_data = bytes([pgn & 0xFF, (pgn & 0xFF00) >> 8, (pgn & 0xFF0000) >> 16])
        data = None
        while (not recvd) and time.time() - start_time < .5:
            sent_time = time.time()
            result = self.send_message(6,59904,req_data)
            if result < 0:
                continue
            (this_pgn,priority,src,dst,data) = self.read_message()
            while this_pgn != pgn and time.time() - sent_time < .2:
                (this_pgn,priority,src,dst,data) = self.read_message()
            if this_pgn == pgn:
                print(repr((this_pgn,priority,src,dst,data)))
                recvd = True
            else:
                data = None
        
        return data

if __name__ == '__main__':
    driver = J1939Driver()
    names={'DM02':65227,'DM04':65229,'DM05':65230,'DM06':65231,'DM10':65234,'DM12':65236,'DM19':54016,'DM20':49664,'DM21':49408,'DM23':64949,'DM24':64950,
		'DM26':64952,'DM27':64898,'DM28':64896,'DM29':40448,'DM31':41728,'DM32':41472,'DM33':41216,'DM34':40960,'DM35':40704,'DM36':64868,'DM37':64868,
		'DM38':64866,'DM39':64865,'DM40':64864,'Vehicle Hours':65255,'Idle Operation':65244,'High Res ODD':65217,'Fuel Consumption':65257,
		'Total Average Info':65101,'Fuel Info':65203,'TripInfoAF2':64888,'TripInfoAF1':64889,'TipFuelCons':65199,'TripTimeInfo':65200,
		'EAvgTripFuelInfo':65202,'EAvgTripFuelInfo2':65203,'TripTimeGearInfo':65204,'TripShudownInfo':65205,'TripSpeedInfo':65206,
		'EngineSpeedInfo':65207,'TripFuelInfo':65208,'TripFuelInfo2':65209,'TripDistInfo':65210,'TripFanInfo':65211,'BrakeInfo':65212,
		'EngineTime':65254,'VIN':65260,'CompID':65259}
    for name in names.keys():
        print('%s (%d): %s' % (name,names[name],driver.request_pgn(names[name])))
        

