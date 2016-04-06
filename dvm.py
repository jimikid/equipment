
"""
Created on 02/36/2016, @author: sbaek
  V00
  - initial release

  V01, 03/09/2016
  - values in item has been changed after calibration and CEC efficienci scripts
"""
import time
def measure_dc_volts(equip, range="DEF", resolution="DEF"):
    """ Will measure the DC voltage from the instrument.
    'range' is 0.1, 1, 10, 100, 1000, in volts """

    equip['DVM'].write("CONF:VOLT:DC %s, %s" % (range, resolution))
    equip['DVM'].write("INIT")

    value=equip['DVM'].ask("FETCH?")
    timestr=time.strftime(" %m/%d/%Y %I:%M:%S")
    print ' dc_volts: %.1f V at %s' %(value, timestr)
    return value


def measure_tempc(equip, range="DEF", resolution="DEF"):
    """ Will measure the DC voltage from the instrument.
    'range' is 0.1, 1, 10, 100, 1000, in volts """

    equip['DVM'].write("CONF:VOLT:DC %s, %s" % (range, resolution))
    equip['DVM'].write("INIT")

    value=equip['DVM'].ask("FETCH?")
    temp=float(value)*1000
    timestr=time.strftime(" %m/%d/%Y %I:%M:%S")
    print ' temperature : %.1f C at %s' %(temp, timestr)
    return temp









