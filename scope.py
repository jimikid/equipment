"""
Created on 02/26/2016, @author: sbaek
  V00
    - initial release
"""

#from data_aq_lib.equipment.file_utils import unique_file
import os
import time
import pandas as pd
import data_aq_lib.measurement.measurements as mm   
#import data_aq_lib.analysis.waveforms_functions as wf
import data_aq_lib.analysis.waveform_func as wf
import visa
from collections import OrderedDict
results2=OrderedDict()

class scope:
    """
           __INIT__     
           __STR__
    """    

    def __init__(self, data_path):
        self.return_str= ''
        self.data_path=data_path
        self.results, self.df = pd.DataFrame(), pd.DataFrame()

        rm = visa.ResourceManager()
        list_equip=rm.list_resources()
        for item in list_equip:
            print item
            if 'GPIB' in item:   #check equipment by gpib
                eq=rm.open_resource(item)
                eq.write('*IDN?')
                c=eq.read()
                print c
                if 'DSO-X' in c:
                    #cata='SCOPE'
                    #print item+' ->  set '+cata
                    #item.update({cata:eq})
                    #item[cata].write('*IDN?')
                    #print item[cata].read()
                    self.eq=eq

                #else: print ' scope is not configuable'
        #self.eq= self.item.eq

    
    def __str__(self):
        self.return_str= '\n\n -- class scope_measurement --' 
        self.return_str += '\n data_path : %s  ' %self.data_path
        return self.return_str       


    def initialize(self, trig, ch, reset='Off'):
        print '\n initizlize scope...'
        # Initialize scope here   
        if reset == 'On':            
            print ' - reset scope' 
            reset()
            time.sleep(1)
        
        print ' - attenuation factor set up' 
        if 1 in ch: self.set_probe_attenuation_factor(1,100)
        if 2 in ch: self.set_probe_attenuation_factor(2,1000)
        if 3 in ch: self.set_probe_attenuation_factor(3,10)
        if 4 in ch: self.set_probe_attenuation_factor(4,10)    
    
        time.sleep(1)
        #self.set_auto_scale()   #Caution! auto scale can reset the configuration made previously    b

        timescale=5e-3        
        self.set_timebase_scale_factor(timescale)
        
        if trig=='EXT':
            self.set_trig(trig)
            print ' - set trigger : %s' %trig  
        else:
            self.set_trig(int(trig))
            print ' - set trigger : %s' %trig  
        time.sleep(1)

        print ' - set input impedance'     
        #def set_probe(self, channel, impedance):
        if 1 in ch: self.set_probe(1, 'FIFT')
        if 2 in ch: self.set_probe(2, 'FIFT')    
        if 3 in ch: self.set_probe(3, 'ONEM')
        if 4 in ch: self.set_probe(4, 'ONEM')
         
        print ' - set units'                
        #def set_channel_Unit(self, channel,unit):
        #'VOLT','AMP'
        if 3 in ch: self.set_channel_UnitAmp(3)
        if 4 in ch: self.set_channel_UnitAmp(4)      
        time.sleep(1)   
        
        print ' - display all channels'       
        #def set_channel_BW_limit(self, channel):
        for i in ch:
            self.display_channel(i)
        time.sleep(1)         
        self.set_offset_all(0) 
        time.sleep(1)
  
   
    def get_data(self, chan, NumPt):
        w=[]        
        t,v=self.wave(chan, NumPt) # minimum 100
        w.append(t)
        w.append(v)
        return w    

                      
    def DC2AC_measurement(self, filename, pts_deg, NumPt, TimeDiv, ch_names):
        waveforms_list=[]
        ''' collect data'''
        d=[]
        for deg in pts_deg:
            TimeShift=deg/360/60.0
            results, self.waveforms = self.get_waveforms(filename, deg, NumPt, TimeDiv, TimeShift, ch_names)
            waveforms_list.append(self.waveforms)
            results.update({'deg':deg, 'NumPt':NumPt, 'TimeDiv':TimeDiv,  'freq':results['freq']})
            d.append(results)     

        df=pd.DataFrame(d)    
        df=df.set_index([range(len(df))])    #set index. Without this,  index numbers are all 'zero'
        file_name = self.data_path+'%s_DC2AC_.csv' % filename
        print "\n Data will be stored as %s\n" % file_name
        df.to_csv(file_name)
          
        return waveforms_list
 
    def get_waveforms(self, filename, deg, NumPt, TimeDiv, TimeShift, ch_names):
        self.NumPt, self.TimeDiv, self.TimeShift, self.ch_names = NumPt, TimeDiv, TimeShift, ch_names
        w=[]

        results=dict()
        if ch_names==None:
            ch_names=['ch1','ch2','ch3','ch4']
        SCOPE=self.eq

        print '\n---------------------------------------------------------------' 
        print '--- Deg %s, shift %.1f us'  %(str(deg), TimeShift*1e6)
        self.set_timebase_delay_factor(TimeShift)
        self.set_timebase_scale_factor(TimeDiv)
           
        time.sleep(1)
        self.set_stop()
    
        print ' - save data with %s pts' %str(NumPt)
        for i in range(4):
            w.append(self.get_data(i+1, NumPt))
        SCOPE.write(':RUN')   

        waveforms=[w[0][0],w[0][1],w[1][1],w[2][1],w[3][1]]

        data_dict=OrderedDict({'t': waveforms[0]})  #put 't' first to put htat in the first colume to work with wave_func.py
        data_dict.update({ch_names[0]:waveforms[1], ch_names[1]:waveforms[2], ch_names[2]:waveforms[3], ch_names[3]:waveforms[4]})
        df=pd.DataFrame(data_dict)

        file_name=self.data_path+'%s_scope_%s.csv' % (filename, str(deg))
        print "\n save as %s" % file_name
        df.to_csv(file_name)

        waves=wf.waveforms(df=df,  filepath=self.data_path)
        rms=waves.get_rms()
        avg=waves.get_avg()
        pkpk=waves.get_pkpk()
        zeros= waves.get_zero_crossing(waves.get_labels()[2])
        freq = waves.get_freq(waves.get_labels()[2], zeros)
        print ' %.1f kHz' %(freq/1000)
        waves.plot_all()

        rms_dict={ch_names[0]+'_rms':rms[0], ch_names[1]+'_rms':rms[1],
                    ch_names[2]+'_rms':rms[2], ch_names[3]+'_rms':rms[3]}
        avg_cit={ch_names[0]+'_avg':avg[0] , ch_names[1]+'_avg':avg[1],
                    ch_names[2]+'_avg':avg[2] , ch_names[3]+'_avg':avg[3] }

        results.update(rms_dict)
        results.update(avg_cit)
        results.update({'freq':freq})
        return results, waveforms

    def reset(self):
        self.eq.write('*RST')
    
    def set_probe_attenuation_factor(self, channel, attenuation):
        self.eq.write(':CHAN%s:PROBE %s' % (channel, attenuation))    
    
    def set_auto_scale(self):
        print ' - autoscale' 
        self.eq.write(':AUToscale')
 
    def set_probe(self, channel, impedance):       
        self.eq.write(':CHAN%s:IMP %s' % (channel, impedance))
    #    
    def set_channel_UnitAmp(self, channel):
        self.eq.write(':CHAN%s:UNIT AMP' % channel)
    #
    def set_timebase_scale_factor(self, timebase_scale):
        print ' - set time scale %s ms' %(timebase_scale*1000) 
        self.eq.write(':TIM:SCAL %s' % timebase_scale)
    
    def set_trig(self, channel):
        #<source> ::= {CHANnel<n> | EXTernal | LINE | WGEN} for the DSO models
        if channel=='EXT':
            self.eq.write(':TRIG:EDGE:SOUR EXT')
        else:
            self.eq.write(':TRIG:EDGE:SOUR CHAN%s'  % str(channel))
       
    def display_channel(self, channel):
        self.eq.write(':CHAN%s:DISP ON' % channel)
    #    
    def set_channel_Invert(self, channel):
        self.eq.write(':CHAN%s:INV ON' % channel)       
    
    def set_stop(self):
        self.eq.write(':STOP')

    def set_offset_all(self, offset):
        self.eq.write(':CHAN1:OFFS %s' % offset)
        self.eq.write(':CHAN2:OFFS %s' % offset)
        self.eq.write(':CHAN3:OFFS %s' % offset)
        self.eq.write(':CHAN4:OFFS %s' % offset)


    def set_timebase_delay_factor(self, timebase_delay):
        self.eq.write(':TIM:DEL %s' % timebase_delay)
        
    def wave(self, channel, num_of_points='MAX', filename=None):
        """Record one channel of data from oscilloscope."""
        #self.eq['SCOPE'].set_timeout(5 * 30)
        # self._write('WAV:FORMAT BYTE')
        # self._write('WAV:FORMAT WORD')
        # self._write('WAV:BYTEORDER MSBF')

        # self._write('WAV:UNSIGNED 1') # Return unsigned numbers
        self.eq.write('WAV:FORMAT ASC')

        # It appears that the oscilloscope returns 1 less than requested, therefore bump up the request by 1.
        if type(num_of_points) == int:
            num_of_points += 1
        if channel == 'MATH':
            #print 'WAV:SOURCE MATH'
            self.eq.write('WAV:SOURCE MATH')
        else:
            #print 'WAV:SOURCE CHANNEL%s' % channel
            self.eq.write('WAV:SOURCE CHANNEL%s' % channel)
        self.eq.write('WAV:POINTS %s' % num_of_points)

        data = self.eq.ask('WAV:DATA?')
        ydata = data[10:]
        ydata = map(float, ydata.split(','))

        wave_preamble = self.eq.ask('WAV:PRE?')
        preamble = [float(v) for v in wave_preamble.split(',')]
        format_type, ttype, points, count, xincrement, xorigin, xreference, yincrement, yorigin, yreference = preamble
        xdata = [(x - xreference) * xincrement + xorigin for x in range(int(points))]
        #self.restore_timeout()

        return xdata, ydata
