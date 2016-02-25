# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 16:24:10 2016, @author: sbaek
    V00
    - initial release
    - '.serial' is a object 'rm.open_resource('ASRL5', timeout=12, baud_rate=115200)'
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
            self.serial.write('\r')
            data = self.serial.read()
            if '>' in data:
                #print '\n'
                #print data
                break
            time.sleep(delay)

    def write(self, cmd, delay=4):
        print '\nd> %s' % cmd
        self.get_prompt()
        for i in range(10):
            data = self.serial.read()
            if '>' in data:
                self.serial.write(cmd)
                #print ('%s' % cmd)
                time.sleep(delay)  # PCU needs some time to respond.
                break

    def read(self):
        try:
            while True:
                data = self.serial.read()
                if ('>' not in data) and ('?' not in data) and (data is not '') and (data is not '\r \r'):
                    print '\nd> %s' % data
        except:
            pass



if __name__ == '__main__':

    a=SerialCom()
    a.write(cmd='rl f636 1\r')
    a.read()

    a.write(cmd='wl f636 60\r')
    a.write(cmd='rl f636 1\r')
    a.read()

    lap=5

    a.write(cmd='pt 2\r')

    #time.sleep(lap)
    a.write(cmd='p 90\r')

    #time.sleep(lap)
    a.write(cmd='p 30\r')

    #time.sleep(lap)
    a.write(cmd='p 70\r')
    a.serial.close()
