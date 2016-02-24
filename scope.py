"""
Created on 02/26/2016, @author: sbaek
  V00
    - initial release
"""

from data_aq_lib.equipment.file_utils import unique_file
import os
import time
import pandas as pd
import data_aq_lib.measurement.measurements as mm   
import data_aq_lib.analysis.waveforms_functions as wf
import time
results2=dict()

class scope:
    """
           __INIT__     
           __STR__      
           
    inputs
            para=                - type:dict
            equip=                - type:dict  
            
    """    
    
    def __init__(self, para, equip):              
        self.return_str= ''   
        self.par=para
        self.eq=equip
        self.results, self.df = pd.DataFrame(), pd.DataFrame()
        self.flag='up'        
        
        try:self.pcu=self.eq['pcu']
        except:pass
    
    def __str__(self):
        self.return_str= '\n\n -- class scope_measurement --' 
        self.return_str += '\n data_path : %s  ' %self.par['data_path']
        self.return_str += '\n source_path : %s  ' %self.par['source_path']
        return self.return_str       
 
              
    def initialize(self, trig='4', ch=(1,2,3,4), reset='Off'):
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
    
        #Caution! auto scale can reset the configuration made previously        
        self.set_auto_scale() 
        time.sleep(1)
        
        timescale=5e-3        
        self.set_timebase_scale_factor(timescale)
        
        if trig=='EXT':
            self.set_trig(trig)
            print ' - set trigger : %s' %trig  
        else:
            self.set_trig(int(trig))
            print ' - set trigger : %s' %trig  
        time.sleep(1) 
        #scope.set_trig(4)   
    
        
        #print ' - set BW On ch 1,2,3,4' 
        print ' - set BW Off' 
    #    scope.set_channel_BW_limit(1)
    
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
  
   
    def get_data(self, chan):
        w=[]        
        t,v=self.wave(chan, self.par['NumPt']) # minimum 100
        w.append(t)
        w.append(v)
        return w    
        
    def calibrate(self, list1, lagging_time, channel): 
            temp=[]
            for i in range(len(list1[1])):
                temp.append(list1[1][i])
            timestep=list1[0][100]-list1[0][99]
            pts=int(round(lagging_time/timestep))    
            
            print ' calibrate Ch %s,  timestep:%.1f ns , pts:%s' %(channel, timestep*1e9, pts) 
            if lagging_time>0:
                for i in range(pts,len(list1[0])-pts-1):            
                    list1[1][i] = temp[i-pts]
            elif lagging_time<0:
                for i in range(len(list1[0])-pts-1):
                    list1[1][i] = temp[1][i+pts]   
            return pts        
     
                      
    def DC2AC_measurement(self):  
        waveforms_list=[]
        self.par['section']=len(self.par['degree'])
     
        ''' collect data'''
        d=[]
        
        for it in range(self.par['section']):         
            self.par['phase']=self.par['degree'][it]  # lets say phase is the deg that we are in, 60Hz
            self.par['timedelay']=self.par['phase']/360/60
            
            #results, data_file, self.waveforms, mode =self.do_measure(it)
            results, data_file, self.waveforms, mode = self.get_waveforms(it)
            waveforms_list.append(self.waveforms)
      
            results.update({'Sec':it+1,'phase':self.par['phase'], 'NumPt':self.par['NumPt'], 'timeDiv':self.par['timeDiv'], 'calib':self.par['calib'], 'freq':results['freq']})    
            d.append(results)     
            self.waveforms.print_rms()
            self.waveforms.print_avg()
        df=pd.DataFrame(d)    
        df=df.set_index([range(len(df))])    #set index. Without this,  index numbers are all 'zero'    
 
        file_name = self.par['data_path']+'/%s_%sW_%sV_DC2AC.csv' % (self.par['data_file_name'], self.par['p_rated'], self.par['SAS_volt'])
        print "\n Data will be stored as %s\n" % file_name
        df.to_csv(file_name)    
          
        return waveforms_list
 
    def get_waveforms(self, it):
        para, equip= self.par, self.eq
        data_file=''        
        results=dict()
 
        SCOPE=equip['SCOPE']           
        #ch1 = w[0] ch2 = w[1], ch3 = w[2], ch4 = w[3], which is also a list of time and value
 
        w=[]        
        timedelay, degree, timeDiv, NumPt = para['timedelay'], int(para['phase']), para['timeDiv'], para['NumPt']
    
        print '\n---------------------------------------------------------------' 
        print '--- SEC %s, phase shift: %s degree (%.1f us)'  %(str(it+1), degree, para['timedelay']*1e6)       
        self.set_timebase_delay_factor(timedelay)    
        self.set_timebase_scale_factor(timeDiv)             
           
        time.sleep(1)
        self.set_stop()
    
        print ' - save data with %s pts' %str(NumPt)   
        for i in range(4):
            w.append(self.get_data(i+1))            
        SCOPE.write(':RUN')   
        
        if True: # if you want to save original waveforms    
            scope_data=[w[0][0],w[0][1],w[1][1],w[2][1],w[3][1]]                              
            df=pd.DataFrame({'Time':scope_data[0], para['ch_names'][0]:scope_data[1], para['ch_names'][1]:scope_data[2], para['ch_names'][2]:scope_data[3], para['ch_names'][3]:scope_data[4]})
            data_fp, data_file = unique_file(para['data_path']+'/%s.csv' %'scope_data')    
            df.to_csv(data_file)      
                      
        pts=[]
        calib=para['calib']
        if calib[0]=='ON':
            print '\n Calib. On'
            # channel 3 and 4 has 20ns delay
            for i in range(len(calib[1])):
                channel=calib[1][i][0]        
                pts.append(self.calibrate(w[channel-1], calib[1][i][1], channel))
        else: pts=0
                
        #clear up with wrong data due to time shift   
        if not(pts==0):                
            for m in range(4):
                for i in range(max(pts)*2):
                    w[m][0].pop(0)
                    w[m][1].pop(0)
                    w[m][0].pop(len(w[m])-1)
                    w[m][1].pop(len(w[m])-1)    
                    
