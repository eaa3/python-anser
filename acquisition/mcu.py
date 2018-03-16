import serial

class Mcu():

    def __init__(self, portname):
        self.portname = portname
        self.port =serial.Serial(portname)

    def sendDefaults(self):
        pass

    def sendResetAll(self):
        string = 'RESET\n'.encode('utf-8')
        self.port.write(string)

    def sendDefaultFreq(self):
        string = 'FREQ:1@20000:2@22000:3@24000:4@26000:5@28000:6@30000:7@32000:8@34000\n'.encode('utf-8')
        self.port.write(string)

    def sendFreq(self, coilno, freq):
        string = 'FREQ' + str(coilno) + '@' + freq + '\n'
        string = string.encode('utf-8')
        self.port.write(string)

    def open(self):
        self.port.open()

    def close(self):
        self.port.close()
