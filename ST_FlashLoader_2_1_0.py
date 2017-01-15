import serial
from datetime import timedelta, datetime
import hexToPage
import sys
import time

import matplotlib.ticker as ticker
import os
import tkFileDialog
import glob
import os.path

chip_ACK  = '\x79'
chip_NACK = '\x1F'

# *********************************************************************************

VERSION_NUM             =       "2.1.0"

# *********************************************************************************
def setupSerialPort (portNumber):
	if sys.platform.startswith('win'):
		port = 'COM' + str(portNumber) 	#port = "COM83" # 
	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		port = "/dev/ttyUSB0"
	print 'Selected Port = ' + port
	return serial.Serial(port, baudrate=115200, bytesize=8, parity='E', stopbits=1, timeout=1) #timeout=0.4

# **********************************************************************************

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
# **********************************************************************************

# *********************************************************************************
# see if the micro is in boot mode (send 0x7F and expect 0x79 back)
# *********************************************************************************
def chipInBootMode(serPort):
	serPort.flushInput()
	i=0
	while i < 5: 
		serPort.write("\x7F")
		if serPort.read(1) == chip_ACK:
			return "Chip is in Boot Mode Now"
		i +=1
	return "Failed to put Chip in Boot Mode!!!"		
	
# *********************************************************************************
# To get the Chip's ID
# *********************************************************************************
def getChipId():
	ser.flushInput()
	i=0
	while i < 5: 
		ser.write("\x02" + "\xFD")
		data = ser.read(1)
		if data == chip_ACK:
			data = readPort(1)
			if data[-1] != chip_ACK:
				return False  
			return data[0:-1]
		i +=1
	return False	


# *********************************************************************************
# To erase the number of pages of flash memory	
# *********************************************************************************
def Pageerase(numPages):
	ser.flushInput()
	i=0
	while i < 5: 
		ser.write("\x43" + "\xBC")
		data = ser.read(1)
		if data == chip_ACK:
			if numPages == 255:
				ser.write("\xFF" + "\x00")
				data = readPort(1)
				if data[-1] != chip_ACK:
					return True
				return False
		i +=1
	return False
	

# *********************************************************************************
# To mass erase the chip's memory
#	- Global mass erase	GLOBAL_ME
#	- Bank 1 mass erase	BANK1_ME
#	- Bank 2 mass erase	BANK2_ME	
# *********************************************************************************
def massErase(massEraseType, serPort):
	serPort.flushInput()
	print "Erasing memory ..."
	i=0
	while i < 5:
		serPort.write("\x44" + "\xBB")
		data = serPort.read(1)
		if data == chip_ACK:
			serPort.write("\xFF" + "\xFF")	#this is the checksum
			serPort.write("\x00")	#this is the checksum
			serialtimeout = serPort.timeout
			serPort.timeout = 30
			data = serPort.read(1)
			serPort.timeout = serialtimeout
			if data == chip_ACK:
				return 'Erase successful'
			return 'Erase Failed!!!!'
		i +=1
	return 'Erase Failed!!!!'



# *********************************************************************************
# To write to memory
#	INPUT: root to the hex file directory
#	OUTPUT: SUCCESS or ERROR	
# *********************************************************************************
def writeMemory(rootDir, serPort):
	serPort.flushInput()

	#rootDir = 'PR.hex'

	hexToPage.buildAddresAndDataLists (hexToPage.importHexFile(rootDir))

	i=0
	j=0
	while i<len(hexToPage.START_ADDRESS_WITH_CHECKSUM_LINE):
		
		while j<5:
			serPort.write("\x31" + "\xCE")
			data = serPort.read(1)
			if data == chip_ACK:
				break
			j += 1
			if j == 6:
				return "ERROR ENTRING WRITE MODE (TIMEOUT)"
				
		serPort.write(hexToPage.START_ADDRESS_WITH_CHECKSUM_LINE[i])

		data = serPort.read(1)
		if data != chip_ACK:
			return "ERROR SENDING WRITE ADDRESS"


		serPort.write(hexToPage.DATA_WITH_CHECKSUM_LINE[i])
		
		#serialtimeout = ser.timeout
		#ser.timeout = 5
		data = serPort.read(1)
		#ser.timeout = serialtimeout
		if data != chip_ACK:
			print "Failes at packet #", i
			return "ERROR WRITING DATA TO MEMORY"
		
		i += 1
		sys.stdout.write('\r')
		print 'Writing ',
		print '%.2f'  % (float(float(i)/len(hexToPage.START_ADDRESS_WITH_CHECKSUM_LINE))*100),
		print "%",

	return "\nSUCCESS"
	
