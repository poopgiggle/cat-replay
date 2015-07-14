
class J1708Msg:

    '''This is an object for a 1708 message'''

    def __init__(self, time, mid, mid_name, pid, name, dataLeng, dataType, bitResolution, minimum, maximum, units, period, dataForm, data, formatStr, category):
        self.time = time
        self.mid = mid
        self.mid_name = mid_name
        self.pid = pid
        self.name = name
        # self.desc = desc
        self.dataLeng = dataLeng
        self.dataType = dataType
        self.bitResolution = bitResolution
        self.minimum = minimum
        self.maximum = maximum
        self.units = units
        self.period = period
        self.dataForm = dataForm
        # self.notes = notes
        self.data = data
        self.rawData = data
        self.originalData = data
        self.formatStr = formatStr
        self.category = category
        self.count = 1
    # def init

    @staticmethod
    def getStrLables():
        # return "Time,PID,Name,Data,Units,Period,Count,RawData"
        return "Name,Value,Units,PID,Raw Hex Data"

    def __str__(self):
        # if (type(self.rawData))!= int:
        #       print('TYPEHERE:')
        #       print(type(self.rawData))
        #       print(self.rawData)
        #       print(type(self.rawData[0]))
        #       print(self.rawData[0])
        return "\"" + str(self.name) + "\",\"" + str(self.data) + "\",\"" + (str(self.units) if self.units != '' else 'Bytes') + "\"," + str(self.pid) + "," +\
            ((str(' '.join(('%2.2X' % (i)) for i in list(self.rawData))) if type(
                self.rawData) != int else hex(self.rawData)) if self.rawData != 'N/A' else 'N/A')

    def html(self):
        return "<td>" + str(self.name) + "</td><td>" + str(self.data) + "</td><td>" +\
            (str(self.units) if self.units != '' else 'Bytes') + "</td><td>" + str(self.pid) + "</td><td>" +\
            ((str(' '.join(('%2.2X' % (i)) for i in list(self.rawData))) if type(self.rawData) != int
             else hex(self.rawData)) if self.rawData != 'N/A' else 'N/A') + "</td>"

    def shortFormat(self):
        return  ",,,," +\
                ((str(' '.join(('%2.2X' % (i)) for i in list(self.originalData))) if type(self.originalData) != type(
                    int()) else hex(self.originalData)) if self.originalData != 'N/A' else 'N/A')

    def shortFormatHtml(self):
        return "<td></td><td></td><td>" +\
            "</td><td></td><td>" +\
            ((str(' '.join(('%2.2X' % (i)) for i in list(self.originalData))) if type(self.originalData) != type(
                int()) else hex(self.originalData)) if self.originalData != 'N/A' else 'N/A') + "</td>"

    def toJsonFormat(self):
        retval = {'mid': self.mid, 'mid_name': self.mid_name, 'pid': self.pid, 'pid_name': self.name, 'raw_data': self.getRawHexData(),
                  'value': self.format_data,
                  'units': self.units, 'formatStr': self.formatStr, 'category': self.category}
        return retval

    def getRawHexData(self):
        return ((str(' '.join(('%2.2X' % (i)) for i in list(self.rawData))) if type(self.rawData) != int else hex(self.rawData)) if self.rawData != 'N/A' else 'N/A')

    @property
    def format_data(self):
        try:
            retVal = self.data if type(self.data) == str or not self.formatStr else self.formatStr % self.data
        except:
            print('bad format_data')
            print(self.data)
            print(self.pid)
            print(self.formatStr)
            retVal = self.data
        return retVal


