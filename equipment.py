
"""
Created on 02/24/2016  @author: sbaek
    V00
    - initial release
"""

import visa
from collections import OrderedDict 

class equip:
    """
           __INIT__     
           __STR__      
   
    """    
    
    def __init__(self):              
        self.return_str= '' 
        self.item=OrderedDict()
        
    def __str__(self):
        self.return_str= ''
        return self.return_str      
    
    def get_equip(self):
        rm = visa.ResourceManager()
        list_equip=rm.list_resources()
 
        
        for item in list_equip: 
            print item
            if 'GPIB' in item:   #check equipment by gpib                                
                eq=rm.open_resource(item)
                eq.write('*IDN?')   
                c=eq.read()
                if 'E4360A' in c:
                    cata='SAS'
                    print item+' ->  set '+cata
                    self.item.update({cata:eq})
                    self.item[cata].write('*IDN?')   
                    print self.item[cata].read()   
                
                if 'DSO-X' in c:
                    cata='SCOPE'
                    print item+' ->  set '+cata
                    self.item.update({cata:eq})
                    self.item[cata].write('*IDN?')   
                    print self.item[cata].read()   

                
                if 'YOKOGAWA' in c:
                    cata='POWER_METER'
                    print item+' ->  set '+cata
                    self.item.update({cata:eq})
                    self.item[cata].write('*IDN?')   
                    print self.item[cata].read()   

                        
                if '34401A' in c:
                    cata='DVM'
                    print item+' ->  set '+cata
                    self.item.update({cata:eq})
                    self.item[cata].write('*IDN?')   
                    print self.item[cata].read()   

        
                if 'UPC-32E' in c:
                    cata='AC_SOURCE'
                    print item+' ->  set '+cata
                    self.item.update({cata:eq})
                    self.item[cata].write('*IDN?')   
                    print self.item[cata].read()   
                    
                if 'ASRL5' in c:
                    cata='serial_com'
                    print item+' ->  set '+cata
                    self.item.update({cata:eq})
                    self.item[cata].write('*IDN?')   
                    print self.item[cata].read() 
                    
           
        return self.item
                
               
               
               
