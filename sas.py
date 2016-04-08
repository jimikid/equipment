
"""
Created on 02/26/2016, @author: sbaek
  V00
  - initial release   
"""
#
import sys, time
from os.path import abspath, dirname
sys.path.append(dirname(dirname(dirname(__file__))))
sys.path.append('%s/data_aq_lib' % (dirname(dirname(dirname(__file__)))))

import data_aq_lib.equipment.power_meter as pm
import data_aq_lib.equipment.dvm as dvm
from data_aq_lib.measurement import serial_commands as sc
import data_aq_lib.equipment.ac_source as ac


def sas_fixed(equip, CURR=0, VOLT=0):
    channel_list='(@1)'  
    equip['SAS'].write('SOURCE:CURR:MODE FIX,%s' % channel_list)
    equip['SAS'].write('SOURCE:CURR %s, %s' % (CURR, channel_list))
    equip['SAS'].write('SOURCE:VOLT %s, %s' % (VOLT, channel_list))
    equip['SAS'].write('OUTPUT ON')


def sas_fixed_adj(equip, CURR=0, VOLT=0):  
    VOLT_set=VOLT
    time.sleep(2.0)
    item=pm.pm_measure(equip)
    step= float(VOLT)-float(item['volt_in'])
    VOLT_set=VOLT_set+step
    sas_fixed(equip, CURR=CURR, VOLT=VOLT_set)
 
            
def sas_pcu_boot(equip, CURR=0, VOLT=0):
    ''' turn on SAS and wait until PCU produce power '''
    print '\n initizlize SAS at %.0fV and %.0fA' %(VOLT, CURR)
    item={}
    
    sas_fixed(equip, CURR, VOLT)
    item=pm.pm_measure(equip)
    
    ## check boot-up
    for i in range(60):
        time.sleep(1.0)
        if (item['p_ac_out']>100.0):
            temp=dvm.measure_tempc(equip)
            item.update({'Temp':temp})
            timestr=time.strftime("%I:%M:%S")
            datestr=time.strftime(" %m/%d/%Y")
            item.update({'scan_time':timestr, 'scan_date':datestr})
            item.update(pm.pm_measure(equip))  
            break    
        else:
            item=pm.pm_measure(equip)
            print ' . '
    return item
   
    
def sas_off(equip):
    time.sleep(2)
    print '\n SAS off...'
    equip['SAS'].write('OUTP:STAT OFF')  
   

