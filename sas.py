
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
    print ' adjust SAS at %.1f' %float(VOLT)
    VOLT_set=VOLT
    sas_fixed(equip, CURR=CURR, VOLT=VOLT_set)
    time.sleep(3)
    item=pm.pm_measure(equip)
    step= float(VOLT)-float(item['volt_in'])
    #print step, float(VOLT), float(item['volt_in'])
    VOLT_set=VOLT_set+step
    print ' set %.2f' %VOLT_set
    sas_fixed(equip, CURR=CURR, VOLT=VOLT_set)
 
            
def sas_pcu_boot(equip, para, CURR=0, VOLT=0, boot_up=1.0):
    ''' turn on SAS and wait until PCU produce power '''
    msg='\n initizlize SAS at %.1fV and %.1fA' %(VOLT, CURR)
    print msg
    para['log'] +=msg
    item={}
    
    sas_fixed(equip, CURR, VOLT)
    item=pm.pm_measure(equip)

    if boot_up==1.0:
        ## check boot-up
        msg= ' boot up at a full load \n'
        print msg
        para['log'] +=msg
        item=check_boot(equip, iteration=60)

    else:
        #boot up with pt 2 at the load condition given
        check_boot(equip, iteration=10)
        for i in range(3):
            time.sleep(2)
            sc.command_p(boot_up, para, equip, adj=False, delay=1, show=False) #taking data from pm takes time.
            print ' boot up at %s' %boot_up
            ## check boot-up
            item=check_boot(equip, iteration=20)

    sas_fixed_adj(equip, CURR, VOLT)
    return item
   
def check_boot(equip, iteration=60):
    item=pm.pm_measure(equip)
    for i in range(iteration):
        time.sleep(1.0)
        if (item['p_ac_out']>20.0):  #30% of the rated power
            time.sleep(3)
            print ' PCU is running ...'
            temp=dvm.measure_tempc(equip)
            item.update({'Temp':temp})
            item.update({'scan_time':time.strftime("%I:%M:%S")})
            item.update(pm.pm_measure(equip))
            break
        else:
            item=pm.pm_measure(equip, show=False)  # need to check the list from pm
            print ' . '
    time.sleep(3)
    return item


def sas_off(equip):
    time.sleep(2)
    print '\n SAS off...'
    equip['SAS'].write('OUTP:STAT OFF')  
   