#       #ch1 = w[0] ch2 = w[1], ch3 = w[2], ch4 = w[3], which is also a list of time and value
        waveforms=[w[0][0],w[0][1],w[1][1],w[2][1],w[3][1]]  
            
        d={'Time':waveforms[0], para['ch_names'][0]:waveforms[1], para['ch_names'][1]:waveforms[2], para['ch_names'][2]:waveforms[3], para['ch_names'][3]:waveforms[4]}
        df=pd.DataFrame(d)
        data_fp, data_file = unique_file(para['data_path']+'/%s.csv' % para['data_file_name'])    
        print "\n Data will be stored in %s" % data_file
        df.to_csv(data_file)
  
        mode=it+1
        file_name='data'
        waveforms=wf.waveforms(para, file_name=file_name) 
        if para['cycle']:
           VIrms, VIavg, freq= waveforms.conversion(mode=mode, data_file=data_file, cycle=para['cycle'])   
        else:VIrms, VIavg, freq= waveforms.conversion(mode=mode, data_file=data_file)               
  
        results.update(VIrms)
        results.update(VIavg)
        results.update({'freq':freq})
    
        return results, data_file, waveforms, mode    
   
     
    def reset(self):
        self.eq['SCOPE'].write('*RST')
    
    def set_probe_attenuation_factor(self, channel, attenuation):
        self.eq['SCOPE'].write(':CHAN%s:PROBE %s' % (channel, attenuation))    
    
    def set_auto_scale(self):
        print ' - autoscale' 
        self.eq['SCOPE'].write(':AUToscale')
 
    def set_probe(self, channel, impedance):       
        self.eq['SCOPE'].write(':CHAN%s:IMP %s' % (channel, impedance))
    #    
    def set_channel_UnitAmp(self, channel):
        self.eq['SCOPE'].write(':CHAN%s:UNIT AMP' % channel)
    #
    def set_timebase_scale_factor(self, timebase_scale):
        print ' - set time scale %s ms' %(timebase_scale*1000) 
        self.eq['SCOPE'].write(':TIM:SCAL %s' % timebase_scale)
    
    def set_trig(self, channel):
        #<source> ::= {CHANnel<n> | EXTernal | LINE | WGEN} for the DSO models
        if channel=='EXT':
            self.eq['SCOPE'].write(':TRIG:EDGE:SOUR EXT')
        else:
            self.eq['SCOPE'].write(':TRIG:EDGE:SOUR CHAN%s'  % channel)
       
    def display_channel(self, channel):
        self.eq['SCOPE'].write(':CHAN%s:DISP ON' % channel)
    #    
    def set_channel_Invert(self, channel):
        self.eq['SCOPE'].write(':CHAN%s:INV ON' % channel)       
    
    def set_stop(self):
        self.eq['SCOPE'].write(':STOP')
    #def set_run(self):
    #    self._write(':RUN')    
    #
    def set_offset_all(self, offset):
        self.eq['SCOPE'].write(':CHAN1:OFFS %s' % offset)
        self.eq['SCOPE'].write(':CHAN2:OFFS %s' % offset)
        self.eq['SCOPE'].write(':CHAN3:OFFS %s' % offset)
        self.eq['SCOPE'].write(':CHAN4:OFFS %s' % offset)


    def set_timebase_delay_factor(self, timebase_delay):
        self.eq['SCOPE'].write(':TIM:DEL %s' % timebase_delay)
        
    def wave(self, channel, num_of_points='MAX', filename=None):
        """Record one channel of data from oscilloscope."""
        #self.eq['SCOPE'].set_timeout(5 * 30)
        # self._write('WAV:FORMAT BYTE')
        # self._write('WAV:FORMAT WORD')
        # self._write('WAV:BYTEORDER MSBF')

        # self._write('WAV:UNSIGNED 1') # Return unsigned numbers
        self.eq['SCOPE'].write('WAV:FORMAT ASC')

        # It appears that the oscilloscope returns 1 less than requested, therefore bump up the request by 1.
        if type(num_of_points) == int:
            num_of_points += 1

        if channel == 'MATH':
            #print 'WAV:SOURCE MATH'
            self.eq['SCOPE'].write('WAV:SOURCE MATH')
        else:
            #print 'WAV:SOURCE CHANNEL%s' % channel
            self.eq['SCOPE'].write('WAV:SOURCE CHANNEL%s' % channel)
        self.eq['SCOPE'].write('WAV:POINTS %s' % num_of_points)

        data = self.eq['SCOPE'].ask('WAV:DATA?')
        ydata = data[10:]
        ydata = map(float, ydata.split(','))

        wave_preamble = self.eq['SCOPE'].ask('WAV:PRE?')
        preamble = [float(v) for v in wave_preamble.split(',')]

        format_type, ttype, points, count, xincrement, xorigin, xreference, yincrement, yorigin, yreference = preamble
        xdata = [(x - xreference) * xincrement + xorigin for x in range(int(points))]

        #self.restore_timeout()

        if filename:
            # fp, filename = unique_file(filename)
            filename = os.path.normpath(filename)
            fp = open(filename, 'w')
            # print filename
            for x, y in zip(xdata, ydata):
                fp.write('%e, %e\n' % (x, y))
            fp.close()
            return filename

        return xdata, ydata

