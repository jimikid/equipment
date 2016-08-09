"""
Created on 26/01/2015

@author: tbeswick
Betsy copied to pcu_bench\tools August 2015
Modified to run from command line with a directory name


  V01 08/09/2016
  - modify the script for script automation

"""
import sys
import serial
import time
import logging
#from tools_parser import parse_command_line, code_parser


class PCUProgrammer(object):
    def __init__(self):
        self.conn = None # the serial connection to the PCU
        self.log = logging.getLogger('PCUProgrammer')

    def connect(self, comport='COM2'):
        """
        Connects to the PCU on the given comport.
        """
        if self.conn:
            self.disconnect()
        comport = 'COM%i' % comport   # serial needs the COM# format
        self.conn = serial.Serial(port=comport, baudrate=115200, bytesize=8, parity='N',
                             stopbits=1, timeout=None, xonxoff=0, rtscts=0)
        return self.conn
    
    def disconnect(self):
        """
        Disconnects the PCU serial connection.
        """
        self.conn.close()

    def enter_flasher_mode(self):
        """
        Puts the pcu into flasher mode.  May require the user to cycle the
        power depending on what state the pcu is currently in.
        """
        self.log.debug("Entering flasher mode")
        # Unit could be booting
        try:
            found = self.wait_for(['...'], timeout_secs=2)
        except serial.SerialTimeoutException:
            pass
        else:
            self.log.debug("Sending 'f'")
            self.conn.write('f')
        self.conn.write('\r')
        while 1:
            try:
                found = self.wait_for(['f>', 'd>', '...'])
            except serial.SerialTimeoutException:
                self.ask_user("Please cycle the power.")
            else:
                if found == 'f>':
                    self.log.info("Have entered flasher mode")
                    return
                elif found == 'd>':
                    self.log.debug("Sending 'boot'")
                    self.conn.write("boot\r")
                    time.sleep(2)
                elif found == '...':
                    self.conn.write('f')
                else:
                    assert False, "unexpected result from wait_for"
 
    def enter_bootloader_mode(self):
        """
        Puts the pcu into bootloader mode ('b>' prompt).  May require the user to cycle the
        power depending on what state the pcu is currently in.
        """
        self.log.debug("Entering bootloader mode")
        
        self.conn.write('\r')
        while 1:
            try:
                found = self.wait_for(['f>', 'd>', '...', 'b>'])
            except serial.SerialTimeoutException:
                self.ask_user("Please cycle the power.")
            else:
                if found == 'b>':
                    self.log.info("Have entered bootloader mode")
                    return
                elif found == 'd>':
                    self.log.debug("Sending 'boot'")
                    self.conn.write("boot\r")
                    time.sleep(2)
                elif found == '...':
                    self.conn.write('\r')
                elif found == 'f>':
                    self.conn.write('boot\r')
                else:
                    assert False, "unexpected result from wait_for"
        
    def ask_user(self, message):
        print(message)
                
    def wait_for(self, strings, timeout_secs=5):
        """
        Waits for a string to be received via serial.  Will only return once
        one of the strings in strings is received.
        :raises serial.SerialTimeoutException
        :returns: the string found first
        """
        self.log.debug("waiting for: {}".format(strings))
        read_buffer = ""
        timeout_time = time.time() + timeout_secs
        while time.time() < timeout_time:
            read_buffer += self.conn.read(self.conn.inWaiting())
            for string in strings:
                if string in read_buffer:
                    self.log.debug("Found '{0}'".format(string))
                    return string
            time.sleep(0.01) # short sleep to keep CPU usage down
        self.log.debug("read_buffer: '{0}'".format(read_buffer))
        raise serial.SerialTimeoutException("{0} not found within {1} secs."
                                            .format(strings, timeout_secs))
        
    def erase_procload_and_parm(self):
        """
        Erases the procload and parameter tables, by sending the following:
          * eci0
          * eci1
          * ecm0
          * ecm1
          * epi0
          * epi1
          * epm0
          * epm1
        """
        for area in ('c', 'p'):
            for type_ in ('i', 'm'):
                for bank in ('0', '1'):
                    self.send_command("e{0}{1}{2}".format(area, type_, bank))
                    
    def erase_manufactuing_data(self):
        """
        Erases the manufacturing tables (i.e. calibration) from the pcu,
        by sending the following:
          * emi0
          * emi1
          * emm0
          * emm1
        """
        for command in ['emi0', 'emi1', 'emm0', 'emm1']:
            self.send_command(command)
        
    def send_command(self, command, prompt='f>', timeout_secs=5):
        """
        Sends a command (with line end) to the flasher, and waits for a prompt 
        back.
        """
        self.log.debug("sending: {0}".format(command))
        self.conn.write("{0}\r".format(command))
        self.wait_for([prompt], timeout_secs)
        
    def program_file(self, command, filepath, timeout_secs=600):
        """
        Sends a file to the pcu after sending a program command.
        """
        assert command.startswith('p')
        self.send_command(command, prompt='p>')
        self.send_file(filepath)
        self.wait_for(['f>'], timeout_secs=10)
    
    def send_file(self, filepath, timeout_secs=600):
        """
        Sends a file over serial
        """
        with open(filepath, 'rb') as pfile:
            self.log.debug("sending: '{0}'".format(filepath))
            timeout_time = time.time() + timeout_secs
            for line in pfile:
                # strip out whatever line endings we have and replace with '/r'
                line = line.rstrip()
                line += '\r'
                # clear the read buffer
                # TODO: actually check the response from the PCU to verify data
                self.conn.read(self.conn.inWaiting())
                self.conn.write(line)
                if time.time() >  timeout_time:
                    raise RuntimeError("Timed out while programming '{0}'"
                               .format(filepath))
            self.log.debug("file sent")
    
