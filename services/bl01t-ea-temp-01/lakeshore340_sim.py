#!/usr/bin/env python3

import socket
import sys
from random import random, randrange


class ls340data(object):
    """
    Class to deal with return data for the lakeshore 340 simulation.
    For each command, this class generates an appropriate response.
    The class can also hold state.

    At the moment setting parameter has no effect on what is read back.
    The numbers read back are all random numbers.
    """

    def __init__(self):
        self.__setp = 0.0
        self.__range = 0
        self.__ramponoff = 0
        self.__ramprate = 0.0
        self.__mout = 0.0
        self.__p = 0.0
        self.__i = 0.0
        self.__d = 0.0
        self.__c_mode = 1
        self.__aout = 0.0

    def getCMODE(self):
        return self.__c_mode

    def getAOUT(self):
        return self.returnRateTypeString(self.__aout)

    def setSETP(self, val):
        self.__setp = float(val)

    def setRANGE(self, val):
        ival = int(val)
        if (ival >= 0) and (ival <= 5):
            self.__range = ival

    def setRAMP(self, onoff, val):
        ionoff = int(onoff)
        fval = float(val)
        if (ionoff == 0) or (ionoff == 1):
            self.__ramponoff = ionoff
            self.__ramprate = fval

    def setMOUT(self, val):
        fval = float(val)
        if (fval >= 0) and (fval <= 100.0):
            self.__mout = fval

    def sETPID(self, p, i, d):
        self.__p = float(p)
        if i is not None:
            self.__i = float(i)
        if d is not None:
            self.__d = float(d)

    def setC_MODE(self, c_mode):
        ic_mode = int(c_mode)
        if (ic_mode > 0) and (ic_mode < 7):
            self.__c_mode = ic_mode

    def getIDN(self):
        return "LSCI,MODEL340,123456,02032001"

    def getHTR(self):
        return self.returnRateTypeString(0.0)

    def getSETP(self):
        return self.returnTempTypeString()

    def getKRDG(self):
        return self.returnTempTypeString()

    def getSRDG(self):
        return self.returnTempTypeString()

    def getRANGE(self):
        return self.__range

    def getRAMP(self):
        rand1 = randrange(0, 2, 1)
        return str(rand1) + "," + self.returnRateTypeString(self.__ramprate)

    def getMOUT(self):
        return self.returnRateTypeString(0.0)

    def getPID(self):
        rand1 = randrange(0, 1001, 1)
        rand2 = randrange(0, 10, 1)
        rand3 = randrange(0, 1001, 1)
        rand4 = randrange(0, 10, 1)
        rand5 = randrange(0, 1001, 1)

        if rand1 == 1000:
            rand2 = 0

        if rand3 == 1000:
            rand4 = 0

        return (
            str(rand1)
            + "."
            + str(rand2)
            + ","
            + str(rand3)
            + "."
            + str(rand4)
            + ","
            + str(rand5)
        )

    def getC_MODE(self):
        rand1 = randrange(1, 7, 1)
        return str(rand1)

    def getTUNEST(self):
        rand1 = randrange(0, 2, 1)
        return str(rand1)

    def returnRateTypeString(self, val):
        """
        Returns a string number in this format: 000.0
        """

        result = None
        sign = 0
        if val < 0:
            val = abs(val)
            sign = 1

        if val <= 9.9:
            result = "00" + str(val)
        elif (val <= 99.9) and (val >= 10.0):
            result = "0" + str(val)
        elif val >= 100.0:
            result = str(val)

        if sign == 1:
            result = "-" + result

        return result

    def returnTempTypeString(self):
        """
        Returns a string in this format: +000.000E+0
        The signs are random.
        All numbers are random.
        """
        rand1 = randrange(0, 101, 1)
        rand2 = randrange(0, 101, 1)
        rand3 = randrange(0, 10, 1)

        sign = random()
        signstr1 = "-"
        if sign < 0.5:
            signstr1 = "+"

        sign = random()
        signstr2 = "-"
        if sign < 0.5:
            signstr2 = "+"

        return signstr1 + str(rand1) + "." + str(rand2) + "E" + signstr2 + str(rand3)


