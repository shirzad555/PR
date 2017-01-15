import serial
from datetime import timedelta, datetime
import sys
import time
import matplotlib.ticker as ticker
import os
import tkFileDialog
import glob
import os.path

# *********************************************************************************

SERIAL_TIMEOUT_MS       =       500
VERSION_NUM             =       "Tactile_Gripper_2.0.0"

# *********************************************************************************
# *********************************************************************************
def setupSerialPort (portNumber):
	if sys.platform.startswith('win'):
		port = 'COM' + str(portNumber) 	#port = "COM83" # 
	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		port = "/dev/ttyUSB0"
	print 'Selected Port = ' + port
	return serial.Serial(port, baudrate=115200, bytesize=8, stopbits=1, timeout=0.4) #timeout=0.4

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
# **********************************************************************************


if __name__ == "__main__":
#	print "Make sure PR.hex file is savesd in C:\\test folder (if there is no test folder, please create it and #copy the hex file in there)"
	
	import time
	import sys

        print ('Perception Robotics Data Logger, Ver: ' + VERSION_NUM)

        #serilaPortList = list(serial.tools.list_ports.comports())
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
            sourceFile = tkFileDialog.asksaveasfilename(initialdir=savedFileName)
        else :
            sourceFile = tkFileDialog.asksaveasfilename()

        print (sourceFile)

        openedFile = open(sourceFile , 'w+') #open('Retraction')

	if sys.platform.startswith('win'):
        	savedFileLocationDirectory = open('C:\\Users\\Public\\PR_FileRecord.txt' , 'w+')
		savedFileLocationDirectory.write(sourceFile)
	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		savedFileLocationDirectory = open('PR_FileRecord.txt' , 'w+')
        	savedFileLocationDirectory.write(os.path.dirname(sourceFile))
        savedFileLocationDirectory.close()

	ser.write('r')
	time.sleep(1) # delays for 1 second, give micro enough time to init

	ser.flushInput()
	ser.flushOutput()
	#while 1:
	ser.write('s')
	#data_raw = ser.read(2)

	counter = 0
	channel = 1;

	ser.flushInput()
	ser.flushOutput()

        openedFile.write("F1_CH1_LPF ,F1_CH2_LPF ,F1_CH3_LPF ,F1_CH4_LPF ,F1_CH5_LPF ,F2_CH1_LPF ,F2_CH2_LPF ,F2_CH3_LPF ,F2_CH4_LPF ,F2_CH5_LPF ,F1_CH1_HPF ,F1_CH2_HPF ,F1_CH3_HPF ,F1_CH4_HPF ,F1_CH5_HPF ,F2_CH1_HPF ,F2_CH2_HPF ,F2_CH3_HPF ,F2_CH4_HPF ,F2_CH5_HPF , ")
        openedFile.write('\n')
        
	while 1:
		data_raw = ser.read(2)
		
		#print data_raw.encode('hex')

		if data_raw.encode('hex') == 'abcd':
			data_raw2 = ser.read(400) # taking 2 reading of 16bit every 2ms and sending data out every 200ms => (200ms/2ms)*2readings*2bytePerReading = 400
			i = 0
                        k = 0
                        l = [0,4,2,6] # 0: F1_LPF, 4: F2_LPF, 2: F1_HPF, 6: F2_HPF
			while i < (len(data_raw2) -40):
                            while k<4: # save them in order of finger1_lpf_electrodeX then finger2_lpf_electrodeX then finger1_hpf_electrodeX and finally finger2_hpf_electrodeX