import os
if __name__ == '__main__':
    """ To load code into Heron board.
        Board needs to be booted, serial cable attached, uses COM2.
        Copy procload & parameter table files to a directory on local drive, and pass the 
        directiry name on command line.
        Example: pcu_bench\tools> code_update_heron.py c:\procload
        """
    options = parse_command_line(parser_func=code_parser)
    logging.basicConfig(level=logging.DEBUG)
   
    dir = options.code_dir
    
    files = os.listdir(dir)
    if len(files) != 4:
        print "Unable to program device - the directory: %s does not contain exactly 4 files" % dir
        sys.exit()
    found = 0
    
    pl_file = None 
    pl_meta = None 
    pt_file = None 
    pt_meta = None 
    
    for name in files:
        print (name)
        if name.find("parm") != -1:
            if name.find("meta") == -1:
                pt_file = "%s/%s" %  (dir, name)
                found += 1
            else:
                pt_meta = "%s/%s" %  (dir, name)
                found += 1
        if name.find("procload-") != -1:
            print name
            if name.find("meta") == -1:
                pl_file = "%s/%s" %  (dir, name)
                found += 1
            else:
                pl_meta = "%s/%s" %  (dir, name)
                found += 1
    if found != 4:
        print "\tDid not find the correct files in %s" % dir
        if pl_file is None:
            print "\t\tMissing procload code file"
        if pl_meta is None:
            print "\t\tMissing procload meta file"
        if pt_file is None:
            print "\t\tMissing parameter table file"
        if pt_meta is None:
            print "\t\tMissing parameter table meta file"
        print pl_file, pl_meta, pt_file, pt_meta
        sys.exit()
        
    x = PCUProgrammer()
    x.connect(options.serial_port)
    x.enter_flasher_mode()
    x.erase_procload_and_parm()
    
    
        
    print pl_file
    print pl_meta
    print pt_file
    print pt_meta
    
    for bank in (0,1):
        x.program_file('pci%i'% bank,pl_file)
        x.program_file('pcm%i'% bank, pl_meta)
        x.program_file('ppi%i' % bank, pt_file)
        x.program_file('ppm%i'% bank, pt_meta)