class J1939Msg:

    '''This is an object for a J1939 message'''

    def __init__(self, time, sa, sn, da, dn, pgn, lable, pgnLength, transRate, startb, endb, spnLeng, spn, name, operationalLow, operationalHigh,
                 operatingRange, dataRange, resolution, offset, units, data, formatStr, category):
        self.time = time
        self.sourceAddress = sa
        self.sourceName = sn
        self.destinationAddress = da
        self.destinationName = dn
        self.pgn = pgn
        self.lable = lable
        self.pgnLength = pgnLength
        self.transRate = transRate
        self.startb = startb
        self.endb = endb
        self.spnLeng = spnLeng
        self.spn = spn
        self.name = name
        self.operationalLow = operationalLow
        self.operationalHigh = operationalHigh
        self.operatingRange = operatingRange
        self.dataRange = dataRange
        self.resolution = resolution
        self.offset = offset
        self.units = units
        self.rawData = data
        self.data = data
        self.formatStr = formatStr
        self.category = category
        self.count = 1
    # def init

    @staticmethod
    def getStrLables():
        # return
        # "Time,PGN,Label,SPN,Name,Data,Units,TransmissionRate,Count,RawData"
        # Source Address
        return "Name,Value,Units,PGN,Acronym,SPN,Source,Raw Hex Data"

    def __str__(self):
        # if (type(self.rawData))!= int:
        #       print('TYPEHERE:')
        #       print(type(self.rawData))
        #       print(self.rawData)
        #       print(type(self.rawData[0]))
        return ("\"" + str(self.name) + "\",\"" + str(self.data) + "\",\"" +
                ((str(self.units) if self.units != 'bit' else 'binary mapped') if self.units != 'binary' else '') +
                "\"," + str(self.pgn) + ",\"" +
                str(self.lable) + "\"," + str(self.spn) + ",\"" + str(self.sourceName) + "\"," +
                ((str(' '.join(('%2.2X' % (i)) for i in list(self.rawData)))
                if type(self.rawData) != int else hex(self.rawData)) if self.rawData != 'N/A' else 'N/A'))

    def html(self):
        return "<td>" + str(self.name) + "</td><td>" + str(self.data) + "</td><td>" + ((str(self.units) if self.units != 'bit' else 'binary mapped') if self.units != 'binary' else '') +\
            "</td><td>" + str(self.pgn) + "</td><td>" + str(self.lable) + "</td><td>" + str(self.spn) + "</td><td>" + str(self.sourceName) + "</td><td>" +\
            ((str(' '.join(('%2.2X' % (i)) for i in list(self.rawData))) if type(self.rawData) != type(
                int()) else hex(self.rawData)) if self.rawData != 'N/A' else 'N/A') + "</td>"

    def shortFormat(self):
        return ",,," + str(self.pgn) + ",\"" + str(self.lable) + "\",,\"" + str(self.sourceName) + "\"," +\
            ((str(' '.join(('%2.2X' % (i)) for i in list(self.rawData))) if type(
                self.rawData) != int else hex(self.rawData)) if self.rawData != 'N/A' else 'N/A')

    def shortFormatHtml(self):
        return "<td></td><td></td><td></td><td>" + str(self.pgn) + "</td><td>" + str(self.lable) + "</td><td></td><td>" + str(self.sourceName) + "</td><td>" +\
            ((str(' '.join(('%2.2X' % (i)) for i in list(self.rawData))) if type(self.rawData) != type(
                int()) else hex(self.rawData)) if self.rawData != 'N/A' else 'N/A') + "</td>"

    def getHexData(self):
        return ((str(' '.join(('%2.2X' % (i)) for i in list(self.rawData))) if type(self.rawData) != int else hex(self.rawData)) if self.rawData != 'N/A' else 'N/A')

    def toJsonFormat(self):
        retval = {'spn': self.spn, 'spn_name': self.name,
                  'value': self.format_data,
                  'units': self.units, 'range': self.operatingRange,
                  'op_low': self.operationalLow, 'op_high': self.operationalHigh, 'formatStr': self.formatStr, 'category': self.category}
        # if self.da != None:
        #       retval['da']=self.da
        return retval

    @property
    def format_data(self):
        try:
            retVal = self.data if type(self.data) == str or not self.formatStr else self.formatStr % self.data
        except:
            print('bad format_data')
            print(self.data)
            print(self.spn)
            print(self.formatStr)
            retVal = self.data
        return retVal


