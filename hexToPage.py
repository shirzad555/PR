# Receives a hex file and gives out a list of 256 bytes with address and checksome for each page (note that the last page might be less than 256bytes)
#OUTPUT:
# ADDRESS3, ADDRESS2, ADDRESS1, ADDRESS0, XOR(ADDRESSES), NUMBER of Byte (N), DAT (N+1), XOR(N and N+1 data bytes)
#.
#.
# Note: N+1 should always be a multiple of 4. 0 < N < 256 (N+1 max 256)

#import os


# **************************************************************************************************************
# **************************************************************************************************************
#def openFile(rootDir):
#	Open(rootDir, r)



#file = open('test.hex', 'r')



#***************************************************************************************************************************************
#This will read an intel hex file XXXXX and save the content into "data". data[18]
def importHexFile(rootDir):
	with open(rootDir) as f:
		data = f.readlines()
		f.close()
	return data

#***************************************************************************************************************************************
# This will return the MSB part of the start address of the memory (the LSB is part of each line in HEX file)
# Input is a list from the intel hex file
def getStartAddress (data):
	for col in data:
		recordType = col[7:9]
		if recordType == '04': # '04' (extended linear address record)
			start_address_msb = col[9: 9+int(col[1:3], 16)*2]
			return start_address_msb
	return 'ERROR'


#***************************************************************************************************************************************
START_ADDRESS_WITH_CHECKSUM_LINE = []	
DATA_WITH_CHECKSUM_LINE = []


def buildAddresAndDataLists (data):

	start_address_msb = getStartAddress (data)
	if start_address_msb == 'ERROR':
		return 'ERROR_MSB_START_ADDRESS'

	lineCounter = 0
	for col in data:
		recordType = col[7:9]
		if recordType  == '00': #HEX record type not '00' (data record)
			START_ADDRESS_WITH_CHECKSUM_LINE.append(start_address_msb + col[3:7])
			dataWithChecksum = addChecksum(START_ADDRESS_WITH_CHECKSUM_LINE[lineCounter], False)
			START_ADDRESS_WITH_CHECKSUM_LINE[lineCounter] = dataWithChecksum 
			
			#print addChecksum(START_ADDRESS_WITH_CHECKSUM_LINE[lineCounter]) 
			#print START_ADDRESS_WITH_CHECKSUM_LINE[lineCounter]
			
			numBytes = int(col[1:3], 16)
			DATA_WITH_CHECKSUM_LINE.append(col[9: 9+(numBytes*2)])
			dataWithChecksum = addChecksum(DATA_WITH_CHECKSUM_LINE[lineCounter], True)
			DATA_WITH_CHECKSUM_LINE[lineCounter] = dataWithChecksum 

			lineCounter += 1

	return len(START_ADDRESS_WITH_CHECKSUM_LINE)


#****************************************************************************************************************
# Calculates the checksum of the input and add it to the input (this should be ready to be written to flash)	
def addChecksum (dataList, isDataByte):
	i = 0
	temp = []
	while i<len(dataList):
		temp.append(dataList[i:i+2])
		i += 2	

	result = '00'
	for eachByte in temp:
		result = int(eachByte, 16) ^ int(result, 16)
		result = '{:x}'.format(result)

	
	
	if isDataByte == True:  			# adding the number of bytes to the checksum	
		#print dataList	
		temp2 = len(dataList)/2 -1
		#print temp2
		result = temp2 ^ int(result, 16)
		result = '{:x}'.format(result)
		temp.insert(0, '{:x}'.format(temp2))
		
		#print '{:x}'.format(temp2)

	temp.append(result)
	

	i = 0
	for item in temp:
		if len(item) == 1:
			item = '0' + item

		temp[i] = item.decode('hex')
		i += 1

	return temp
	

if __name__ == '__main__':

	print 'testing ...'
	rootDir = 'C:\Users\Shirzad_shahriari\Documents\Shirzad\\2.0\NewSmartCable\Pressure\PSC1\FW\X1_V1\STM32F427_437xx\\STM32F427_437xx.hex' 

	#data = importHexFile(rootDir)
	
	buildAddresAndDataLists (importHexFile(rootDir))

	#for item in START_ADDRESS_WITH_CHECKSUM_LINE[0]:
	#	print item

	print START_ADDRESS_WITH_CHECKSUM_LINE[121]
	print DATA_WITH_CHECKSUM_LINE[121]

	for item in DATA_WITH_CHECKSUM_LINE[121]:
		print item 
