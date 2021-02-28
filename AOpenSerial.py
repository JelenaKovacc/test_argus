import argparse
import threading
import time
import serial
import logging

# ============================ defines =========================================
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
#============================ classes =========================================

class SerialportHandler(threading.Thread):

    def __init__(self, serialport, baudrate= 115200):

            # store params
            self.serialport           = serialport
            self.baudrate             = baudrate

            # logging setup
            self.logger = logging.getLogger('SeialportHandler')
            #self.logger.info("Trying to connect to serial port:" + self.serialport)

            # local variables
            self.serialHandler        = None
            self.goOn                 = True
            self.pleaseConnect        = False
            self.dataLock             = threading.RLock()

            # initialize thread
            super(SerialportHandler, self).__init__()
            self.name                 = 'SerialportHandler@{0}'.format(self.serialport)
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

            except serial.SerialException:
                # mote disconnected, or pyserialHandler closed
                # destroy pyserial instance
                self.logger.warning("Could not open port:" + ' ' + self.serialport + '. No connection to the device could be established.')
                self.serialHandler = None
                self.goOn          = False
            except:
                self.logger.warning("Could not open port:" + ' ' + self.serialport, exc_info=True)
                self.serialHandler = None
                self.goOn          = False
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
    parser = argparse.ArgumentParser() #creating an ArgumentParser object
    parser.add_argument("serialport", help= 'Input the serial port')
    args = parser.parse_args()

    openserial = SerialportHandler(serialport=args.serialport)

    logger.info('Try to listen on serial port:' +  args.serialport)
    openserial.connectSerialPort() #connect to serial port
