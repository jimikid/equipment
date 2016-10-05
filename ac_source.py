
"""
Created on 02/26/2016, @author: sbaek
  V00
  - initial release

  V01 04/06/2016
  - ac_on(equip), ac_off(equip) are added  
"""

import time


def set_ac_source(equip, mode='LL', freq=60.0):     
    if mode=='LN':
        print '\n AC_SOURCE On.. mode: LN 120, 120, 120, 3-phase'        
        configure_voltage(equip, prog_num=98,
                                         frequency=60,
                                         current_limit=10.0,
                                         line_voltages=(120.0, 120.0, 120.0))
                                         
        equip['AC_SOURCE'].write("PROG:NAME %d" % 98)
        equip['AC_SOURCE'].write("PROG:EXEC")        
        equip['AC_SOURCE'].write("OUTPUT ON")
        time.sleep(2)

    elif mode=='LN_n10':
        print '\n AC_SOURCE On.. mode: LN %s, %s, %s, 3-phase' %(120*0.9, 120*0.9, 120*0.9)
        configure_voltage(equip, prog_num=98,
                                         frequency=60,
                                         current_limit=10.0,
                                         line_voltages=(120*0.9, 120*0.9, 120*0.9))

        equip['AC_SOURCE'].write("PROG:NAME %d" % 98)
        equip['AC_SOURCE'].write("PROG:EXEC")
        equip['AC_SOURCE'].write("OUTPUT ON")
        time.sleep(2)

    elif mode=='LL':
        print '\n AC_SOURCE On.. mode: LL 120, 120, split-phase' 
        configure_voltage(equip, prog_num=99,
                                         frequency=freq,
                                         current_limit=10.0,
                                         line_voltages=(120.0, 120.0))
                                        
        equip['AC_SOURCE'].write("PROG:NAME %d" % 99)
        equip['AC_SOURCE'].write("PROG:EXEC")        
        equip['AC_SOURCE'].write("OUTPUT ON")
        time.sleep(2)

    elif mode=='LL_p10':
        print '\n AC_SOURCE On.. mode: LL %s, %s, split-phase' %(120*1.1, 120*1.1)
        configure_voltage(equip, prog_num=97,
                                         frequency=freq,
                                         current_limit=10.0,
                                         line_voltages=(120*1.1, 120*1.1))

        equip['AC_SOURCE'].write("PROG:NAME %d" % 97)
        equip['AC_SOURCE'].write("PROG:EXEC")
        equip['AC_SOURCE'].write("OUTPUT ON")
        time.sleep(2)

    elif mode=='LL_p15':
        print '\n AC_SOURCE On.. mode: LL %s, %s, split-phase' %(120*1.15, 120*1.15)
        configure_voltage(equip, prog_num=97,
                                         frequency=freq,
                                         current_limit=10.0,
                                         line_voltages=(120*1.15, 120*1.15))

        equip['AC_SOURCE'].write("PROG:NAME %d" % 97)
        equip['AC_SOURCE'].write("PROG:EXEC")
        equip['AC_SOURCE'].write("OUTPUT ON")
        time.sleep(2)



def configure_voltage(equip, prog_num, line_voltages, frequency, current_limit):
    """Programs a voltage profile into memory on the instrument.

    INPUTS
    'prog_num'  Integer. The program number to store. The 3XX series can
                store programs at memory locations 1 through 99.
    'line_voltages'  Tupple. The line to line voltages.
    'frequency'  Float. The frequency to use. Range is 20 to 5000 Hz.
    'current_limit'  Float. The current limit. Range is 1 to 20 A.
    """
    definition = _configure_voltage(frequency=frequency,
                                         current_limit=current_limit,
                                         line_voltages=line_voltages)
                                         
    """Will program 'definition', a String, into memory at 'prog_num'."""
    fmt_definition = ",".join([x.strip() for x in definition.split(",")])
    equip['AC_SOURCE'].write("PROG:NAME %d" % prog_num)
    equip['AC_SOURCE'].write("PROG:DEF %s" % fmt_definition)

        
        
def _configure_voltage(frequency, current_limit, line_voltages, xfmr_mode=False):  # pylint: disable-msg=R0914
    """Returns a voltage configuration string which may be programmed into
    memory on the instrument.

    INPUTS
    'frequency'  Float. The frequency to use. Range is 20 to 5000 Hz.
    'current_limit'  Float. The current limit. Range is 1 to 20 A.
    'line_voltages'  Tuple of Floats. One line-to-neutral per phase. Number
                     of phases are determined by the tuple length.
    'xfmr_mode'  Boolean. If True, will force transformer-coupled mode.
                 Defaults to False.
    """
    current_limit_str = 'SOUR:CURRENT:LIMIT %s' % current_limit
    frequency_str = 'FREQUENCY,%f,' % frequency

    num_phases = len(line_voltages)
    form_str = {1:"FORM 1,", 2:"FORM 3,", 3:"FORM 3,"}[num_phases]
    voltages_template = {1:'VOLT1,%f,',
                         2:'VOLT1,%f,VOLT2,%f,VOLT3,0.0,',
                         3:'VOLT1,%f,VOLT2,%f,VOLT3,%f,'}[num_phases]
    voltages_str = voltages_template % line_voltages

    coupling_str = 'SOUR:COUPLING DIRECT,XFMRRATIO,0.0,'
    for voltage in line_voltages:
        if voltage > 150.0 or xfmr_mode:
            coupling_str = 'SOUR:COUPLING XFMR,XFMRRATIO,2.5,'
            break

    waveform_str = ""
    if form_str == 'FORM 3,':
        waveform_str = ",WAVEFORM1,1,WAVEFORM2,1,WAVEFORM3,1"

    phases = {1:(0.0, 0.0), 2:(180.0, 0.0), 3:(120.0, 240.0)}[num_phases]
    phases_str = "SOUR:PHASE2 %f,SOUR:PHASE3 %f," % phases

    template = '%(form_str)s %(coupling_str)s ' \
               '%(voltages_str)s %(phases_str)s ' \
               '%(frequency_str)s %(current_limit_str)s ' \
               '%(waveform_str)s'

    return template % locals()        
  
def ac_on(equip):  
    equip['AC_SOURCE'].write("OUTPUT ON")

def ac_off(equip):
    print '\n AC_SOURCE off'
    equip['AC_SOURCE'].write("OUTPUT OFF")