class J1939Raw:
    '''This is an object for a non-decoded J1939 Message'''

    def __init__(self, time=0, mid=0, pri=0, edp=0, dp=0, pduf=0, pdus=0, sa=0, pgn=0, da=0, data=None, sent=False):
        self.time = time
        self.mid = mid
        self.pri = pri
        self.edp = edp
        self.dp = dp
        self.pduf = pduf
        self.pdus = pdus
        self.sa = sa
        self.pgn = pgn
        self.data = data
        self.count = 1
        self.da = da
        self.sent = sent

    @staticmethod
    def getStrLables():
        return "Time,PGN,Source,Data"

    def __str__(self):
        return str(self.time) + "," + str(self.pgn) + ",\"" + str(self.sa) + "\"," + (str(','.join(str(i) for i in list(self.data))) if type(self.data) != int else str(self.data))

    def html(self):
        return "<td>" + str(self.time) + "</td><td>" + str(self.pgn) + "</td><td>" + str(self.sa) + "</td><td>" + (str(','.join(str(i) for i in list(self.data))) if type(self.data) != int else str(self.data)) + "</td>"

    def getHexData(self):
        return ((str(' '.join(('%2.2X' % (i)) for i in list(self.data))) if type(self.data) != int else hex(self.data)) if self.data != 'N/A' else 'N/A')

    def get_log_line(self):
        return '%f,%s,%s,%d,%x,%x,%x,%x,%s\n' % (self.time, "J1939", "SM" if self.sent else "RM", self.count, self.pgn, self.pri, self.sa, self.da, ' '.join(list(map(lambda x: "%02x" % x, list(self.data)))))

    def toJsonFormat(self):
        retval = {'time': self.time, 'priority': self.pri, 'pgn': self.pgn, 'sa': self.sa, 'raw_data': self.getHexData(),
                  'message_count': self.count}
        if self.da != None and self.da != -1:
            retval['da'] = self.da
        return retval


class J1708Raw:

    '''This is an object for a non-decoded J1708 Message'''

    def __init__(self, time,  mid, data, sent=False):
        self.time = time
        self.mid = mid
        self.data = data
        self.count = 1
        self.sent = sent

    @staticmethod
    def getStrLables():
        return "Time,Mid,Data"

    def __str__(self):
        return str(self.time) + "," + str(self.mid) + "," + (str(','.join(str(i) for i in list(self.data))) if type(self.data) != int else str(self.data))

    def html(self):
        return "<td>" + str(self.time) + "</td><td>" + str(self.mid) + "</td><td>" + (str(','.join(str(i) for i in list(self.data))) if type(self.data) != int else str(self.data)) + "</td>"

    def shortFormat(self):
        return  ",,,," +\
                ((str(' '.join(('%2.2X' % (i)) for i in list(self.data))) if type(
                    self.data) != int else hex(self.data)) if self.data != 'N/A' else 'N/A')

    def shortFormatHtml(self):
        return "<td></td><td></td><td>" +\
            "</td><td></td><td>" +\
            ((str(' '.join(('%2.2X' % (i)) for i in list(self.data))) if type(self.data) != type(
                int()) else hex(self.data)) if self.data != 'N/A' else 'N/A') + "</td>"

    def getHexData(self):
        return ((str(' '.join(('%2.2X' % (i)) for i in list(self.data))) if type(self.data) != int else hex(self.data)) if self.data != 'N/A' else 'N/A')

    def to_buffer(self):
        return bytes([self.mid] + self.data)

    def get_log_line(self):
        return '%f,%s,%s,%d,%02x,%s\n' % (self.time, "J1587", "SM" if self.sent else "RM", self.count, self.mid, ' '.join(list(map(lambda x: "%02x" % x, list(self.data)))))

    def toJsonFormat(self):
        retval = {'time': self.time, 'mid': self.mid,
                  'data': self.getHexData(), 'message_count': self.count}
        return retval


class CANRaw:

    def __init__(self, time, can_id, data, sent=False):
        self.time = time
        self.can_id = can_id
        self.data = data
        self.sent = sent
        self.count = 1

    def get_log_line(self):
        return '%f,%s,%s,%d,%x,%s\n' % (self.time, "CAN", "SM" if self.sent else "RM", self.count, self.can_id, ' '.join(list(map(lambda x: "%02x" % x, list(self.data)))))