##                                 f.write(str((ord(data_raw2[i+1+j])*256+ord(data_raw2[i+j])))) # *250*324/65535, ord to change character to int
##                                 f.write(', ')
                                j=l[k]                                
                                openedFile.write(str((ord(data_raw2[i+j+1])*256+ord(data_raw2[i+j+0])))) # Electrode1
                                openedFile.write(', ') 
                                openedFile.write(str((ord(data_raw2[i+j+9])*256+ord(data_raw2[i+j+8])))) # Electrode2
                                openedFile.write(', ')
                                openedFile.write(str((ord(data_raw2[i+j+17])*256+ord(data_raw2[i+j+16])))) # Electrode3
                                openedFile.write(', ')
                                openedFile.write(str((ord(data_raw2[i+j+25])*256+ord(data_raw2[i+j+24])))) # Electrode4
                                openedFile.write(', ')
                                openedFile.write(str((ord(data_raw2[i+j+33])*256+ord(data_raw2[i+j+32])))) # Electrode5
                                openedFile.write(', ')                                                                
                                k+=1

                            i += 40 # 20 readings in each small loop * 2 since it's 2 bytes each time
                            k = 0 
                            openedFile.write('\n')

			sys.stdout.write('\r')
                        
			print ' ' + str(counter) + ' ', # + '\n'
			print 'LPF_F1_CH1=' + str((ord(data_raw2[1])*256+ord(data_raw2[0]))), #0
                        print 'HPF_F1_CH1=' + str((ord(data_raw2[3])*256+ord(data_raw2[2]))), #5
			print 'LPF_F2_CH1=' + str((ord(data_raw2[5])*256+ord(data_raw2[4]))), #1
                        print 'HPF_F2_CH1=' + str((ord(data_raw2[7])*256+ord(data_raw2[6]))), #6
			print 'LPF_F1_CH2=' + str((ord(data_raw2[9])*256+ord(data_raw2[8]))), #2
                        print 'HPF_F1_CH2=' + str((ord(data_raw2[11])*256+ord(data_raw2[10]))), #7 
			print 'LPF_F2_CH2=' + str((ord(data_raw2[13])*256+ord(data_raw2[12]))), #3
                        print 'HPF_F2_CH2=' + str((ord(data_raw2[15])*256+ord(data_raw2[14]))), #6
			print 'LPF_F1_CH3=' + str((ord(data_raw2[17])*256+ord(data_raw2[16]))), #4
                        print 'HPF_F1_CH3=' + str((ord(data_raw2[19])*256+ord(data_raw2[18]))), #7
			print 'LPF_F2_CH3=' + str((ord(data_raw2[21])*256+ord(data_raw2[20]))), #0
                        print 'HPF_F2_CH3=' + str((ord(data_raw2[23])*256+ord(data_raw2[22]))), #5
			
			print 'LPF_F1_CH4=' + str((ord(data_raw2[25])*256+ord(data_raw2[24]))), #0
                        print 'HPF_F1_CH4=' + str((ord(data_raw2[27])*256+ord(data_raw2[26]))), #5
			print 'LPF_F2_CH4=' + str((ord(data_raw2[29])*256+ord(data_raw2[28]))), #1
                        print 'HPF_F2_CH4=' + str((ord(data_raw2[31])*256+ord(data_raw2[30]))), #6
			print 'LPF_F1_CH5=' + str((ord(data_raw2[33])*256+ord(data_raw2[32]))), #2
                        print 'HPF_F1_CH5=' + str((ord(data_raw2[35])*256+ord(data_raw2[34]))), #7 
			print 'LPF_F2_CH5=' + str((ord(data_raw2[37])*256+ord(data_raw2[36]))), #3
                        print 'HPF_F2_CH5=' + str((ord(data_raw2[39])*256+ord(data_raw2[38]))), #6
## 			print 'LPF_F1_CH6=' + str((ord(data_raw2[41])*256+ord(data_raw2[40]))), #4
##                         print 'HPF_F1_CH6=' + str((ord(data_raw2[43])*256+ord(data_raw2[42]))), #7
## 			print 'LPF_F2_CH6=' + str((ord(data_raw2[45])*256+ord(data_raw2[44]))), #0
##                         print 'HPF_F2_CH6=' + str((ord(data_raw2[47])*256+ord(data_raw2[26]))), #5
                        
## 			print 'C1=' + str((ord(data_raw2[5])*256+ord(data_raw2[4]))*250*324/65535), #0
## 			print 'C2=' + str((ord(data_raw2[1])*256+ord(data_raw2[0]))*250*324/65535), #1
## 			print 'C3=' + str((ord(data_raw2[7])*256+ord(data_raw2[6]))*250*324/65535), #2
## 			print 'C4=' + str((ord(data_raw2[11])*256+ord(data_raw2[10]))*250*324/65535), #3
## 			print 'C5=' + str((ord(data_raw2[15])*256+ord(data_raw2[14]))*250*324/65535), #4
## 			print 'C6=' + str((ord(data_raw2[19])*256+ord(data_raw2[18]))*250*324/65535), #5
## 			print 'C7=' + str((ord(data_raw2[23])*256+ord(data_raw2[22]))*250*324/65535), #6
## 			print 'C8=' + str((ord(data_raw2[27])*256+ord(data_raw2[26]))*250*324/65535), #7
			#print 'C9=' + str((ord(data_raw2[31])*256+ord(data_raw2[30]))*250*324/65535), #8
			#print 'C10=' + str((ord(data_raw2[35])*256+ord(data_raw2[34]))*250*324/65535), #9
			#print 'C11=' + str((ord(data_raw2[39])*256+ord(data_raw2[38]))*250*324/65535), #10
			#print 'C12=' + str((ord(data_raw2[43])*256+ord(data_raw2[42]))*250*324/65535), #11
			#print 'C12=' + str((ord(data_raw2[47])*256+ord(data_raw2[46]))*250*324/65535), 
			#print 'C14=' + str((ord(data_raw2[51])*256+ord(data_raw2[50]))*250*324/65535),
			#print 'C15=' + str((ord(data_raw2[55])*256+ord(data_raw2[54]))*250*324/65535),
			#print 'C16=' + str((ord(data_raw2[59])*256+ord(data_raw2[58]))*250*324/65535),
			#print data_raw2[5].encode('hex') + data_raw2[4].encode('hex'),
			counter += 1
			
		ser.flushInput()


####################################### VERSION HISTORY ######################################
'''
    V2.0.0 :
        - Added Linux compatibilties
    V1.0.0 :
        - Initial script        
'''
