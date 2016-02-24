
"""
Created on 02/26/2016, @author: sbaek
  V00
  - initial release   
"""

def sas_fixed(equip, CURR=0, VOLT=0):
    channel_list='(@1)'  
    equip['SAS'].write('SOURCE:CURR:MODE FIX,%s' % channel_list)
    equip['SAS'].write('SOURCE:CURR %s, %s' % (CURR, channel_list))
    equip['SAS'].write('SOURCE:VOLT %s, %s' % (VOLT, channel_list))
    equip['SAS'].write('OUTPUT ON')
    
 




















   
        
def sas_up(self, SAS_volt, SAS_amp):
    print '\n initizlize SAS ... at %.0fVdc' %(SAS_volt)  
    self.eq['SAS'].select_fixed(SAS_volt, SAS_amp)
    ## check boot-up 
    for i in range(60):
        time.sleep(1.0)
        meas_pm = self.eq['POWER_METER'].measurement(integrate=0.0)
        if (meas_pm.dc_watts_1>80.0):
            time.sleep(5.0)
            m1=mm.measurement(self.par, self.eq)     
            data=m1.measure_DC2AC()
            print data['volt_in']
            flag='up'
            break      
        else:flag='down'        
    if flag=='down':        
        print '\n failed to boot up, flag down'
        self.shutdown()
    return flag

def sas_soft_up(self, SAS_volt, SAS_amp):
    print '\n soft bootup'
    print '\n initizlize SAS ... at %.0fVdc' %(SAS_volt)  
    self.eq['SAS'].select_fixed(SAS_volt, SAS_amp)
    time.sleep(5.0)
    
    flag='down'
    while (flag=='down'):                
        try:
            time.sleep(5.0)
            #print flag
            self.pcu.debugger_cmd('pt 2\r')  
            time.sleep(5.0)                
            print '\n command p 40\r' 
            self.pcu.debugger_cmd('p 40\r')      
            flag='up'
            #print flag                
        except : pass
    
    time.sleep(2.0)
    self.eq['init'].ac_source_up(mode=self.par['ac_mode'], freq=60.0)

    flag='down'
     ## check boot-up 
    for i in range(60):
        time.sleep(1.0)
        meas_pm = self.eq['POWER_METER'].measurement(integrate=0.0)
        if (meas_pm.dc_watts_1>30.0):
            time.sleep(5.0)
            m1=mm.measurement(self.par, self.eq)     
            data=m1.measure_DC2AC()
            print data['volt_in']
            flag='up'
            break      
        else:flag='down'        
    if flag=='down':        
        print '\n failed to boot up, flag down'
        self.shutdown()
    return flag
    
    
    
def sas_down(self):
    time.sleep(2)
    print ' SAS off...'
    self.eq['SAS'].off()    

def ac_source_up(self, mode='LL', freq=60.0):     
    if mode=='LN':
        print '\n AC_SOURCE On.. mode: LN 120, 120, 120, 3-phase'        
        self.eq['AC_SOURCE'].configure_voltage(prog_num=98,
                                         frequency=60,
                                         current_limit=10.0,
                                         line_voltages=(120.0, 120.0, 120.0))
        self.eq['AC_SOURCE'].exec_program(98)
        self.eq['AC_SOURCE'].on()
        time.sleep(2)          

    else :
        print '\n AC_SOURCE On.. mode: LL 120, 120, split-phase' 
        self.eq['AC_SOURCE'].configure_voltage(prog_num=99,
                                         frequency=freq,
                                         current_limit=10.0,
                                         line_voltages=(120.0, 120.0))
                                        
        self.eq['AC_SOURCE'].exec_program(99)
        self.eq['AC_SOURCE'].on()
        time.sleep(2)             
    """Programs a voltage profile into memory on the instrument.
  
    INPUTS
    'prog_num'  Integer. The program number to store. The 3XX series can
                store programs at memory locations 1 through 99.
    'line_voltages'  Tupple. The line to line voltages.
    'frequency'  Float. The frequency to use. Range is 20 to 5000 Htry:self.pcu.close()  
    except:passz.
    'current_limit'  Float. The current limit. Range is 1 to 20 A.
    
            
    INPUT
    'prog_num'  Integer. The program number to execute. The 3XX series can
                execute programs at memory locations 1 through 99.
                
    """    
  
       
def ac_source_down(self):
    time.sleep(5)
    print ' AC_SOURCE off...'
    self.eq['AC_SOURCE'].off()   

def power_meter_up(self):        
    para=dict()        
    para['volt_range_ac'], para['current_range_ac']=150, 5
    para['volt_range_dc'], para['current_range_dc']=60, 10

    self.eq['POWER_METER'].init(ac_voltage=(120,120),
                     num_channels=3,
                     mode='Efficiency',
                     degauss=False,
                     use_500_hz_ac_filter=False)
                     
    self.eq['POWER_METER'].ac_range(max_voltage=para['volt_range_ac'], max_current=para['current_range_ac'])
    self.eq['POWER_METER'].dc_range(max_voltage=para['volt_range_dc'], max_current=para['current_range_dc']) 
    self.eq['POWER_METER'].set_update_rate(250)
    self.eq['POWER_METER'].ac_line_filter('off')
    self.eq['POWER_METER'].averaging('off')           


def shutdown(self):
    print '\n ** shutdown **'       
    try:self.pcu.close()  
    except:pass
    self.sas_down()
    self.ac_source_down()