class ls340:
    Terminator = "\r\n"

    def __init__(self):
        """Constructor."""

        print("Initialising ls340 simulator, V2.0 2024.01.21")

        self.__ls340data = ls340data()

        # Valid channel numbers
        self.__channels = ["0", "1", "2", "3"]

    def diagnosticLevel(self):
        return 1

    def start_ip(self, port, server_ip="0.0.0.0"):
        """Start the simulator listening on the given port."""

        server_socket = socket.socket()  # get instance
        # look closely. The bind() function takes tuple as argument
        server_socket.bind((server_ip, port))  # bind host address and port together

        # configure how many client the server can listen simultaneously
        server_socket.listen(2)
        print("Listening on port: " + str(port))
        conn, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))

        try:
            while True:
                data = conn.recv(1024)
                if len(data) == 0:
                    continue
                # decode and remove the terminator
                data = data.decode("utf-8")[:-2]

                print("RECEIVED: %s" % data)

                reply = self.reply(data)
                if reply is not None:
                    reply = str(reply).encode("utf-8") + self.Terminator.encode("utf-8")
                    print("RESPONSE: %s" % reply)
                    conn.send(reply)

        except Exception:
            print("Connection closed.")
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            server_socket.close()
            raise

    def covered(self, command):
        pass

    def reply(self, command):
        """This function must be defined. It is called by the serial_sim system
        whenever an asyn command is send down the line. Must return a string
        with a response to the command or None."""

        result = None

        if self.diagnosticLevel() > 0:
            print("ls340::reply. command: " + repr(command))

        if command == "*IDN?":
            result = self.__ls340data.getIDN()
            self.covered("*IDN?")

        elif command == "HTR?":
            result = self.__ls340data.getHTR()
            self.covered("HTR?")

        elif command.startswith("CMODE?"):
            result = self.__ls340data.getCMODE()
            self.covered("CMODE?")

        elif command.startswith("AOUT?"):
            result = self.__ls340data.getAOUT()
            self.covered("AOUT?")

        elif command.startswith("SETP?"):
            result = self.__ls340data.getSETP()
            self.covered("SETP?")

        elif command.startswith("KRDG?"):
            chan = command.split(" ")[1]
            if self.isChannelNumberOK(chan):
                result = None
            else:
                result = self.__ls340data.getKRDG()
            self.covered("KRDG?")

        elif command.startswith("SRDG?"):
            chan = command.split(" ")[1]
            if self.isChannelNumberOK(chan):
                result = None
            else:
                result = self.__ls340data.getSRDG()
            self.covered("SRDG?")

        elif command == "RANGE?":
            result = self.__ls340data.getRANGE()
            self.covered("RANGE?")

        elif command.startswith("RAMP?"):
            result = self.__ls340data.getRAMP()
            self.covered("RAMP?")

        elif command.startswith("MOUT?"):
            result = self.__ls340data.getMOUT()
            self.covered("MOUT?")

        elif command.startswith("PID?"):
            result = self.__ls340data.getPID()
            self.covered("PID?")

        elif command.startswith("C_MODE?"):
            result = self.__ls340data.getC_MODE()
            self.covered("C_MODE?")

        elif command == "TUNEST?":
            result = self.__ls340data.getTUNEST()
            self.covered("TUNEST?")

        # Set functions

        elif command.startswith("SETP"):
            val = command.split(",")[1]
            self.__ls340data.setSETP(val)
            self.covered("SETP")

        elif command.startswith("RANGE "):
            val = command.split(" ")[1]
            self.__ls340data.setRANGE(val)
            self.covered("RANGE")

        elif command.startswith("RAMP "):
            val_onoff = command.split(",")[1]
            val_rate = command.split(",")[2]
            self.__ls340data.setRAMP(val_onoff, val_rate)
            self.covered("RAMP")

        elif command.startswith("MOUT "):
            val = command.split(",")[1]
            self.__ls340data.setMOUT(val)
            self.covered("MOUT")

        elif command.startswith("PID "):
            vals = command.split(",")
            val_p = vals[1]
            val_i = None
            val_d = None
            if len(vals) > 2:
                val_i = vals[2]
            if len(vals) > 3:
                val_d = vals[3]
            self.__ls340data.sETPID(val_p, val_i, val_d)
            self.covered("PID_P")
            if val_i is not None:
                self.covered("PID_I")
            if val_d is not None:
                self.covered("PID_D")

        elif command.startswith("C_MODE "):
            val = command.split(",")[1]
            self.__ls340data.setC_MODE(val)
            self.covered("C_MODE")

        else:
            # Return nothing in the case of a syntax error (that's what the lakeshore does)
            result = None
            if self.diagnosticLevel() > 0:
                print("ls340::reply. Command not supported by simulation.")

        if self.diagnosticLevel() > 0:
            print("ls340::reply. result: " + repr(command))

        return result

    def isChannelNumberOK(self, channel):
        """
        Check that the channel number is in the __channels list
        Returns True (channel is valid) or False (channel is not valid).
        """
        chanError = 0
        for c in self.__channels:
            if channel != c:
                chanError = chanError + 1
        if chanError == 4:
            return True
        else:
            return False

    def initialise(self):
        """Called by the framework when the power is switched on."""
        print("ls340::initialise. Power on.")


if __name__ == "__main__":
    # little test function that runs only when you run this file
    dev = ls340()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5401
    dev.start_ip(port)
