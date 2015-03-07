#!/usr/bin/python
# Code sourced from AdaFruit discussion board: https://www.adafruit.com/forums/viewtopic.php?f=8&t=34922


import sys
import time
from Adafruit_I2C import Adafruit_I2C
from enum import Enum

SLAVE_ADDRESS = 0x39
COMMAND_REGISTER_SELECT = 0x80
CONTROL_REGISTER_ADDRESS = 0x00
CONTROL_REGISTER_POWERON = 0x03
CONTROL_REGISTER_POWEROFF = 0x00
TIMING_REGISTER_ADDRESS = 0x01
DATA_REGISTER_ADDRESS_FULL_LOW = 0x8c
DATA_REGISTER_ADDRESS_IR_LOW = 0x8e

class Gain(Enum):
    auto = 0
    low = 1
    high = 2
GainCommand = {Gain.low:  0x00,
               Gain.high: 0x10}
GainFactor = {Gain.auto: 0,
              Gain.low:  1,
              Gain.high: 16}

class Integration(Enum):
    fast = 0
    medium = 1
    slow = 2
IntegrationCommand = {Integration.fast:   0x00,
                      Integration.medium: 0x01,
                      Integration.slow:   0x02}
IntegrationTime = {Integration.fast:   13.7,
                   Integration.medium: 101,
                   Integration.slow:   402}
IntegrationFactor = {Integration.fast:   0.034,
                     Integration.medium: 0.252,
                     Integration.slow:   1}
IntegrationMax = {Integration.fast:   5047,
                  Integration.medium: 37177,
                  Integration.slow:   65535}

class TSL2561:
    i2c = None

    def __init__(self, address=SLAVE_ADDRESS,
                       gain=Gain.high, # device default per datasheet
                       integration=Integration.slow, # device default per datasheet
                       debug=False,
                       package='T'):
        self.i2c = Adafruit_I2C(address)
        self.address = address
        self.debug = debug
        self.gain = gain
        self.integration = integration
        self.package = package
# enable the device
        self.i2c.write8(COMMAND_REGISTER_SELECT | CONTROL_REGISTER_ADDRESS,
                        CONTROL_REGISTER_POWERON)

    def setGain(self, gain):
        """ Set the gain """
        if gain == Gain.auto:
            gain = Gain.high
        if gain != self.gain:
            self.gain=gain;      # save gain for calculation
            self.updateTiming()

    def setIntegrationTime(self, time):
        """ Set the integration time """
        if time != self.integration:
            self.integration = time; # save time for calculation
            self.updateTiming()

    def updateTiming(self):
        """ Update the new gain/integration timing data on the device """
        self.i2c.write8(COMMAND_REGISTER_SELECT | TIMING_REGISTER_ADDRESS,
                        GainCommand[self.gain] | IntegrationCommand[self.integration])
        time.sleep(1.5*IntegrationTime[self.integration]/1000)

    def readWord(self, reg):
        """Reads a word from the I2C device"""
        try:
            wordval = self.i2c.readU16(reg)
            if self.debug:
                print(("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address,
                                                                               wordval & 0xFFFF,
                                                                               reg)))
            return wordval
        except IOError:
            print(("Error accessing 0x%02X: Check your I2C address" % self.address))
            return -1


    def readFull(self):
        """Reads visible+IR diode from the I2C device"""
        return self.readWord(DATA_REGISTER_ADDRESS_FULL_LOW);

    def readIR(self):
        """Reads IR only diode from the I2C device"""
        return self.readWord(DATA_REGISTER_ADDRESS_IR_LOW);

    def readLux(self, gain = Gain.auto):
        """Grabs a lux reading either with autoranging (Gain.auto) or with a specified gain (Gain.low, Gain.high)"""
        if gain in (Gain.low, Gain.high):
            self.setGain(gain) # low/high Gain
            ambient = self.readFull()
            IR = self.readIR()
        else: # auto gain
            self.setGain(Gain.high) # first try highGain
            intMax = IntegrationMax[self.integration]
            ambient = self.readFull()
            if ambient < intMax:
                IR = self.readIR()
            if ambient >= intMax or IR >= intMax: # value(s) exeed(s) datarange
                self.setGain(Gain.low)
                ambient = self.readFull()
                IR = self.readIR()

        ambient *= 16/GainFactor[self.gain]
        IR *= 16/GainFactor[self.gain]

        ratio = IR / float(ambient)

        if self.debug:
            print("IR Result", IR)
            print("Ambient Result", ambient)

        if self.package.upper() == 'CS':
            if ratio >= 0 and ratio <= 0.52:
                lux = (0.0315 * ambient) - (0.0593 * ambient * (ratio**1.4))
            elif ratio <= 0.65:
                lux = (0.0229 * ambient) - (0.0291 * IR)
            elif ratio <= 0.80:
                lux = (0.0157 * ambient) - (0.018 * IR)
            elif ratio <= 1.3:
                lux = (0.00338 * ambient) - (0.0026 * IR)
            else:
                lux = 0
        else:
            if ratio >= 0 and ratio <= 0.50:
                lux = (0.0304 * ambient) - (0.062 * ambient * (ratio**1.4))
            elif ratio <= 0.61:
                lux = (0.0224 * ambient) - (0.031 * IR)
            elif ratio <= 0.80:
                lux = (0.0128 * ambient) - (0.0153 * IR)
            elif ratio <= 1.3:
                lux = (0.00146 * ambient) - (0.00112 * IR)
            else:
                lux = 0

        return lux

if __name__ == "__main__":
    tsl=TSL2561()
    print(tsl.readLux())
#print "LUX LOW GAIN ", tsl.readLux(1)
#print "LUX AUTO GAIN ", tsl.readLux()
