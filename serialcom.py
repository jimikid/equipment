# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 16:24:10 2016, @author: sbaek
    V00
    - initial release
    - '.serial' is a object 'rm.open_resource('ASRL5', timeout=12, baud_rate=115200)'
 
  V01 04/06/2016
    - run this script to close serial com when it was abnormaly terminated.
      if __name__ == '__main__':
        a=SerialCom()
        a.serial.close()  
"""

import visa
import time
from collections import OrderedDict
from threading import Thread, Lock
from Queue import Queue, Empty


class SerialCom:
    """
           __INIT__     
           __STR__
    """

    def __init__(self):
        self.return_str = ''
        self.item = OrderedDict()
        self.prompt_dict = {'b>': 'BOOT', 'd>': 'DEBUG', 'f>': 'FLASH_LOADER', 'x>': 'EMU_EMULATE'}

        rm = visa.ResourceManager()
        self.serial = rm.open_resource('ASRL5', timeout=12, baud_rate=115200)

    def __str__(self):
        self.return_str = ''
        return self.return_str

    def get_prompt(self, delay=0.2):
        while True:
            try:                    
                self.serial.write('\r')
                #print '.'
                data = self.serial.read()
                if 'd>' in data:
                    #print '\n'
                    #print data
                    break
                
                time.sleep(delay)
            except:pass

    def write(self, cmd, delay=0):
        '''
        :param cmd: str
        :param delay: int in second, hold after send a command
        :return: None
        '''
        self.get_prompt()
        #self.flush()
        for i in range(10):
            data = self.serial.read()
            if '>' in data:
                print '\nd> %s' % cmd
                self.serial.write(cmd)
                #print ('%s' % cmd)
                time.sleep(delay)  # PCU needs some time to respond.
                break

    def read(self, delay=0):
        #try:
            while True:
                data = self.serial.read()
                if ('>' not in data) and ('?' not in data) and (data is not '') and (data is not '\r \r'):
                    print '\nd> %s' % data
                    break

                #if (id+':' in data) :  #for register
                #    print '\nd> %s' % data
                #    break
            time.sleep(delay)  # PCU needs some time to respond.
        #except:
        #    pass

    def read_F(self, delay=0, id=id):
        '''
         - the dummy strs during boot up mess up reading register. add id.
        '''
        #try:
        while True:
            data = self.serial.read()
            if ('>' not in data) and ('?' not in data) and (data is not '') and (data is not '\r \r') and (id in data):
                print '\nd> %s' % data
                break
        time.sleep(delay)  # PCU needs some time to respond.
        #except:
        #    pass


    def read_reg(self, delay=2):
        try:
            while True:
                data = self.serial.read()                
                if ('>' not in data) and ('?' not in data) and (data is not '') and (data is not '\r \r'):
                    print '\n %s' % data
            time.sleep(delay)  # PCU needs some time to respond.
        except:
            pass


    def close(self):
        self.serial.close()



if __name__ == '__main__':

    '''
    a=SerialCom()
    #a.serial.close()  
    
    a.write(cmd='c f64c 1 1\r')
    time.sleep(1)
    a.write(cmd='s\r', delay=0)
    a.read_reg()
    '''
#
#    a.write(cmd='wl f636 60\r')
    a=SerialCom()
    a.write(cmd='rl f612 1\r')
    a.read()
#
#    lap=5
#
#    a.write(cmd='pt 2\r')
#
#    #time.sleep(lap)
#    a.write(cmd='p 90\r')
#
#    #time.sleep(lap)
#    a.write(cmd='p 30\r')
#
#    #time.sleep(lap)
#    a.write(cmd='p 70\r')
#    a.serial.close()