# *********************************************************************************
# Read Port
# *********************************************************************************
def readPort(timeOut_sec):
	#endtime = datetime.utcnow() + timedelta(seconds = timeOut_sec)
	serialtimeout = ser.timeout
	ser.timeout = timeOut_sec
	data = ser.read(1)
	received  = []
	while data != '':
		received.append(data)
		data = ser.read(1)
	if received == []:
		received.append('Empty')
	ser.timeout = serialtimeout
	return received


if __name__ == "__main__":
	#print "********** Make sure PR.hex file is in the same folder as this script ************"
	#print "********** hex file must be called PR                                 ************"
	
	import hexToPage

	print ('Perception Robotics ST Flash Loader, Ver: ' + VERSION_NUM)

	print ('*********************************************************************')
	print ('Select your port from the list below and type the port number only')
	print serial_ports()
	print ('*********************************************************************')
	print ('eg for Linux if you see ''/dev/ttyUSB0'' write 0)')
	print ('eg for Windows if you see ''Com1'' write 1)')
	print ('*********************************************************************')
        print ('Press CTRL + c to stop')
        
	comPort = raw_input('Enter the USB port number: ')

	ser = setupSerialPort (comPort)

	if sys.platform.startswith('win'):
        	savedFileLocationDirectory = open('C:\\Users\\Public\\PR_FileRecord.txt' , 'a+')
	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		savedFileLocationDirectory = open('PR_FileRecord.txt' , 'a+')
        savedFileName = savedFileLocationDirectory.read()
        savedFileLocationDirectory.close()

	print (savedFileName)

        if len(savedFileName) > 0:
            sourceFile = tkFileDialog.askopenfilename(initialdir=savedFileName)
        else :
            sourceFile = tkFileDialog.askopenfilename()

        print (sourceFile)

        #openedFile = open(sourceFile , 'w+') #open('Retraction')

	if sys.platform.startswith('win'):
        	savedFileLocationDirectory = open('C:\\Users\\Public\\PR_FileRecord.txt' , 'w+')
		savedFileLocationDirectory.write(sourceFile)
	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		savedFileLocationDirectory = open('PR_FileRecord.txt' , 'w+')
		savedFileLocationDirectory.write(sourceFile)
        	#savedFileLocationDirectory.write(os.path.dirname(sourceFile))
        savedFileLocationDirectory.close()


	ser.setDTR(False) # BOOT0 to Low
	time.sleep(.300)
	ser.setRTS(True) # RESET to Low
	time.sleep(.300)
	ser.setRTS(False)  # RESET to High
	time.sleep(.300)		
	ser.setDTR(True) # Boot0 to High

	bootMode = chipInBootMode(ser)
	print bootMode
	if bootMode == "Chip is in Boot Mode Now":
		print massErase('', ser)
		#print writeMemory('', ser) 
		print writeMemory(sourceFile, ser)


####################################### VERSION HISTORY ######################################
'''
    V2.1.0 :
        - Removed the default root directory and default hex file (PR.hex)
    V2.0.0 :
        - Added Linux compatibilties 
	- Added pup op window feature 
        
'''
