
"""
Created on 02/36/2016, @author: sbaek
  V00
  - initial release    
"""

def pm_measure(equip):
    equip['POWER_METER'].write('STAT:FILT1 FALL')        
    equip['POWER_METER'].ask('STAT:EESR?')
    equip['POWER_METER'].write('COMM:WAIT 1')
    results2 = equip['POWER_METER'].ask('NUMERIC:NORMAL:VALUE?').split(',')
    #results2 = equip['POWER_METER'].ask('NUMERIC:NORMAL:ITEM?')
    #item=OrderedDict()
    item={'p_in':float(results2[2]),'p_ac_out':float(results2[11]),
          'volt_in':float(results2[0]),'amp_in':float(results2[1]),
          'amp_ac_out1':float(results2[14]),'amp_ac_out2':float(results2[15]),
          'volt_ac_out1':float(results2[12]),'volt_ac_out2':float(results2[13]),
          'eff':100*float(results2[11])/float(results2[2])}   

    return item












