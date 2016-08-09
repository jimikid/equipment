
"""
Created on 02/36/2016, @author: sbaek
  V00
  - initial release

  V01, 03/09/2016
  - values in item has been changed after calibration and CEC efficienci scripts
 
  V02 04/06/2016
  - Errors occur when no power transfer due to '0' value.

  V02 04/06/2016
  - Errors occur when no power transfer due to '0' value.

"""

def pm_measure(equip, show=False):
    equip['POWER_METER'].write('STAT:FILT1 FALL')
    equip['POWER_METER'].ask('STAT:EESR?')
    equip['POWER_METER'].write('COMM:WAIT 1')
    results2 = equip['POWER_METER'].ask('NUMERIC:NORMAL:VALUE?').split(',')

    '''

    #for for 'release_April_11_2016'
    item={'p_in':float(results2[2]),'p_ac_out':float(results2[13]),
          'volt_in':float(results2[0]),'amp_in':float(results2[1]),
          'amp_ac_out1':float(results2[14]),'amp_ac_out2':float(results2[15]),
          'volt_ac_out1':float(results2[16]),'volt_ac_out2':float(results2[17])}

    if (float(item['p_in'])>0) and (float(item['p_ac_out'])>0):
          item.update({'eff':100*float(results2[13])/float(results2[2])}) # /0 causes error when there is no power.
    if show:
        for i in range(len(results2)):
                print '%s, %.1f' %(i,float(results2[i]))
    '''

    #print results2
    item={'p_in':float(results2[2]),'p_ac_out':float(results2[15]),
          'volt_in':float(results2[0]),'amp_in':float(results2[1]),
          'amp_ac_out1':float(results2[18]),'amp_ac_out2':float(results2[19]),
          'volt_ac_out1':float(results2[16]),'volt_ac_out2':float(results2[17])}
    if (float(item['p_in'])>2.0) and (float(item['p_ac_out'])>2.0):
        #print 'eff'
        #print float(item['p_in']), float(item['p_ac_out'])
        #item.update({'eff': 100*float(results2[15])/float(results2[2])}) # /0 causes error when there is no power.
        item.update({'eff': 100*float(item['p_ac_out'])/float(item['p_in'])}) # /0 causes error when there is no power.
    if show:
        for i in range(len(results2)):
                print '%s, %.1f' %(i,float(results2[i]))
    #print item
    return item



    