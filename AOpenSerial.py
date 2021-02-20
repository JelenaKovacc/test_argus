import threading
import time
import serial
import serial.tools.list_ports
import argparse
import logging

class SerialportHandler(threading.Thread):

    def __init__(self, serialport, baudrate= 115200):

            # store params
            self.serialport           = serialport
            self.baudrate             = baudrate

            # local variables
            self.serialHandler        = None
            self.goOn                 = True
            self.pleaseConnect        = False
            self.dataLock             = threading.RLock()

            # initialize thread
            super(SerialportHandler, self).__init__()
            self.name                 = 'SerialportHandler@{0}'.format(self.serialport)
            self.logger = logging.getLogger(self.name)
            self.start()

    def run(self):
        while self.goOn:
            try:
                with self.dataLock:
                    pleaseConnect = self.pleaseConnect

                if pleaseConnect:
                    # open serial port
                    self.serialHandler = serial.Serial(self.serialport, baudrate=self.baudrate)

                    # read byte
                    while True:
                        waitingbytes   = self.serialHandler.inWaiting()
                        if waitingbytes != 0:
                            c = self.serialHandler.read(waitingbytes)
                            print(c)
                            time.sleep(0.2)

            except:
                # mote disconnected, or pyserialHandler closed
                # destroy pyserial instance
                self.serialHandler = None

            # wait
            time.sleep(1)
    #======================== public ==========================================

    def connectSerialPort(self):
        with self.dataLock:
            self.pleaseConnect = True

    def disconnectSerialPort(self):
        with self.dataLock:
            self.pleaseConnect = False
        try:
            self.serialHandler.close()
        except:
            pass

    def close(self):
        self.goOn            = False
    #======================== public ==========================================

#============================ main ============================================

if __name__ == '__main__':

    # parse args
    parser = argparse.ArgumentParser(description='Input the serial port') #creating an ArgumentParser object
    parser.add_argument("--serialport", nargs="?", default="COM3")
    args = parser.parse_args()


    openserial = SerialportHandler(serialport=args.serialport)
    openserial.connectSerialPort() #connect to serial port
